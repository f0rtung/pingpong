import asyncio
import functools
import logging

import aiohttp
from aiomisc.log import LogFormat, basic_config
from fastapi import FastAPI, Response, BackgroundTasks
from uvicorn import Config, Server

from ping_model import PingModel, is_valid_ping
from ping_transformer import make_ping_transformer, PingTransformerFn
from settings import Settings

settings = Settings()
basic_config(settings.log_level, LogFormat.stream, buffered=False)
logger = logging.getLogger(__name__)


async def send_ping(s: aiohttp.ClientSession, ping: PingModel) -> None:
    ping_json = ping.dict()
    logger.debug(f'Send request with ping {ping_json}')
    async with s.post(settings.ping_url, json=ping_json) as response:
        logger.info(f'Response status {response.status}')


async def ping_handler(
        s: aiohttp.ClientSession,
        ping_transformer_fn: PingTransformerFn,
        ping: PingModel,
        response: Response,
        background_tasks: BackgroundTasks):
    logger.info(f'Receive ping request {ping.json()}')
    if is_valid_ping(ping):
        logger.error('Invalid ping request')
        response.status_code = 400
    else:
        logger.info('Add send_ping background_tasks')
        background_tasks.add_task(send_ping, s, ping_transformer_fn(ping))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)

    async def on_stop_server():
        await session.close()
        logger.info('Stop server')

    app = FastAPI()
    app.on_event("shutdown")(on_stop_server)

    ping_transformer = make_ping_transformer(settings.mode)
    ping_handler_fn = functools.partial(ping_handler, session, ping_transformer)
    app.post("/ping")(ping_handler_fn)

    logger.info(f'Run server with settings {settings.json()}')
    config = Config(host=settings.host, port=settings.port, app=app, loop=loop)
    server = Server(config)
    loop.run_until_complete(server.serve())

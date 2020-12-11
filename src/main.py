import asyncio
import functools
import logging

import aiohttp
from aiomisc.log import LogFormat, basic_config
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from uvicorn import Config, Server

from ping_model import PingModelIn, is_invalid_ping
from ping_transformer import make_ping_transformer, PingTransformerFn
from settings import Settings

settings = Settings()
basic_config(settings.log_level, LogFormat.stream, buffered=False)
logger = logging.getLogger(__name__)


async def send_ping(s: aiohttp.ClientSession, ping: PingModelIn) -> None:
    ping_json = ping.dict()
    logger.debug(f'Send request with ping {ping_json}')
    try:
        async with s.post(settings.ping_url, json=ping_json) as response:
            logger.info(f'Response status {response.status}')
    except Exception as ex:
        logger.error(f'Can not make request, error: {ex}')


async def ping_handler(
        s: aiohttp.ClientSession,
        ping_transformer_fn: PingTransformerFn,
        ping: PingModelIn,
        background_tasks: BackgroundTasks):
    logger.info(f'Receive ping request {ping.json()}')
    if is_invalid_ping(ping):
        logger.error('Invalid ping request')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid ping request')
    logger.info('Add send_ping background task')
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
    app.post("/ping", responses={400: {'description': 'Invalid request'}})(ping_handler_fn)

    logger.info(f'Run server with settings {settings.json()}')
    config = Config(host=settings.host, port=settings.port, app=app, loop=loop)
    server = Server(config)
    loop.run_until_complete(server.serve())

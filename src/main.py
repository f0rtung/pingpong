import logging
import random
import typing

import aiohttp
import uvicorn
from aiomisc.log import LogFormat, basic_config
from fastapi import FastAPI, Response, BackgroundTasks

from ping_model import PingModel
from settings import Settings, AppMode

settings = Settings()
basic_config(settings.log_level, LogFormat.stream, buffered=False)
logger = logging.getLogger(__name__)

# session = aiohttp.ClientSession()
app = FastAPI()


# @app.on_event("shutdown")
# async def shutdown_event():
#     await session.close()
#     logger.info('Stop server')


PingTransformer = typing.Callable[[PingModel], None]


def make_ping_transformer(app_mode: AppMode) -> PingTransformer:
    if app_mode == AppMode.digits:
        def digits_action(ping: PingModel) -> None:
            ping.digits.append(random.randint(0, 100))
        return digits_action
    elif app_mode == AppMode.avg_max_min:
        def avg_max_min_action(ping: PingModel) -> None:
            if ping.digits:
                d = ping.digits
                ping.avg = sum(d) / len(d)
                ping.min = min(d)
                ping.max = max(d)
        return avg_max_min_action
    raise RuntimeError(f'invalid app mode {app_mode.name}')


ping_transformer: PingTransformer = make_ping_transformer(settings.mode)


async def send_ping(ping: PingModel) -> None:
    ping_transformer(ping)
    ping_json = ping.dict()
    logger.debug(f'Send request with ping {ping_json}')
    async with aiohttp.ClientSession() as session:
        async with session.post(settings.ping_url, json=ping.dict()) as response:
            logger.info(f'Response status {response.status}')


def is_invalid_request() -> bool:
    return random.randint(0, 10) % 3 == 0


@app.post("/ping")
async def ping_handler(ping: PingModel, response: Response, background_tasks: BackgroundTasks):
    logger.info(f'Receive ping request {ping.json()}')
    if is_invalid_request():
        logger.error('Invalid request')
        response.status_code = 400
    else:
        logger.info('Add background_tasks')
        background_tasks.add_task(send_ping, ping)


if __name__ == "__main__":
    logger.info(f'Run server with settings {settings.json()}')
    uvicorn.run(app, host=settings.host, port=settings.port)

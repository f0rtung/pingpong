import typing
import random

from pydantic import BaseModel


class PingModelIn(BaseModel):
    digits: typing.List[int] = []
    avg: typing.Optional[float]
    max: typing.Optional[int]
    min: typing.Optional[int]


def is_invalid_ping(_: PingModelIn) -> bool:
    return random.randint(0, 10) % 3 == 0

import typing

from pydantic import BaseModel


class PingModel(BaseModel):
    digits: typing.List[int] = ...
    avg: typing.Optional[float]
    max: typing.Optional[int]
    min: typing.Optional[int]

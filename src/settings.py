import enum
import typing

from aiomisc.log import LogLevel
from pydantic import BaseSettings


@enum.unique
class AppMode(enum.Enum):
    digits = enum.auto()
    avg_max_min = enum.auto()


class Settings(BaseSettings):
    host: str = '0.0.0.0'
    port: int = 8080
    ping_url: str = 'http://0.0.0.0:8080/ping'
    mode_str: str = AppMode.digits.name
    log_level_str: str = 'info'

    def __init__(self, **values: typing.Any):
        super().__init__(**values)

    @property
    def mode(self) -> AppMode:
        return AppMode[self.mode_str.lower()]

    @property
    def log_level(self) -> LogLevel:
        return LogLevel[self.log_level_str.lower()]

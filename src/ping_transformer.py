import random
import typing

from ping_model import PingModel
from settings import AppMode

PingTransformerFn = typing.Callable[[PingModel], PingModel]


def make_ping_transformer(app_mode: AppMode) -> PingTransformerFn:
    if app_mode == AppMode.digits:
        def digits_action(ping: PingModel) -> PingModel:
            ping.digits.append(random.randint(0, 100))
            return ping
        return digits_action
    elif app_mode == AppMode.avg_max_min:
        def avg_max_min_action(ping: PingModel) -> PingModel:
            if ping.digits:
                d = ping.digits
                ping.avg = sum(d) / len(d)
                ping.min = min(d)
                ping.max = max(d)
            return ping
        return avg_max_min_action
    raise RuntimeError(f'Invalid app mode {app_mode.name}')

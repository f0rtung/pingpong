import random
import typing

from ping_model import PingModelIn
from settings import AppMode

PingTransformerFn = typing.Callable[[PingModelIn], PingModelIn]


def make_ping_transformer(app_mode: AppMode) -> PingTransformerFn:
    if app_mode == AppMode.digits:
        def digits_action(ping: PingModelIn) -> PingModelIn:
            ping.digits.append(random.randint(0, 100))
            return ping
        return digits_action
    elif app_mode == AppMode.avg_max_min:
        def avg_max_min_action(ping: PingModelIn) -> PingModelIn:
            if ping.digits:
                d = ping.digits
                # Not optimal, complexity = 3n, but could be n
                ping.avg = sum(d) / len(d)
                ping.max = max(d)
                ping.min = min(d)
            return ping
        return avg_max_min_action
    raise RuntimeError(f'Invalid app mode {app_mode.name}')

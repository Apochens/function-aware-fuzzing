from functools import wraps
from typing import NoReturn, Tuple
from enum import Enum
import time
from pathlib import Path


PATH_ROOT = Path(__file__).parent
PATH_LOG = PATH_ROOT.joinpath('log')
PATH_SEED = PATH_ROOT.joinpath('saved-seed')
PATH_DUMMY = PATH_ROOT.joinpath('dummy')
PATH_CONFIG = PATH_ROOT.joinpath('server-config.ini')


Addr = Tuple[str, int]


def obsleted(f):

    @wraps(f)
    def wrapper(*args, **kwargs) -> NoReturn:
        raise Exception(f"Use obsleted function: {f.__module__}::{f.__name__}")

    return wrapper


def format_time(time_in_sec: float) -> str:
    hour, left = divmod(time_in_sec, 3600)
    min, sec = divmod(left, 60)
    return f'{int(hour):02d}:{int(min):02d}:{int(sec):02d}'


def get_local_time() -> str:
    fmt_str = "%Y-%m-%d-%H-%M-%S"
    return time.strftime(fmt_str)


class Timer:

    def __init__(self) -> None:
        self._start_time = 0
        self._total_time = 0

        self._epoch_count = 0

        self._last_interval = 0
        self._epoch_interval = 0

    def count(self):
        """Epoch count adds 1, update the epoch interval"""
        self._epoch_count += 1
        self._last_interval = self._epoch_interval
        self._epoch_interval = 0

    def __enter__(self) -> "Timer":
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        interval: float = time.time() - self.start_time
        self._epoch_interval += interval
        self._total_time += interval

    @property
    def epoch_count(self) -> int:
        """The total epoch count"""
        return self._epoch_count

    @property
    def epoch_time(self) -> float:
        """The time of one epoch"""
        return self._last_interval
    
    @property
    def total_time(self) -> float:
        """The total execution time"""
        return self._total_time

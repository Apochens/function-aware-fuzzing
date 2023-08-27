from functools import wraps
from typing import NoReturn, Tuple
from enum import Enum
import time
from pathlib import Path


PATH_ROOT = Path(__file__).parent
PATH_LOG = PATH_ROOT.joinpath('log')
PATH_SEED = PATH_ROOT.joinpath('saved-seed')


Addr = Tuple[str, int]


class Protocol(Enum):
    FTP = 959
    SMTP = 5321
    DNS = 1034

    @classmethod
    def new(cls, protocol: str) -> "Protocol":
        if protocol == 'ftp':
            return cls.FTP
        if protocol == 'smtp':
            return cls.SMTP
        if protocol == 'dns':
            return cls.DNS
        raise Exception("No such protocol")


def obsleted(f):

    @wraps(f)
    def wrapper(*args, **kwargs) -> NoReturn:
        raise Exception(f"Use obsleted function: {f.__module__}::{f.__name__}")

    return wrapper


def format_time(time_in_sec: float) -> str:

    time_str = ''
    time_str += f"{int(time_in_sec // 3600)}h"

    time_in_sec = time_in_sec % 3600 

    hour, left = divmod(time_in_sec, 3600)
    min, sec = divmod(left, 60)


    return f'{hour:02d}:{min:02d}:{sec:02d}'


def get_local_time() -> str:
    fmt_str = "%Y-%m-%d-%H-%M-%S"
    return time.strftime(fmt_str)
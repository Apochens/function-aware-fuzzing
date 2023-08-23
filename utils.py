from functools import wraps
from typing import NoReturn, Tuple
from enum import Enum
import time


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


def get_local_time() -> str:
    fmt_str = "%Y-%m-%d-%H-%M-%S"
    return time.strftime(fmt_str)
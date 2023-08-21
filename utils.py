from functools import wraps
from typing import NoReturn, Tuple


Addr = Tuple[str, int]


def obsleted(f):

    @wraps(f)
    def wrapper(*args, **kwargs) -> NoReturn:
        raise Exception(f"Use obsleted function: {f.__module__}::{f.__name__}")

    return wrapper
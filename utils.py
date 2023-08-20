from functools import wraps
from typing import NoReturn


def obsleted(f):

    @wraps(f)
    def wrapper(*args, **kwargs) -> NoReturn:
        raise Exception("Use obsleted code")

    return wrapper
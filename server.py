"""Server wrappers"""

from abc import ABC, abstractmethod
from pathlib import Path


class Server(ABC):

    def __init__(self, path: str) -> None:
        self.path: Path = Path(path)

    @abstractmethod
    def start():
        pass

    @abstractmethod
    def terminate():
        pass

    @abstractmethod
    def collect_coverage():
        pass


class LightFTP(Server):
    pass
from typing import List, Any
from copy import deepcopy
from enum import Enum
import logging


from corpus.fn import Fn
from exception import FnExecFailed
from utils import Protocol


logger = logging.getLogger("seed")


class Seed:
    """
    The fuzzing seed, a list of function calls (class `Fn`)
    """
    def __init__(self, fn_list: List[List[Any]]) -> None:
        self.fns: List[Fn] = [Fn(fn_name, args) for fn_name, *args in fn_list]
        self.mutations: List[str] = []
        self.power = 1

        self.succ_count: int = 0
        self.fail_count: int = 0

    @classmethod
    def new(cls, protocol: Protocol) -> "Seed":
        """Construct the corresponding seed"""
        SEED = None

        if protocol == Protocol.FTP:
            from .ftpseed import SEED
        if protocol == Protocol.SMTP:
            from .smtpseed import SEED
        if protocol == Protocol.DNS:
            from .dnsseed import SEED
        
        if SEED is None:
            raise Exception(f"No seed found for {protocol.name}")
        
        if len(SEED) == 0:
            logger.warning("The initial seed has no api call.")

        logger.debug(f"Use {protocol.name} seed")
        return cls(SEED)

    def execute(self, obj: object) -> None:
        """
        Execute the seed
        
        Args:
            obj (object): The corresponding client or library for executing the seed (APIs)
        """
        for fn in self.fns:
            try:
                logger.debug(f"Executing {fn.fn_name}: {fn}")
                fn.execute(obj)
                self.succ_count += 1
            except FnExecFailed:
                self.fail_count += 1  

    def save(self, path: str):
        pass

    def copy(self) -> "Seed":
        new_seed: Seed = deepcopy(self)
        new_seed.succ_count = new_seed.fail_count = 0
        return new_seed
        
    def len(self) -> int:
        return len(self.fns)
    
    def insert(self, pos: int, fn: Fn):
        self.fns.insert(pos + 1, fn)

    def __str__(self) -> str:
        return "<Seed\n" + '\n'.join([str(fn) for fn in self.fns]) + '\n>\n'

    def __repr__(self) -> str:
        return f"<Seed {self.mutations}>"

    def __getitem__(self, index) -> Fn:
        return self.fns[index]
    
    def __setitem__(self, index: int, value: Fn) -> None:
        self.fns[index] = value
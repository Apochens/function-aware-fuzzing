from typing import List, Any
from copy import deepcopy
from enum import Enum
import logging
from pathlib import Path
import pickle

from seed.fn import Fn
from exception import FnExecFailed
from utils import get_local_time


SEED_INDEX = 0
logger = logging.getLogger("fazz.seed")


class SeedStatus(Enum):
    Timeout = -1
    Boring = 0
    Interesting = 1
    Crash = 2


class Seed:
    """
    The fuzzing seed, a list of function calls (class `Fn`)
    """
    def __init__(self, fn_list: List[List[Any]]) -> None:
        self.fns: List[Fn] = [Fn(fn_name, args) for fn_name, *args in fn_list]
        self.mutations: List[str] = []
        self.power = 1  # Now, for simplicity, we just use 1
        self.execute_count = 0

        self.succ_count: int = 0
        self.fail_count: int = 0

    def execute(self, obj: object) -> None:
        """
        Execute the seed
        
        Args:
            obj (object): The corresponding client or library for executing the seed (APIs)

        Returns True when execution timeouts, otherwise False
        """
        self.execute_count += 1
        for fn in self.fns:
            try:
                logger.debug(f"Executing {fn.fn_name}: {fn}")
                fn.execute(obj)
                self.succ_count += 1
            except FnExecFailed:
                self.fail_count += 1  

    def save(self, path: Path, status: SeedStatus) -> None:
        """
        Save this seed (Interesting or Crash) into binary file by pickling
        """
        global SEED_INDEX
        file = None

        if status == SeedStatus.Interesting:
            logger.debug("Save seed causing a coverage increase.")
            file = path.joinpath(f"cov_{get_local_time()}_{SEED_INDEX:07d}")

        if status == SeedStatus.Crash:
            logger.debug("Save seed causing a crash.")
            file = path.joinpath(f"crash_{get_local_time()}_{SEED_INDEX:07d}")

        if file is not None:
            SEED_INDEX += 1
            pickle.dump(self, file.open('wb'))

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
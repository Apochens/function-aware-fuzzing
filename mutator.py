from abc import ABC, abstractmethod
from typing import List, Any
import random
import sys


class Mutator(ABC):
    """
    Mutator interface
    """
    @abstractmethod
    def mutate(self, seed: List):
        return seed

    @abstractmethod
    def name(self) -> str:
        pass


class DupMutator(Mutator):
    """
    Choose one api call in a seed to duplicate it.
    """

    def mutate(self, seed: List):
        randpos = random.randrange(0, len(seed))
        seed.insert(randpos + 1, seed[randpos])

    def name(self) -> str:
        return "dup"


class SwapMutator(Mutator):
    """
    Choose two api calls in a seed to swap them
    """

    def mutate(self, seed: List):
        randpos1 = random.randrange(0, len(seed))
        while (randpos2 := random.randrange(0, len(seed))) == randpos1:
            continue

        seed[randpos1], seed[randpos2] = seed[randpos2], seed[randpos1]

    def name(self) -> str:
        return "swap"


class ArgMutator(Mutator):
    """
    Choose one api call in a seed to mutate its arguments
    """

    def mutate(self, seed: List):
        randpos: int = random.randrange(0, len(seed))
        fn: List = seed[randpos]

        mutated_args: List[Any] = []
        for arg in fn[1:]:
            mutated_arg: Any = arg

            if isinstance(arg, int):    # type int
                mutated_arg = random.randint(-sys.maxsize, sys.maxsize)

            if isinstance(arg, bool):   # type bool
                mutated_arg = True if random.choice([0, 1]) == 1 else False

            if isinstance(arg, str):    # type str
                mutated_arg = arg
            
            mutated_args.append(mutated_arg)

        seed[randpos] = [fn[0]] + mutated_args
    
    def name(self) -> str:
        return "arg"


class DelMutator(Mutator):
    """
    Choose one api call in a seed to delete it
    """

    def mutate(self, seed: List):
        if len(seed) > 2:
            randpos = random.randrange(0, len(seed))
            seed.remove(seed[randpos])

    def name(self) -> str:
        return "del"


class InsertMutator(Mutator):
    """
    Randomly insert an api call into a seed
    """


class MutExecutor:
    """
    Mutation executor
    """

    def __init__(self) -> None:
        self.mutators: List[Mutator] = [
            DupMutator(), 
            SwapMutator(),
            ArgMutator(),
            DelMutator(),
        ]

    def mutate(self, queue: List, *, top_n: int = 10, mut_limit: int = 5) -> List:
        """Given a queue, mutate seeds with `top_n` priority. Perform no more than `mut_limit` mutations."""
        mutated_queue: List = []

        # only mutate seeds with `top_n` priority
        for seed in queue[:top_n]:
            mutated_seed = seed[:]

            # mutate
            for mutator in random.choices(self.mutators, k=random.randint(1, mut_limit)):
                mutator.mutate(mutated_seed)

            mutated_queue.append(mutated_seed)

        return mutated_queue

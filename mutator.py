from abc import ABC, abstractmethod
from typing import List
import random
from copy import deepcopy

from corpus.seed import Seed


class Mutator(ABC):
    """
    Mutator interface
    """
    @abstractmethod
    def mutate(self, seed: Seed):
        pass

    @abstractmethod
    def name(self) -> str:
        return "base"

    def __repr__(self):
        return f"Mutator[{self.name()}]"


class DupMutator(Mutator):
    """
    Choose one api call in a seed to duplicate it.
    """
    def mutate(self, seed: Seed) -> None:
        seed.mutations.append(self.name())

        randpos: int = random.randrange(0, seed.len())
        seed.insert(randpos, deepcopy(seed[randpos]))

    def name(self) -> str:
        return "dup"


class SwapMutator(Mutator):
    """
    Choose two api calls in a seed to swap them
    """
    def mutate(self, seed: Seed) -> None:

        # If the number of API calls in a seed is less than 2, 
        # it will cause an infinite loop when choosing API calls to exchange 
        if seed.len() < 2:
            return

        seed.mutations.append(self.name())

        randpos1 = random.randrange(0, seed.len())
        while (randpos2 := random.randrange(0, seed.len())) == randpos1:
            continue

        seed[randpos1], seed[randpos2] = seed[randpos2], seed[randpos1]

    def name(self) -> str:
        return "swap"


class DelMutator(Mutator):
    """
    Choose one api call in a seed to delete it
    """
    def mutate(self, seed: Seed):
        seed.mutations.append(self.name())

        if seed.len() > 2:
            randpos = random.randrange(0, seed.len())
            seed.fns.remove(seed[randpos])
        
    def name(self) -> str:
        return "del"
    

class ArgMutator(Mutator):
    """
    Choose one api call in a seed to mutate its arguments
    """
    def mutate(self, seed: Seed) -> None:
        seed.mutations.append(self.name())

        randpos: int = random.randrange(0, seed.len())
        fn = seed[randpos]

        for arg in fn.args:
            if arg.mutable:
                arg.mutate()
    
    def name(self) -> str:
        return "arg"


class InsMutator(Mutator):
    """
    Randomly insert an api call into a seed
    """
    def mutate(self, seed: Seed):
        return 
    
    def name(self) -> str:
        return "ins"


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

    def mutate(self, queue: List[Seed], *, top_n: int = 10, mut_limit: int = 5) -> List[Seed]:
        """Given a queue, mutate seeds with `top_n` priority. Perform no more than `mut_limit` mutations."""
        mutated_queue: List[Seed] = []

        # only mutate seeds with `top_n` priority
        for seed in queue[:top_n]:

            for _ in range(0, seed.power):  # power schedule
                mutated_seed: Seed = seed.copy()
                mutator = random.choice(self.mutators)
                mutator.mutate(mutated_seed)
                mutated_queue.append(mutated_seed)

        return mutated_queue

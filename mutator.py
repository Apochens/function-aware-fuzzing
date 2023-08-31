from abc import ABC, abstractmethod
from typing import List, Tuple
import random
from copy import deepcopy

from seed import Seed


class Mutator(ABC):
    """
    Mutator interface
    """
    @abstractmethod
    def mutate(self, seed: Seed) -> Seed:
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
    def mutate(self, seed: Seed) -> Seed:
        seed = seed.copy()

        seed.mutations.append(self.name())

        randpos: int = random.randrange(0, seed.len())
        seed.insert(randpos, deepcopy(seed[randpos]))

        return seed

    def name(self) -> str:
        return "dup"


class SwapMutator(Mutator):
    """
    Choose two api calls in a seed to swap them
    """
    def mutate(self, seed: Seed) -> Seed:
        seed = seed.copy()
        # If the number of API calls in a seed is less than 2, 
        # it will cause an infinite loop when choosing API calls to exchange 
        if seed.len() < 2:
            return seed

        seed.mutations.append(self.name())

        randpos1 = random.randrange(0, seed.len())
        while (randpos2 := random.randrange(0, seed.len())) == randpos1:
            continue

        seed[randpos1], seed[randpos2] = seed[randpos2], seed[randpos1]

        return seed

    def name(self) -> str:
        return "swap"


class DelMutator(Mutator):
    """
    Choose one api call in a seed to delete it
    """
    def mutate(self, seed: Seed) -> Seed:
        seed = seed.copy()
        seed.mutations.append(self.name())

        if seed.len() > 2:
            randpos = random.randrange(0, seed.len())
            seed.fns.remove(seed[randpos])
        
        return seed
        
    def name(self) -> str:
        return "del"
    

class ArgMutator(Mutator):
    """
    Choose one api call in a seed to mutate its arguments
    """
    def mutate(self, seed: Seed) -> Seed:
        seed = seed.copy()
        seed.mutations.append(self.name())

        randpos: int = random.randrange(0, seed.len())
        fn = seed[randpos]

        for arg in fn.args:
            if arg.mutable:
                arg.mutate()
        
        return seed
    
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
        self.mutator_with_weight: List[Tuple[Mutator, float]] = [
            (ArgMutator(), 0.4),
            (DupMutator(), 0.2), 
            (SwapMutator(), 0.2),
            (DelMutator(), 0.2),
        ]

    @property
    def mutators(self):
        return [mutator for mutator, _ in self.mutator_with_weight]

    @property
    def weights(self):
        return [weight for _, weight in self.mutator_with_weight]

    def mutate(self, queue: List[Seed], *, top_n: int = 10, mut_limit: int = 5) -> List[Seed]:
        """Given a queue, mutate seeds with `top_n` priority. Perform no more than `mut_limit` mutations."""
        # Only mutate seeds with `top_n` priority
        # For now, for simplicity, we just use sample to random select #top_n seeds to mutate
        # TODO: Use priority algorithm to select seeds
        selected_seeds = random.sample(queue, top_n) if top_n < len(queue) else queue

        return [mutator.mutate(seed) 
                for seed in selected_seeds 
                for mutator in random.choices(self.mutators, self.weights, k=seed.power)]

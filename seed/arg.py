from abc import ABC, abstractmethod
from typing import Tuple, Union, Callable, TypeVar, Generic
from io import BufferedReader, TextIOWrapper
from pathlib import Path
from enum import Enum
import sys
import random

T = TypeVar("T")

class Arg(ABC, Generic[T]):
    """
    The wrapper of parameters in the signature of function calls (class `Fn`).
    To inherent this abstract class, `mutate` and `unpack` must be overrided.
    """
    def __init__(self, value: T, /, mutable: bool = True, name: str = "") -> None:
        self.value = value
        self.__mutable = mutable

    @property
    def mutable(self) -> bool:
        return self.__mutable

    @abstractmethod
    def mutate(self) -> None:
        pass
    
    @abstractmethod
    def unpack(self):
        pass

    def __repr__(self) -> str:
        return f'<{type(self)} {self.value}>'
    
    def __str__(self) -> str:
        class_type = str(type(self)).split(".")[-1].split("'")[0]
        value = self.value
        if isinstance(value, Callable):
            value = value.__name__

        return f"<{class_type} {value}>"
    

Number = Union[int, float]


class NumberArg(Arg[Number]):
    """
    Argument wrapper for number (i.e., int and float)
    """
    def mutate(self) -> None:
        if isinstance(self.value, int):
            self.value = random.randint(-sys.maxsize, sys.maxsize)
        if isinstance(self.value, float):
            self.value = random.uniform(sys.float_info.min, sys.float_info.max)

    def unpack(self) -> Union[int, float]:
        return self.value


class StringArg(Arg[str]):
    """
    Argument wrapper for string
    """
    def mutate(self) -> None:

        def random_pair() -> Tuple[int, int]:
            pos1 = random.randrange(0, len(self.value))
            pos2 = random.randrange(0, len(self.value))
            return (pos1, pos2) if pos1 < pos2 else (pos2, pos1)

        if len(self.value) == 0:
            #TODO: write a mutation
            return

        pos1, pos2 = random_pair()
        
        choice = random.randint(1, 3)
        if choice == 1:  # slicing
            self.value = self.value[pos1:pos2]  
        if choice == 2:  # deletion
            self.value = self.value[:pos1] + self.value[pos2:]  
        if choice == 3:  # duplicate
            self.value = self.value[:pos2] + self.value[pos1:pos2] + self.value[pos2:]  

    def unpack(self):
        return self.value


class BooleanArg(Arg[bool]):
    """
    Argument wrapper for bool
    """
    def mutate(self) -> None:
        self.value = not self.value

    def unpack(self) -> bool:
        return self.value


class FileDescriptorArg(Arg[Path]):
    """
    Argument wrapper for string
    """
    def mutate(self) -> None:
        pass

    def unpack(self) -> Union[BufferedReader, TextIOWrapper]:
        return self.value.open('rb')


class CallableArg(Arg[Callable]):
    """
    Argument wrapper for function
    """
    def mutate(self) -> None:
        pass 

    def unpack(self) -> Callable:
        return self.value


# Generic type for enumeration
E = TypeVar("E", bound=Enum)


class EnumArg(Arg[E]):
    """
    Argument wrapper for enumeration
    """

    def mutate(self) -> None:
        candidate = [member for member in type(self.value)]
        self.value = random.choice(candidate)
    
    def unpack(self) -> E:
        return self.value
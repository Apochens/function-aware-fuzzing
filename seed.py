import random
import sys
from pathlib import Path
from os.path import abspath
from typing import List, Any, Tuple, Union, Callable, Iterable
from abc import ABC, abstractmethod
from copy import deepcopy
from colorama import Fore

from io import BufferedReader, TextIOWrapper


class Arg(ABC):
    """
    The wrapper of parameters in the signature of function calls (class `Fn`)
    """
    def __init__(self, value) -> None:
        self.value = value

    @abstractmethod
    def mutate(self) -> None:
        pass
    
    @abstractmethod
    def unpack(self):
        pass

    def __repr__(self) -> str:
        return f'<{type(self)} {self.value}>'
    
    def __str__(self) -> str:
        class_type = str(type(self)).split(".")[1].split("'")[0]
        value = self.value
        if isinstance(value, Callable):
            value = value.__name__

        return f"""<{class_type} {value}>"""


class Fn:
    """
    The function call, which is the component of a seed (class `Seed`). 
    A function call consists of a function name and a list of arguments (class `Arg`). 
    """
    def __init__(self, fn_name: str, args: Iterable) -> None:
        self.fn_name: str = fn_name
        self.args: List[Arg] = self.__init_args(args)

    def execute(self, obj: object):
        real_fn = getattr(obj, self.fn_name)
        try:
            resp = real_fn(*[arg.unpack() for arg in self.args])
            # print(f'''{Fore.GREEN}Execution succeed{Fore.RESET}: {self.fn_name} - {resp}''')
        except Exception as e:
            # print(f'''{Fore.RED}Execution failed{Fore.RESET}: {self.fn_name} - {e}''')
            raise e

    def __init_args(self, args: Iterable) -> List[Arg]:
        inited_args: List[Arg] = []
        for arg in args:
            type_str = str(type(arg))

            # boolean
            if isinstance(arg, bool):  
                inited_args.append(BooleanArg(arg))
                continue

            # int | float
            if isinstance(arg, int) or isinstance(arg, float):  
                inited_args.append(NumberArg(arg))
                continue

            # string
            if isinstance(arg, str):
                inited_args.append(StringArg(arg))
                continue

            # IO
            if "_io" in type_str:
                arg_value = abspath(arg.name)
                inited_args.append(FileDescriptorArg(arg_value))
                continue

            # Callable
            if isinstance(arg, Callable):
                inited_args.append(CallableArg(arg))
                continue

            print(type(arg), arg, end='\n\n')
        return inited_args

    def __str__(self) -> str:
        return f"{self.fn_name}({','.join([str(arg) for arg in self.args])})"


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

    def execute(self, obj: object) -> None:
        """Execute the seed"""
        for fn in self.fns:
            try:
                fn.execute(obj)
                self.succ_count += 1
            except Exception as e:
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


class NumberArg(Arg):
    """
    Argument wrapper for number (i.e., int and float)
    """
    def mutate(self) -> None:
        self.value = random.randint(-sys.maxsize, sys.maxsize)

    def unpack(self) -> Union[int, float]:
        return self.value


class StringArg(Arg):
    """
    Argument wrapper for string
    """
    def mutate(self) -> None:
        pass

    def unpack(self):
        return self.value


class BooleanArg(Arg):
    """
    Argument wrapper for bool
    """
    def mutate(self) -> None:
        self.value = random.choice([True, False])

    def unpack(self) -> bool:
        return self.value


class FileDescriptorArg(Arg):
    """
    Argument wrapper for string
    """
    def mutate(self) -> None:
        pass

    def unpack(self) -> Union[BufferedReader, TextIOWrapper]:
        return Path(self.value).open('rb')


class CallableArg(Arg):

    def mutate(self) -> None:
        return 

    def unpack(self) -> Callable:
        return self.value


#############################
#     SEED FOR LIGHTFTP     #
#############################
def simple_callback(data: Any) -> None:
    return

SEED_FTP = [
    ['connect', '127.0.0.1', 2200], 
    ['login', 'linuxbrew', '123456'],

    ["getwelcome"],

    ["pwd"],
    ["mkd", "test"],

    ["cwd", "test"],

    ["storbinary", "STOR temp1.txt", Path('temp.txt').open("rb")],
    ["storbinary", "APPE temp1.txt", Path('temp.txt').open("rb")],

    ["storlines", "STOR temp2.txt", Path('temp.txt').open("rb")],
    ["storlines", "APPE temp2.txt", Path('temp.txt').open("rb")],

    ["rename", "temp2.txt", "test.txt"],

    ["retrbinary", "RETR test.txt", simple_callback, 8192, 0],
    ["retrbinary", "LIST", simple_callback],
    ["retrbinary", "NLST", simple_callback],

    ["retrlines", "RETR temp1.txt", simple_callback],
    ["retrlines", "LIST", simple_callback],
    ["retrlines", "NLST", simple_callback],

    ["size", "test.txt"],   # Request the size of the file named filename on the server.
    ["dir"],

    ["nlst"],
    ["mlsd"],

    ["delete", "temp1.txt"],
    ["delete", "test.txt"],

    ["cwd", ".."],
    ["rmd", "test"],

    # ["abort"],
    ["set_pasv", True],
    # ["close"],
    ["quit"],
]
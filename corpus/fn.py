import logging
from typing import List

from colorama import Fore

from arg import Arg


logger = logging.getLogger("apifuzz")


class Fn:
    """
    The function call, which is the component of a seed (class `Seed`). 
    A function call consists of a function name and a list of arguments (class `Arg`). 
    """
    def __init__(self, fn_name: str, args: List[Arg]) -> None:
        self.fn_name: str = fn_name
        self.args: List[Arg] = args # self.__init_args(args)

    def execute(self, obj: object):
        real_fn = getattr(obj, self.fn_name)
        try:
            resp = real_fn(*[arg.unpack() for arg in self.args])
            logger.debug(f'''{Fore.GREEN}Execution succeed{Fore.RESET}: {self.fn_name} - {resp}''')
        except Exception as e:
            logger.error(f'''{Fore.RED}Execution failed{Fore.RESET}: {self.fn_name} - {e}''')
            raise e

    # def __init_args(self, args: Iterable) -> List[Arg]:
    #     inited_args: List[Arg] = []
    #     for arg in args:
    #         type_str = str(type(arg))

    #         # boolean
    #         if isinstance(arg, bool):  
    #             inited_args.append(BooleanArg(arg))
    #             continue

    #         # int | float
    #         if isinstance(arg, int) or isinstance(arg, float):  
    #             inited_args.append(NumberArg(arg))
    #             continue

    #         # string
    #         if isinstance(arg, str):
    #             inited_args.append(StringArg(arg))
    #             continue

    #         # IO
    #         if "_io" in type_str:
    #             arg_value = abspath(arg.name)
    #             inited_args.append(FileDescriptorArg(arg_value))
    #             continue

    #         # Callable
    #         if isinstance(arg, Callable):
    #             inited_args.append(CallableArg(arg))
    #             continue

    #         if isinstance(arg, FileDescriptorArg):
    #             inited_args.append(arg)
    #             continue

    #         print(type(arg), arg, end='\n\n')
    #     return inited_args

    def __str__(self) -> str:
        return f"{self.fn_name}({','.join([str(arg) for arg in self.args])})"
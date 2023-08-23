import logging
from typing import List

from colorama import Fore

from .arg import Arg


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

    def __str__(self) -> str:
        return f"{self.fn_name}({','.join([str(arg) for arg in self.args])})"
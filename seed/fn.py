import logging
from typing import List

from colorama import Fore

from seed.arg import Arg
from exception import FnExecFailed, FnNotFound


logger = logging.getLogger("fn")


class Fn:
    """
    The function call, which is the component of a seed (class `Seed`). 
    A function call consists of a function name and a list of arguments (class `Arg`). 
    """
    def __init__(self, fn_name: str, args: List[Arg]) -> None:
        self.fn_name: str = fn_name
        self.args: List[Arg] = args

    def execute(self, obj: object):
        """
        
        Args:
            obj (object): The corresponding client

        Raises:
            FnNotFound: When the function is not found in the client
            ExecutionFailed: When the client fails to execute the given function 
                (including exceptions raised by the executed function when it handles error messages from the server )
        """
        try:
            real_fn = getattr(obj, self.fn_name)
        except AttributeError:
            logger.error(f"No such function: {self.fn_name}")
            raise FnNotFound(f"No such function: {self.fn_name}")

        try:
            resp = real_fn(*[arg.unpack() for arg in self.args])
            logger.debug(f'''{Fore.GREEN}Execution succeed{Fore.RESET}: {self.fn_name} - {resp}''')
        except Exception as e:
            logger.error(f'''{Fore.RED}Execution failed{Fore.RESET}: {self.fn_name} - {e}''')
            raise FnExecFailed

    def __str__(self) -> str:
        return f"{self.fn_name}({','.join([str(arg) for arg in self.args])})"
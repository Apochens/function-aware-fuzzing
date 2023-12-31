"""Server wrappers"""
import os
import subprocess
import re
import signal
import logging
from pathlib import Path
from configparser import ConfigParser
from typing import Optional, Tuple, Union
from abc import ABC, abstractmethod

from utils import Addr
from exception import ServerConfigNotFound, ServerTerminated, ServerNotStarted

logger = logging.getLogger("server")
SERVER_CONFIG_PATH = Path(__file__).parent.joinpath("server-config.ini")


class Server(ABC):
    """Abstract server wrapper"""
    name = "ServerWrapper"

    def __init__(self, cmd: str, path: str, root: str, host: str, port: str, clean: Optional[str] = None) -> None:
        self.cmd: str = cmd
        self.cmd_cleanup: Optional[str] = clean
        
        self.path: str = path
        self.root: str = root
        self.old_path: str = ""

        self.__host = host
        self.__port = int(port)

        self.proc: Optional[subprocess.Popen] = None

    @property
    def addr(self) -> Addr:
        return (self.__host, self.__port)

    def _start(self) -> subprocess.Popen:
        if self.path:
            self.old_path = os.getcwd()
            os.chdir(self.path)

        self.proc = subprocess.Popen(self.cmd.split(' '), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if self.proc is None:
            raise ServerNotStarted("Cannot start server properly!")
        if self.proc.returncode:
            raise ServerTerminated("Server is down after starting!")
        logger.debug(f"Server is up at {self.addr}, pid is {self.proc.pid}")
        return self.proc

    @abstractmethod
    def _terminate(self) -> int:
        pass

    @abstractmethod
    def _cleanup(self) -> None:
        pass

    def collect_coverage(self) -> Tuple[float, int, float, int]:
        """ 
        For now, we use gcovr to collect the coverage for convenience.
        In the future, we will use approach like that used by AFL to collect runtime code coverage 
        """
        gcovr_proc = subprocess.Popen(f"gcovr -r {self.root} -s | grep [lb][ir][a-z]*:", stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        output = gcovr_proc.communicate()[0].decode().split('\n')

        ln_per, ln_abs = "", ""
        if (ln_match := re.match(r"lines: (\d+(?:\.\d+)?%) \((\d*) out of (\d*)\)", output[0])) is not None:
            ln_per, ln_abs, _ = ln_match.groups()
        else:
            raise Exception("Cannot parse line coverage")
        
        bc_per, bc_abs = "", ""
        if (bc_match := re.match(r"branches: (\d+(?:\.\d+)?%) \((\d*) out of (\d*)\)", output[1])) is not None:
            bc_per, bc_abs, _ = bc_match.groups()
        else:
            raise Exception("Cannot parse branch coverage")

        return float(ln_per[:-1]), int(ln_abs), float(bc_per[:-1]), int(bc_abs)

    def __enter__(self) -> subprocess.Popen:
        return self._start()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._terminate()
        self._cleanup()

    def __str__(self) -> str:
        return f"<Server {self.cmd} ({self.path})>"


class Target(Server):

    def _terminate(self) -> int:
        """Kill the server by default"""
        logger.debug("Killing the server...")
        if self.proc:
            self.proc.terminate()
            return self.proc.wait()
        return 0
    
    def _cleanup(self) -> int:
        """Do cleanup"""
        if self.cmd_cleanup is None:
            return 0
        logger.debug(f"Executing cleanup command: {self.cmd_cleanup}")
        proc_cleanup = subprocess.run(self.cmd_cleanup, shell=True)
        return proc_cleanup.returncode


class LightFTP(Server):
    """Wrapper for LightFTP"""
    name = 'LightFTP'

    def terminate(self) -> int:
        """Terminate the LightFTP server (input a `q` from the stdin)"""
        if self.proc is None:
            return 0

        self.proc.communicate('q'.encode())
        return self.proc.wait()


class ProFTPD(Server):
    """Wrapper for ProFTPD"""
    name = 'ProFTPD'

    def terminate(self) -> int:
        if self.proc is None:
            return 0
        
        self.proc.send_signal(0)
        return self.proc.wait()


class PureFTPD(Server):
    name = 'PureFTPD'

    def terminate(self) -> int:
        if self.proc is None:
            return 0

        self.proc.send_signal(signal.SIGKILL)
        print(f"Exitcode: {self.proc.wait()}")
        return self.proc.returncode

class ServerBuilder:

    def __init__(self, config_path: Union[str, Path] = SERVER_CONFIG_PATH) -> None:

        config_path = Path(config_path) if isinstance(config_path, str) else config_path
        if not config_path.exists():
            raise ServerConfigNotFound(f"No such configuration file: {config_path}")

        self.config: ConfigParser = ConfigParser()
        self.config.read(config_path)

    def get_target(self) -> Target:
        try:
            target = self.config['Target']
        except KeyError:
            raise Exception(f"No target configuration found!")
        
        return Target(**target)
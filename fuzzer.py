import time
from colorama import Style, Fore
from typing import List
import argparse
import logging
import multiprocessing as mp

from mutator import MutExecutor
from corpus import new_seed
from seed import Seed, SeedStatus
from server import Target, ServerBuilder
from utils import Protocol, get_local_time, PATH_LOG, format_time, PATH_SEED
from client import Client
from exception import SeedDryRunTimeout, ServerAbnormallyExited


Interesting = bool
logger = logging.getLogger("fuzzer")
PATH_SEED.mkdir(exist_ok=True)


class Fuzzer:

    def __init__(self: "Fuzzer", protocol: str, target: Target, *, timeout: int = 1, log: bool = False, timeout_testcase: float = 2.0) -> None:
        self.protocol: Protocol = Protocol.new(protocol)
        self.queue: List[Seed] = [new_seed(self.protocol)]

        # Timeout
        self.timeout = timeout
        self.timeout_testcase = timeout_testcase

        # Coverage
        self.line_cov = 0
        self.branch_cov = 0

        self.target: Target = target  # Server tested
        self.mut_executor = MutExecutor()

        self.log = self.create_log() if log else None

        self.start_time = 0
        self.epoch_count = 0

    def execute(self, seed: Seed):
        obj = Client.new(self.protocol, self.target.addr)
        seed.execute(obj)

    def fuzz_one(self: "Fuzzer", seed: Seed) -> SeedStatus:
        '''
        Execute one seed with coverage guided, return true if the seed is interesting
        
        Returns True is the seed is interesting, otherwise False
        '''
        # Start the server
        self.target.start()
        time.sleep(0.1)

        timeout = False

        exe_thread = mp.Process(target=self.execute, args=[seed,])
        exe_thread.start()
        exe_thread.join(timeout=self.timeout_testcase)

        if exe_thread.is_alive():
            exe_thread.terminate()
            timeout = True

        # Stop the server and check the exit status TODO: crash handler
        returncode = self.target.terminate()
        if returncode not in  (0, 2):
            raise ServerAbnormallyExited(f"Server abnormally exited with {returncode}.")

        if timeout:
            logger.debug("Seed execution timeouts...")
            return SeedStatus.Timeout

        # coverage guided
        cov = self.target.collect_coverage()
        if cov[1] > self.line_cov or cov[3] > self.branch_cov:
            self.line_cov = cov[1]
            self.branch_cov = cov[3]
            return SeedStatus.Interesting  # the seed is interesting 
    
        return SeedStatus.Boring  # the seed is not interesting

    def fuzz(self: "Fuzzer") -> None:
        '''main fuzzing loop'''
        self.start_time: float = time.time()
        self.epoch_count: int = 0

        print(f"{Style.DIM}", end=None)
        while ((epoch_start_time := time.time()) - self.start_time) < self.timeout * 60:

            # prepare execution queue (when epoch_count is 0, perform dry run)
            cur_queue = self.queue if self.epoch_count == 0 \
                else self.mut_executor.mutate(self.queue)
            
            # execute the queue
            for seed in cur_queue:
                if (status := self.fuzz_one(seed)) == SeedStatus.Interesting:
                    if self.epoch_count != 0:
                        self.queue.append(seed)
                        seed.save(PATH_SEED, status)
                        if self.log is not None:
                            self.log.write(str(seed))
                elif status == SeedStatus.Crash:
                    # TODO: handle crash seed
                    pass
                elif status == SeedStatus.Timeout:
                    if self.epoch_count == 0:
                        raise SeedDryRunTimeout("The initial seed given is timeout")

            self.epoch_count += 1

            # epoch log
            epoch_time = time.time() - epoch_start_time
            self.__write_epoch_status(epoch_time)

        # summary log 
        total_time = time.time() - self.start_time
        self.__write_fuzz_summary(total_time)

    def catch(self) -> None:
        """Only run the initial seeds"""
        logger.debug("Run one round for tcpdump or initialization test")
        self.start_time: float = time.time()
        self.epoch_count: int = 0

        self.fuzz_one(self.queue[0])

        self.__write_epoch_status(1)

    def create_log(self):
        """
        Create the log file
        """
        PATH_LOG.mkdir(exist_ok=True)

        log_name = f"{self.protocol.name}-{get_local_time()}.log"
        log_path = PATH_LOG.joinpath(log_name)
        return log_path.open("w", encoding="utf-8")

    def __write_epoch_status(self, epoch_time: float) -> None:
        """write status to stdout and log file"""
        epoch_string = f"{Style.RESET_ALL}{Style.BRIGHT}[{Fore.GREEN}{self.epoch_count:05d}{Fore.RESET}] "
        epoch_string += f"- {format_time(time.time() - self.start_time)} - interval: {epoch_time:.2f}s; total: {time.time() - self.start_time:.2f}s; "
        epoch_string += f"cov: {self.line_cov}/{self.branch_cov}; queue: {len(self.queue)}{Style.RESET_ALL}{Style.DIM}"
        print(epoch_string)

        # log
        if self.log is not None:
            epoch_string = f"[{self.epoch_count:05d}] interval: {epoch_time:.2f}s; total: {time.time() - self.start_time:.2f}s; cov: {self.line_cov}/{self.branch_cov}; queue: {len(self.queue)}"
            self.log.write(f"{epoch_string}\n")

    def __write_fuzz_summary(self, total_time: float) -> None:
        formated_time = format_time(total_time)
        info = f"Total {self.epoch_count} epoch, lcov: {self.line_cov}, bcov: {self.branch_cov}"

        # stdout
        summary_string = f"{Style.RESET_ALL}{Style.BRIGHT}[{Fore.BLUE}Summary{Fore.RESET}] - {formated_time} - {info}{Style.RESET_ALL}"
        print(summary_string)

        #log
        if self.log is not None:
            summary_string = f"[Summary] - {formated_time} - {info}"
            self.log.write(summary_string + "\n")

    def __del__(self):
        if self.log is not None:
            self.log.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Function-Aware Fuzzer')
    parser.add_argument('protocol', choices=['ftp', 'smtp', 'dns'])

    parser.add_argument('-t', '--timeout', type=int, default=1)
    parser.add_argument('-d', "--debug", default=False, action="store_true")
    parser.add_argument('-c', "--catch", default=False, action="store_true")
    parser.add_argument('-l', "--log", default=False, action="store_true")

    args = parser.parse_args()

    server_builder = ServerBuilder()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    fuzzer = Fuzzer(args.protocol, server_builder.get_target(), timeout=args.timeout, log=args.log)
    if args.catch:
        fuzzer.catch()
    else:
        fuzzer.fuzz()
import time
from colorama import Style, Fore
from ftplib import FTP
from typing import List, Tuple, Any
import argparse, subprocess, os
import re

from mutator import MutExecutor
from seed import Seed, SEED_FTP


def start_server() -> subprocess.Popen:
    """Start the FTP server"""
    server_path = "/home/linuxbrew/applications/LightFTP/Source/Release/"
    os.chdir(server_path)
    lightftp_server = "./fftp"

    proc = subprocess.Popen([lightftp_server], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=True)
    if not proc:
        raise Exception("Server down!")

    return proc


def stop_server(proc: subprocess.Popen) -> int:
    """Stop the FTP server"""
    proc.communicate('q'.encode())
    return proc.wait()


def get_local_time() -> str:
    fmt_str = "%Y-%m-%d-%H-%M-%S"
    return time.strftime(fmt_str)


def collect_coverage() -> Tuple[float, int, float, int]:
    """collect the execution coverage using gcovr"""
    server_path = "/home/linuxbrew/applications/LightFTP/Source/Release/"
    os.chdir(server_path)
    gcovr_proc = subprocess.Popen("gcovr -r .. -s | grep [lb][ir][a-z]*:", stdout=subprocess.PIPE, shell=True)
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


class Fuzzer:

    def __init__(self, seed: Seed, obj: str, *, timeout: int = 1, debug: bool = False) -> None:
        self.queue: List[Seed] = [seed]
        self.obj: str = obj
        self.timeout = timeout
        self.line_cov = 0
        self.branch_cov = 0

        self.mut_executor = MutExecutor()

        self.log_name = f"{obj}-{get_local_time()}.log"
        self.log = open(self.log_name, 'w', encoding='utf-8') if debug else None

        self.start_time = 0
        self.epoch_count = 0

    def fuzz_one(self, seed: Seed) -> bool:
        '''execute one seed with coverage guided'''
        obj = get_target_client(self.obj)

        print(repr(seed))
        proc = start_server()
        time.sleep(0.01)

        # execute the seed
        seed.execute(obj)

        stop_server(proc)

        # coverage guided
        cov = collect_coverage()
        if cov[1] > self.line_cov or cov[3] > self.branch_cov:
            
            self.line_cov = cov[1]
            self.branch_cov = cov[3]
            return True  # the seed is interesting 
    
        return False  # the seed is not interesting

    def fuzz(self):
        '''main fuzzing loop'''
        self.start_time: float = time.time()
        self.epoch_count: int = 0

        print(f"{Style.DIM}", end=None)
        while ((epoch_start_time := time.time()) - self.start_time) < self.timeout * 60:

            # prepare execution queue (when epoch_count is 0, perform dry run)
            cur_queue = self.queue if self.epoch_count == 0 \
                else self.mut_executor.mutate(self.queue)
            
            # execute
            for seed in cur_queue:
                if self.fuzz_one(seed) and self.epoch_count != 0:
                    self.queue.append(seed)

                    # record the interesting seed
                    if self.log is not None:
                        self.log.write(str(seed))

            self.epoch_count += 1

            # epoch log
            epoch_time = time.time() - epoch_start_time
            self.__write_epoch_status(epoch_time)

        # summary log 
        total_time = time.time() - self.start_time
        self.__write_fuzz_summary(total_time)

    def __write_epoch_status(self, epoch_time: float):
        """write status to stdout and log file"""
        epoch_string = f"{Style.RESET_ALL}{Style.BRIGHT}[{Fore.GREEN}Epoch {self.epoch_count}{Fore.RESET}]"
        epoch_string += f"interval: {epoch_time:.2f}s; total: {time.time() - self.start_time:.2f}s; "
        epoch_string += f"cov: {self.line_cov}/{self.branch_cov}; queue: {len(self.queue)}{Style.RESET_ALL}{Style.DIM}"
        print(epoch_string)

        # log
        if self.log is not None:
            epoch_string = f"[Epoch {self.epoch_count}] interval: {epoch_time:.2f}s; total: {time.time() - self.start_time:.2f}s; cov: {self.line_cov}/{self.branch_cov}; queue: {len(self.queue)}"
            self.log.write(f"{epoch_string}\n")

    def __write_fuzz_summary(self, total_time):
        # stdout
        summary_string = f"{Style.RESET_ALL}{Style.BRIGHT}[{Fore.BLUE}Summary{Fore.RESET}] Total {self.epoch_count} epoch - {total_time:.2f}s{Style.RESET_ALL}"
        print(summary_string)

        #log
        if self.log is not None:
            summary_string = f"[Summary] Total {self.epoch_count} epoch - {total_time:.2f}s"
            self.log.write(summary_string + "\n")

    def __del__(self):
        if self.log is not None:
            self.log.close()

def get_target_client(protocol: str) -> object:
    if protocol == 'ftp':
        return FTP()


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Function-Aware Fuzzer')
    parser.add_argument('protocol', choices=['ftp'])
    parser.add_argument('-t', '--timeout', type=int, default=1)
    parser.add_argument('-d', "--debug", default=False, action='store_true')

    args = parser.parse_args()

    fuzzer = Fuzzer(Seed(SEED_FTP), args.protocol, timeout=args.timeout, debug=args.debug)
    fuzzer.fuzz()
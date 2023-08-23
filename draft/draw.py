import re
from argparse import ArgumentParser
from typing import List, Tuple
import matplotlib.pyplot as plt


REGEX_PATTERN = r"Epoch (?P<epoch_count>\d+)] interval: (?P<interval>\d+\.\d+)s; total: (?P<total>\d+\.\d+)s; cov: (?P<lcov>\d+)/(?P<bcov>\d+); queue: (?P<queue_size>\d+)"


def extract_data(pattern: str, filename: str) -> Tuple[List[float], List[int], List[int]]:

    total: List[float] = []
    lcovs: List[int] = []
    bcovs: List[int] = []

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if (match := re.search(pattern, line)) is not None:
                res = match.groupdict()
                total.append(float(res['total']))
                lcovs.append(int(res['lcov']))
                bcovs.append(int(res['bcov']))

    return total, lcovs, bcovs

def draw_plot(data: Tuple[List[float], List[int], List[int]]):
    total, lcovs, bcovs = data

    fig, (line_ax, branch_ax) = plt.subplots(1, 2, figsize=(8, 2.5), layout='constrained')
    
    line_ax.plot(total, lcovs)
    line_ax.set_ylabel('Line coverage')
    line_ax.set_xlabel('Time (s)')

    branch_ax.plot(total, bcovs)
    branch_ax.set_ylabel('Branch coverage')
    branch_ax.set_xlabel('Time (s)')

    fig.savefig("result.png")


if __name__ == "__main__":
    parser = ArgumentParser("Result plot")
    parser.add_argument("log")

    args = parser.parse_args()

    data = extract_data(REGEX_PATTERN, args.log)
    draw_plot(data)

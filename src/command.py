from typing import List

from io_mode import IOMode
from signal_ import Signal


def cpu_stress(cores: int, percent: int, length: int) -> str:
    return f"stress-ng -c {cores} -l {percent} -t {length}"


def memory_stress(size: str, length: int = 60) -> str:
    return f"stress-ng -m 1 --vm-bytes {size} -t {length}"


def disk_stress(
    dir: str,
    workers: int,
    block_size: int,
    volume_percentage: int,
    length: int,
) -> str:
    return (
        "stress-ng"
        f" --temp-path {dir}"
        f" -d {workers}"
        f" --hdd-write-size {block_size}k"
        f" --hdd-bytes {volume_percentage}%"
        f" -t {length}"
    )


def io_stress(
    dir: str,
    workers: int,
    mode: IOMode,
    block_size: int,
    block_count: int,
    length: int,
) -> str:
    return (
        "fio"
        " -thread"
        f" -directory={dir}"
        f" -numjobs={workers}"
        f" -rw={mode.value}"
        f" -bs={block_size}k"
        f" -size={block_size * block_count}k"
        f" -runtime={length}"
        " -time_based -name=chaos -direct=1"
    )


def os_shutdown(delay: int, reboot: bool) -> str:
    opt = "r" if reboot else "h"
    return f"sudo shutdown -{opt} +{delay}"


def time_travel(offset: int) -> str:
    return f"sudo date -s `date --date='{offset} seconds' +@%s`"


def kill(signal: Signal, pid_lst: int) -> str:
    return f"sudo kill -{signal.value} {' '.join(map(str, pid_lst))}"


def kill_children_by_pid(signal: Signal, pid_lst: List[int]) -> str:
    return f"sudo pkill -{signal.value} -P {','.join(map(str, pid_lst))}"


def pkill(
    signal: Signal,
    process_name_lst: List[str],
    group: str = None,
    user: str = None,
    newest: bool = False,
    oldest: bool = False,
    exact: bool = False,
    full_match: bool = False,
    kill_children: bool = False,
) -> List[str]:
    opt_lst = []
    if group:
        opt_lst.append("-G")
        opt_lst.append(group)
    if user:
        opt_lst.append("-U")
        opt_lst.append(user)
    if newest:
        opt_lst.append("-n")
    if oldest:
        opt_lst.append("-o")
    if exact:
        opt_lst.append("-x")
    if full_match:
        opt_lst.append("-f")
    opts_str = " ".join(["", *opt_lst]) if opt_lst else ""
    cmd_lst = [
        f"for pname in {' '.join(process_name_lst)}; do sudo pkill -{signal.value} $pname{opts_str}; done"
    ]
    if kill_children:
        cmd_lst.insert(
            0,
            (
                f"for pname in {' '.join(process_name_lst)};"
                f" do for pid in $(pgrep $pname{opts_str});"
                f" do sudo pkill -{signal.value} -P $pid; done; done"
            ),
        )
    return cmd_lst

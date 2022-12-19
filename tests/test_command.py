from src.command import (
    cpu_stress,
    disk_stress,
    io_stress,
    kill,
    kill_children_by_pid,
    memory_stress,
    os_shutdown,
    pkill,
    time_travel,
)
from src.io_mode import IOMode
from src.signal_ import Signal


def test_cpu_stress():
    assert cpu_stress(cores=2, percent=50, length=10) == "stress-ng -c 2 -l 50 -t 10"


def test_memory_attack():
    assert (
        memory_stress(size="256m", length=60) == "stress-ng -m 1 --vm-bytes 256m -t 60"
    )


def test_disk_attack():
    assert (
        disk_stress(
            dir="foo/baz/bar", workers=3, block_size=4, volume_percentage=50, length=10
        )
        == "stress-ng --temp-path foo/baz/bar -d 3 --hdd-write-size 4k --hdd-bytes 50% -t 10"
    )


def test_io_stress():
    assert io_stress(
        dir="/tmp",
        workers=1,
        mode=IOMode.rw,
        block_size=4,
        block_count=1,
        length=60,
    ) == (
        "fio -thread"
        " -directory=/tmp"
        " -numjobs=1"
        " -rw=rw"
        " -bs=4k"
        " -size=4k"
        " -runtime=60"
        " -time_based -name=chaos -direct=1"
    )
    assert io_stress(
        dir="/foo/baz/bar",
        workers=4,
        mode=IOMode.r,
        block_size=2,
        block_count=10,
        length=10,
    ) == (
        "fio -thread"
        " -directory=/foo/baz/bar"
        " -numjobs=4"
        " -rw=read"
        " -bs=2k"
        " -size=20k"
        " -runtime=10"
        " -time_based -name=chaos -direct=1"
    )
    assert io_stress(
        dir="/tmp",
        workers=1,
        mode=IOMode.w,
        block_size=4,
        block_count=1,
        length=60,
    ) == (
        "fio -thread"
        " -directory=/tmp"
        " -numjobs=1"
        " -rw=write"
        " -bs=4k"
        " -size=4k"
        " -runtime=60"
        " -time_based -name=chaos -direct=1"
    )


def test_os_shutdown():
    assert os_shutdown(delay=1, reboot=True) == "sudo shutdown -r +1"
    assert os_shutdown(delay=5, reboot=False) == "sudo shutdown -h +5"


def test_time_travel():
    assert time_travel(86400) == "sudo date -s `date --date='86400 seconds' +@%s`"


def test_kill():
    assert (
        kill(signal=Signal.SIGKILL, pid_lst=[12345, 23456])
        == "sudo kill -KILL 12345 23456"
    )


def test_kill_children():
    assert (
        kill_children_by_pid(signal=Signal.SIGKILL, pid_lst=[2012, 2022])
        == "sudo pkill -KILL -P 2012,2022"
    )


def test_pkill():
    assert pkill(signal=Signal.SIGKILL, process_name_lst=["app1", "app2"]) == [
        "for pname in app1 app2; do sudo pkill -KILL $pname; done"
    ]


def test_pkill_when_group_parameter_is_passed():
    assert pkill(
        signal=Signal.SIGKILL, process_name_lst=["app1", "app2"], group="foo"
    ) == ["for pname in app1 app2; do sudo pkill -KILL $pname -G foo; done"]


def test_pkill_when_user_parameter_is_passed():
    assert pkill(
        signal=Signal.SIGKILL, process_name_lst=["app1", "app2"], user="baz"
    ) == ["for pname in app1 app2; do sudo pkill -KILL $pname -U baz; done"]


def test_pkill_when_newest_flag_is_True():
    assert pkill(signal=Signal.SIGKILL, process_name_lst=["process1"], newest=True) == [
        "for pname in process1; do sudo pkill -KILL $pname -n; done"
    ]


def test_pkill_when_oldest_flag_is_True():
    assert pkill(signal=Signal.SIGKILL, process_name_lst=["process1"], oldest=True) == [
        "for pname in process1; do sudo pkill -KILL $pname -o; done"
    ]


def test_pkill_when_exact_flag_is_True():
    assert pkill(signal=Signal.SIGKILL, process_name_lst=["process1"], exact=True) == [
        "for pname in process1; do sudo pkill -KILL $pname -x; done"
    ]


def test_pkill_when_full_match_flag_is_True():
    assert pkill(
        signal=Signal.SIGKILL, process_name_lst=["process1"], full_match=True
    ) == ["for pname in process1; do sudo pkill -KILL $pname -f; done"]


def test_pkill_when_kill_children_flag_is_True():
    assert pkill(
        signal=Signal.SIGKILL,
        process_name_lst=["app1", "app2"],
        newest=True,
        exact=True,
        full_match=True,
        kill_children=True,
    ) == [
        (
            "for pname in app1 app2; do for pid in $(pgrep $pname -n -x -f);"
            " do sudo pkill -KILL -P $pid; done; done"
        ),
        "for pname in app1 app2; do sudo pkill -KILL $pname -n -x -f; done",
    ]

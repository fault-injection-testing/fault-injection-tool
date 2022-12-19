import time

import paramiko
from beartype import beartype
from beartype.typing import Dict, List, Union

import command
import tc_schema
from io_mode import IOMode
from iptables_action import IptablesAction
from signal_ import Signal
from target import Target


@beartype
def inject_cpu_stress(
    cores: int = 1,
    percent: int = 100,
    length: int = 60,
    target: Dict[str, str] = None,
):
    """ターゲットのcpuに負荷をかける

    引数からcpu負荷をかけるコマンドを作成し,ターゲットのサーバ上で実行する

    Args:
        cores (int, optional): 利用するコア数. Defaults to 1.
        percent (int, optional): 各コアのcpu利用率. Defaults to 100.
        length (int, optional): cpu負荷をかける時間(秒). Defaults to 60.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: coresが1未満の値で指定された場合
        ValueError: percentが[0,100]の範囲外で指定された場合
        ValueError: ターゲットのサーバにSSH接続するために必要な情報が設定されていない場合
    """
    if cores < 1:
        raise ValueError("The argument 'cores' must be greater than or equal to 1")
    if percent not in range(0, 101):
        raise ValueError("The argument 'percent' must be between 0 and 100")
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    cmd = command.cpu_stress(cores=cores, percent=percent, length=length)
    __inject_command(command=cmd, target=target)


@beartype
def inject_memory_stress(
    mb: int = None,
    gb: int = None,
    percentage: int = 100,
    length: int = 60,
    target: Dict[str, str] = None,
):
    """ターゲットのメモリに負荷をかける

    引数からメモリ負荷をかけるコマンドを作成し,ターゲットのサーバ上で実行する

    Args:
        mb (int, optional): 利用するメモリの値(MB). Defaults to None.
        gb (int, optional): 利用するメモリの値(GB). Defaults to None.
        percentage (int, optional): 利用可能なメモリ総量に対して利用するメモリの割合. Defaults to 100.
        length (int, optional): メモリ不可をかける時間(秒). Defaults to 60.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: mbが不正な値
        ValueError: gbが不正な値
        ValueError: percentageが不正な値
        ValueError: targetが不正な値
    """
    if mb is not None:
        if mb < 1:
            raise ValueError("The argument 'mb' must be greater than or equal to 1")
        cmd = command.memory_stress(size=f"{mb}m", length=length)
    elif gb is not None:
        if gb < 1:
            raise ValueError("The argument 'gb' must be greater than or equal to 1")
        cmd = command.memory_stress(size=f"{gb}g", length=length)
    elif percentage:
        if percentage not in range(0, 101):
            raise ValueError("The argument 'percentage' must be between 0 and 100")
        cmd = command.memory_stress(size=f"{percentage}%", length=length)
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    __inject_command(command=cmd, target=target)


@beartype
def inject_disk_stress(
    dir: str = "/tmp",
    workers: int = 1,
    block_size: int = 64,
    volume_percentage: int = 100,
    length: int = 60,
    target: Dict[str, str] = None,
):
    """ターゲットのディスクに負荷をかける

    引数からディスク負荷をかけるコマンドを作成し,ターゲットのサーバ上で実行する

    Args:
        dir (str, optional): 負荷をかけるルートディレクトリ. Defaults to "/tmp".
        workers (int, optional): 同時にディスク書き込みを行うワーカー数. Defaults to 1.
        block_size (int, optional): 一度に書き込みを行うKB数. Defaults to 64.
        volume_percentage (int, optional): 書き込みで埋めるディスク容量の割合. Defaults to 100.
        length (int, optional): ディスク負荷をかける時間(秒). Defaults to 60.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: 引数が不正な場合
    """
    if workers < 1:
        raise ValueError("The argument 'workers' must be greater than or equal to 1")
    if block_size < 1:
        raise ValueError("The argument 'block_size' must be greater than or equal to 1")
    if volume_percentage not in range(1, 101):
        raise ValueError("The argument 'volume_percentage' must be between 1 and 100")
    cmd = command.disk_stress(
        dir=dir,
        workers=workers,
        block_size=block_size,
        volume_percentage=volume_percentage,
        length=length,
    )
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    __inject_command(command=cmd, target=target)


@beartype
def inject_io_stress(
    dir: str = "/tmp",
    workers: int = 1,
    mode: str = "rw",
    block_size: int = 4,
    block_count: int = 1,
    length: int = 60,
    target: Dict[str, str] = None,
):
    """ファイルシステムに対してI/O負荷をかける

    引数からI/O負荷をかけるコマンドを作成し,ターゲットのサーバ上で実行する.

    Args:
        dir (str, optional): 負荷をかけるルートディレクトリ. Defaults to "/tmp".
        workers (int, optional): 同時にIO負荷をかけるワーカー数. Defaults to 1.
        mode (str, optional): r,w,rwのいずれかを指定. Defaults to "rw".
        block_size (int, optional): 一度にread/writeをおこなうKB数. Defaults to 4.
        block_count (int, optional): ワーカーによってread/writeされるブロック数. Defaults to 1.
        length (int, optional): IO負荷をかける時間(秒). Defaults to 60.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: 引数が不正な場合
    """
    if workers < 1:
        raise ValueError("The argument 'workers' must be greater than or equal to 1")
    try:
        mode = IOMode[mode]
    except KeyError as key:
        msg = (
            f"Invalid input: {key}."
            f" The argument 'mode' must be chosen between {[s.name for s in IOMode]}."
        )
        raise ValueError(msg)
    if block_size < 1:
        raise ValueError("The argument 'block_size' must be greater than or equal to 1")
    if block_count < 1:
        raise ValueError(
            "The argument 'block_count' must be greater than or equal to 1"
        )

    cmd = command.io_stress(
        dir=dir,
        workers=workers,
        mode=mode,
        block_size=block_size,
        block_count=block_count,
        length=length,
    )
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    __inject_command(command=cmd, target=target)


@beartype
def inject_os_shutdown(
    delay: int = 1,
    reboot: bool = True,
    target: Dict[str, str] = None,
):
    """OSシャットダウンをおこなう

    引数からOSシャットダウンコマンドを作成し,ターゲットのサーバ上で実行する.

    Args:
        delay (int, optional): シャットダウンを行うまでの遅延時間(分). Defaults to 1.
        reboot (bool, optional): シャットダウン後に再起動をおこなうかを示すフラグ. Defaults to True.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: 引数が不正な場合
    """
    if delay < 0:
        raise ValueError("The argument 'delay' must be greater than or equal to 0")
    cmd = command.os_shutdown(delay=delay, reboot=reboot)
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    __inject_command(command=cmd, target=target)


@beartype
def inject_time_travel(
    disable_ntp: bool = False,
    offset: int = 86400,
    target: Dict[str, str] = None,
):
    """時刻変更をおこなう

    引数から時刻変更をおこなうコマンドを作成し,ターゲットのサーバ上で実行する.

    Args:
        disable_ntp (bool, optional): Trueが設定された場合, NTPが使用する宛先ポート123への通信をすべてブロックする. Default to False.
        offset (int, optional): 現在時刻から何秒時間を変更するかを指定する.値がマイナスの場合は過去にさかのぼる. Defaults to 86400.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: 引数が不正な場合
    """
    cmd_lst = [command.time_travel(offset=offset)]
    if disable_ntp:
        cmd_lst.insert(0, "sudo iptables -A OUTPUT -p udp --dport 123 -j DROP")
    print(cmd_lst)
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    __inject_commands(command_lst=cmd_lst, target=target)


@beartype
def rollback_time_travel(enable_ntp: bool = False, target: Dict[str, str] = None):
    """時刻変更をもとに戻す

    Args:
        enable_ntp (bool, optional): Trueが設定された場合, NTPが使用する宛先ポート123への通信をブロックする設定を解除する. Default to False.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: 引数が不正な場合
    """
    cmd_lst = ["sudo chronyc -a makestep"]
    if enable_ntp:
        cmd_lst.insert(0, "sudo iptables -D OUTPUT -p udp --dport 123 -j DROP")
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    __inject_commands(command_lst=cmd_lst, target=target)


@beartype
def inject_process_kill(
    pid_lst: List[int],
    signal: str = "KILL",
    interval: Union[int, float] = 0,
    kill_children: bool = False,
    length: Union[int, float] = -1,
    target: Dict[str, str] = None,
):
    """指定されたPIDのプロセスを終了させる

    引数からプロセスを終了させるコマンドを作成し,ターゲットのサーバ上で実行する

    Args:
        pid_lst (List[int]): 終了させたいプロセスのPIDのリスト.
        signal (str, optional): プロセスに送るシグナル. Defaults to "KILL".
        interval (Union[int, float], optional): プロセスキルを実行する前の遅延時間(秒). Defaults to 0.
        kill_children (bool, optional): プロセスの子プロセスも終了させるかどうかの設定. Defaults to False.
        length (Union[int, float], optional): 障害シミュレーションの長さ(秒). 値を指定しない場合はプロセスキルは1度だけ実行される. Defaults to -1.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: 引数のpid_lstが空の場合
        ValueError: 引数のtarget内にSSH接続に必要な情報が設定されていなかった場合
        ValueError: 引数のsignalがsrc.signal_.Signalで定義されていないものの場合
    """
    if not pid_lst:
        raise ValueError("The argument 'pid_lst' must not be empty.")
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    try:
        signal = Signal(signal)
    except ValueError as error:
        raise ValueError(
            f"{error}. The argument 'signal' must be chosen between {[s.value for s in Signal]}."
        )
    cmd_lst = [command.kill(signal=signal, pid_lst=pid_lst)]
    if kill_children:
        cmd_lst.insert(0, command.kill_children_by_pid(signal=signal, pid_lst=pid_lst))
    start_time = time.time()
    while True:
        time.sleep(interval)
        __inject_commands(target=target, command_lst=cmd_lst)
        if time.time() - start_time > length:
            break


@beartype
def inject_process_pkill(
    process_name_lst: List[str],
    signal: str = "KILL",
    interval: Union[int, float] = 0,
    group: str = None,
    user: str = None,
    newest: bool = False,
    oldest: bool = False,
    exact: bool = False,
    kill_children: bool = False,
    full_match: bool = False,
    length: Union[int, float] = -1,
    target: Dict[str, str] = None,
):
    """指定されたプロセス名のプロセスを終了させる

    引数からプロセスを終了させるコマンドを作成し,ターゲットのサーバ上で実行する

    Args:
        process_name_lst (List[str]): 終了させたいプロセス名のリスト. exactオプションを利用しない場合は部分一致のプロセス名も終了の対象になる.
        signal (str, optional): プロセスに送るシグナル. Defaults to "KILL".
        interval (Union[int, float], optional): プロセスキルを実行する前の遅延時間(秒). Defaults to 0.
        group (str, optional): マッチさせるプロセスをグループ名で絞る場合に設定. Defaults to None.
        user (str, optional): マッチさせるプロセスをユーザ名で絞る場合に設定. Defaults to None.
        newest (bool, optional): Trueの場合はマッチした最新のプロセスのみ終了させる. Defaults to False.
        oldest (bool, optional): Trueの場合はマッチした最古のプロセスのみ終了させる. Defaults to False.
        exact (bool, optional): Trueの場合はプロセス名が完全一致したプロセスのみマッチさせる. Defaults to False.
        kill_children (bool, optional): プロセスの子プロセスも終了させるかどうかの設定. Defaults to False.
        full_match (bool, optional): Trueの場合はプロセス名だけでなくコマンドライン全体に対してマッチさせる. Defaults to False.
        length (Union[int, float], optional): 障害シミュレーションの長さ(秒). 値を指定しない場合はプロセスキルは1度だけ実行される. Defaults to -1.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: 引数のprocess_name_lstが空の場合
        ValueError: newestとoldestが同時にTrueだった場合
        ValueError: 引数のtarget内にSSH接続に必要な情報が設定されていなかった場合
        ValueError: 引数のsignalがsrc.signal_.Signalで定義されていないものの場合

    """
    if not process_name_lst:
        raise ValueError("The argument 'process_name_lst' must not be empty.")
    if newest and oldest:
        raise ValueError("'newest' flag cannot be used with 'oldest' flag.")
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    try:
        signal = Signal(signal)
    except ValueError as error:
        raise ValueError(
            f"{error}. The argument 'signal' must be chosen between {[s.value for s in Signal]}."
        )
    cmd_lst = command.pkill(
        signal=signal,
        process_name_lst=process_name_lst,
        group=group,
        user=user,
        newest=newest,
        oldest=oldest,
        exact=exact,
        full_match=full_match,
        kill_children=kill_children,
    )
    start_time = time.time()
    while True:
        time.sleep(interval)
        __inject_commands(target=target, command_lst=cmd_lst)
        if time.time() - start_time > length:
            break


@beartype
def inject_traffic_control(params: Dict, target: Dict[str, str] = None):
    """ネットワークの遅延やパケットロスをシミュレーションする

    Args:
        params (Dict): ネットワーク遅延やパケットロスの設定をおこなうためのパラメータ群. 以下のdeviceとtcをキーとして設定できる. 詳細はtc_schema.pyを参照.
         - device (str, optional): 対象のネットワークデバイス名. Defaults to eth0.
         - tc (List): シミュレーション設定のリスト.リストの要素は以下のキーを含む．
           - destination_ip_addresses (List[str], optional): 設定したIPアドレスにのみ影響を与える. 指定がない場合はすべてのIPアドレスへの送信トラフィックに影響を与える. Defaults to [].
           - destination_ports (List[str], optional): 設定した宛先ポートへのトラフィックのみ影響を与える. 指定がない場合はすべての宛先ポートに対する送信トラフィックに影響を与える. Defaults to [].
           - source_ports (List[str], optional): 設定した送信ポートからのトラフィックのみ影響を与える. 指定がない場合はすべての送信ポートからのトラフィックに影響を与える. Defaults to [].
           - latency (int, optional): 設定した値分だけ遅延を発生させる. 単位はms. 値の設定がない場合は遅延は設定されない. Defaults to None.
           - loss (float, optional): パケットをロスさせる割合. 単位は%. 値の設定がない場合はパケットロスは設定されない. Defaults to None.
           - corrupt (bool, optional): Trueの場合パケットロスの代わりに指定した割合のパケット破損を発生させる. Defaults to False.
           - protocol (List[str], optional): 指定したプロトコル(tcp, udp, icmp)の通信に対してのみ影響を与える. 何も指定がない場合はすべてのプロトコル(tcp, udp, icmp)に対して影響を与える. Defaults to ["tcp", "udp", "icmp"].

        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: 引数が不正な場合
    """
    v = tc_schema.validator
    if not v.validate(params):
        raise ValueError(f"Validate arguments is failed: {v.errors}")
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    params = v.normalized(params)
    device = params["device"]
    tc_lst = params["tc"]

    # add the root qdisc and the default class
    cmd_lst = [
        f"sudo tc qdisc add dev {device} handle 10: root htb default 1",
        f"sudo tc class add dev {device} parent 10: classid 10:1 htb rate 1000000kbit",
    ]

    # add network emulator rules
    for i, tc in enumerate(tc_lst):
        id = f"10:{10 + i}"
        cmd_lst.append(
            f"sudo tc class add dev {device} parent 10: classid {id} htb rate 1000000kbit"
        )

        netem_cmd = (
            f"sudo tc qdisc add dev {device} parent {id} handle {100 + i}: netem"
        )
        latency = tc["latency"]
        if latency and latency > 0:
            netem_cmd += f" delay {latency}ms"
        loss = tc["loss"]
        corrupt_flag = tc["corrupt"]
        if loss and loss > 0:
            netem_cmd += f" {'corrupt' if corrupt_flag else 'loss'} {loss}%"
        cmd_lst.append(netem_cmd)

        rules = __generate_traffic_control_rules(
            IptablesAction.Append,
            tc,
            id,
        )
        cmd_lst.extend(rules)
    __inject_commands(target=target, command_lst=cmd_lst)


@beartype
def rollback_traffic_control(params: Dict, target: Dict[str, str] = None):
    """ネットワークの遅延やパケットロスをシミュレーションするための設定を削除する

    Args:
        params (Dict): ネットワーク遅延やパケットロスの設定をおこなうためのパラメータ群.詳細はtc_schema.pyを参照.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: 引数が不正な場合
    """
    v = tc_schema.validator
    if not v.validate(params):
        raise ValueError(f"Validate arguments is failed: {v.errors}")
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    params = v.normalized(params)
    device = params["device"]
    tc_lst = params["tc"]
    cmd_lst = []
    for i, tc in enumerate(tc_lst):
        id = f"10:{10 + i}"
        rules = __generate_traffic_control_rules(
            IptablesAction.Delete,
            tc,
            id,
        )
        cmd_lst.extend(rules)
    cmd_lst.append(f"sudo tc qdisc del dev {device} handle 10: root")
    __inject_commands(target=target, command_lst=cmd_lst)


def __generate_traffic_control_rules(
    action: IptablesAction,
    tc: Dict[str],
    id: int,
) -> List[str]:
    destination_ip_addresses = tc["destination_ip_addresses"]
    destination_ports = tc["destination_ports"]
    source_ports = tc["source_ports"]
    tcp = "tcp" in tc["protocol"]
    udp = "udp" in tc["protocol"]
    icmp = "icmp" in tc["protocol"]
    dport = (
        f" --match multiport --dports {','.join(destination_ports)}"
        if destination_ports
        else ""
    )
    sport = (
        f" --match multiport --sports {','.join(source_ports)}" if source_ports else ""
    )
    rules = []
    protocol_lst = []
    if tcp:
        protocol_lst.append("tcp")
    if udp:
        protocol_lst.append("udp")
    if icmp:
        protocol_lst.append("icmp")
    cmd_template = f"sudo iptables -{action.value} POSTROUTING -t mangle -j CLASSIFY --set-class {id} -p {{proto}}"
    for proto in protocol_lst:
        if proto == "icmp":
            rules.append(cmd_template.format(proto=proto))
            continue
        rules.append(cmd_template.format(proto=proto) + dport + sport)

    if destination_ip_addresses:
        ip_rules = []
        for ip_addr in destination_ip_addresses:
            dest = f" -d {ip_addr}"
            ip_rules.extend(map(lambda rule: rule + dest, rules))
        rules = ip_rules
    return rules


@beartype
def inject_traffic_block(
    destination_ip_addresses: List[str] = None,
    device: str = "eth0",
    destination_ports: List[str] = None,
    source_ports: List[str] = None,
    tcp: bool = True,
    udp: bool = True,
    icmp: bool = True,
    target: Dict[str, str] = None,
):
    """引数で指定した送信トラフィックをすべてドロップさせる

    Args:
        destination_ip_addresses (List[str], optional): 指定したIPアドレスへのトラフィックにのみ影響する. 指定しない場合はすべてのIPアドレスへの送信トラフィックに影響を与える. Defaults to None.
        device (str, optional): 影響を与えるネットワークインターフェース. Defaults to "eth0".
        destination_ports (List[str], optional): 指定した宛先ポートへのトラフィックにのみ影響する. 指定がない場合はすべての宛先ポートに対する送信トラフィックに影響を与える. Defaults to None.
        source_ports (List[str], optional): 指定した送信元ポートからのトラフィックにのみ影響する. 指定がない場合はすべての送信ポートからのトラフィックに影響を与える. Defaults to None.
        tcp (bool, optional): tcpプロトコルの通信を対象にするかの判定. Defaults to True.
        udp (bool, optional): udpプロトコルの通信を対象にするかの判定. Defaults to True.
        icmp (bool, optional): icmpプロトコルの通信を対象にするかの判定. Defaults to True.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.

    Raises:
        ValueError: 引数が不正な場合
    """
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    rules = __generate_traffic_block_rules(
        IptablesAction.Append,
        destination_ip_addresses,
        device,
        destination_ports,
        source_ports,
        tcp,
        udp,
        icmp,
    )
    __inject_commands(target=target, command_lst=rules)


@beartype
def rollback_traffic_block(
    destination_ip_addresses: List[str] = None,
    device: str = "eth0",
    destination_ports: List[str] = None,
    source_ports: List[str] = None,
    tcp: bool = True,
    udp: bool = True,
    icmp: bool = True,
    target: Dict[str, str] = None,
):
    """送信トラフィックをブロックする設定を取り除く

    Args:
        destination_ip_addresses (List[str], optional): 対象となるIPアドレス. Defaults to None.
        device (str, optional): 対象となるネットワークインターフェース. Defaults to "eth0".
        destination_ports (List[str], optional): 対象となる宛先ポート. Defaults to None.
        source_ports (List[str], optional): 対象となる送信元ポート. Defaults to None.
        tcp (bool, optional): tcpプロトコルを対象とする場合はTrue. Defaults to True.
        udp (bool, optional): udpプロトコルを対象とする場合はTrue. Defaults to True.
        icmp (bool, optional): icmpプロトコルを対象とする場合はTrue. Defaults to True.
        target (Dict[str, str], optional): SSHに必要なホスト名,ユーザ名と鍵のパス.
    Raises:
        ValueError: 引数が不正な場合
    """
    try:
        target = Target.from_(target)
    except KeyError as key:
        raise ValueError(f"{key} is not found in target.")
    rules = __generate_traffic_block_rules(
        IptablesAction.Delete,
        destination_ip_addresses,
        device,
        destination_ports,
        source_ports,
        tcp,
        udp,
        icmp,
    )
    __inject_commands(target=target, command_lst=rules)


def __generate_traffic_block_rules(
    action: IptablesAction,
    destination_ip_addresses: List[str],
    device: str,
    destination_ports: List[str],
    source_ports: List[str],
    tcp: bool,
    udp: bool,
    icmp: bool,
) -> List[str]:
    rules = []
    dport = (
        f" --match multiport --dports {','.join(destination_ports)}"
        if destination_ports
        else ""
    )
    sport = (
        f" --match multiport --sports {','.join(source_ports)}" if source_ports else ""
    )
    base_cmd = f"sudo iptables -{action.value} OUTPUT -o {device} -p {{proto}}"
    protocols = []
    if tcp:
        protocols.append("tcp")
    if udp:
        protocols.append("udp")
    if icmp:
        protocols.append("icmp")
    for proto in protocols:
        if proto == "icmp":
            rules.append(base_cmd.format(proto=proto))
            continue
        rules.append(base_cmd.format(proto=proto) + dport + sport)

    if destination_ip_addresses:
        ip_rules = []
        for ip_addr in destination_ip_addresses:
            ip_rules.extend(map(lambda rule: rule + f" -d {ip_addr}", rules))
        rules = ip_rules

    rules = map(lambda cmd: cmd + " -j DROP", rules)
    return rules


def __inject_command(target: Target, command: str):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=target.hostname,
            username=target.username,
            key_filename=target.key_filename,
        )

        _, stdout, stderr = ssh.exec_command(command)

        for out in stdout:
            print("[out]", out, end="")
        for err in stderr:
            print("[err]", err, end="")

        del stdout, stderr


def __inject_commands(target: Target, command_lst: List[str]):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=target.hostname,
            username=target.username,
            key_filename=target.key_filename,
        )
        for cmd in command_lst:
            _, stdout, stderr = ssh.exec_command(cmd)
            for out in stdout:
                print("[out]", out, end="")
            for err in stderr:
                print("[err]", err, end="")
            del stdout, stderr

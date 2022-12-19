# 利用可能な関数

すべての機能で共通して以下の引数`target`を設定する必要があります。

```json
"target": {
    "hostname": "str",
    "username": "str",
    "key_filename": "str"
}
```

- `hostname`: 障害をシミュレーションするホスト名
- `username`: 障害をシミュレーションするサーバへSSH接続するユーザ名
- `key_filename`: 障害をシミュレーションするサーバへSSH接続するために必要な鍵のパス

## inject_cpu_stress

ターゲットのcpuに負荷をかける

Args:

- cores (int, optional): 利用するコア数。デフォルトは1。
- percent (int, optional): 各コアのcpu利用率。デフォルトは100。
- length (int, optional): cpu負荷をかける時間。単位は秒。デフォルトは60。

## inject_memory_stress

ターゲットのメモリに負荷をかける

Args:

- mb (int, optional): 利用するメモリの値 (MB)。デフォルトはNone。
- gb (int, optional): 利用するメモリの値 (GB)。デフォルトはNone。
- percentage (int, optional): 利用可能なメモリ総量に対して利用するメモリの割合。デフォルトは100。
- length (int, optional): メモリ不可をかける時間。単位は秒。デフォルトは60。

## inject_disk_stress

ターゲットのディスクに負荷をかける

Args:

- dir (str, optional): 負荷をかけるルートディレクトリ。デフォルトは"/tmp"。
- workers (int, optional): 同時にディスク書き込みを行うワーカー数。デフォルトは1。
- block_size (int, optional): 一度に書き込みを行うKB数。デフォルトは64。
- volume_percentage (int, optional): 書き込みで埋めるディスク容量の割合。デフォルトは100。
- length (int, optional): ディスク負荷をかける時間。単位は秒。デフォルトは60。

## inject_io_stress

ターゲットのファイルシステムに対してI/O負荷をかける

Args:

- dir (str, optional): 負荷をかけるルートディレクトリ。デフォルトは"/tmp"。
- workers (int, optional): 同時にIO負荷をかけるワーカー数。デフォルトは1。
- mode (str, optional): r,w,rwのいずれかを指定。デフォルトは"rw"。
- block_size (int, optional): 一度にread/writeをおこなうKB数。デフォルトは4。
- block_count (int, optional): ワーカーによってread/writeされるブロック数。デフォルトは1。
- length (int, optional): IO負荷をかける時間。単位は秒。デフォルトは60。

## inject_os_shutdown

ターゲットのOSシャットダウンをおこなう

Args:

- delay (int, optional): シャットダウンを行うまでの遅延時間。単位は分。デフォルトは1。
- reboot (bool, optional): シャットダウン後に再起動をおこなうかを示すフラグ。デフォルトはTrue。

## inject_time_travel

ターゲットの時刻変更をおこなう

Args:

- disable_ntp (bool, optional): Trueが設定された場合、NTPが使用する宛先ポート123への通信をすべてブロックする。 デフォルトはFalse。
- offset (int, optional): 現在時刻から何秒時間を変更するかを指定する。値がマイナスの場合は過去にさかのぼる。デフォルトは86400。

## rollback_time_travel

ターゲットの時刻変更をもとに戻す

Args:

- enable_ntp (bool, optional): Trueが設定された場合、NTPが使用する宛先ポート123への通信をブロックする設定を解除する。 デフォルトはFalse。

## inject_process_kill

ターゲットのサーバ上で指定されたPIDのプロセスを終了させる

Args:

- pid_lst (List[int]): 終了させたいプロセスのPIDのリスト。
- signal (str, optional): プロセスに送るシグナル。デフォルトは"KILL"。
- interval (Union[int, float], optional): プロセスキルを実行する前の遅延時間。単位は秒。デフォルトは0。
- kill_children (bool, optional): プロセスの子プロセスも終了させるかどうかの設定。デフォルトはFalse。
- length (Union[int, float], optional): 障害シミュレーションの長さ。単位は秒。値の指定がない場合、プロセスキルは1度だけ実行される。デフォルトは -1。

## inject_process_pkill

ターゲットのサーバ上で指定されたプロセス名のプロセスを終了させる

Args:

- process_name_lst (List[str]): 終了させたいプロセス名のリスト。exactオプションを利用しない場合は部分一致のプロセス名も終了の対象になる。
- signal (str, optional): プロセスに送るシグナル。デフォルトは"KILL"。
- interval (Union[int, float], optional): プロセスキルを実行する前の遅延時間。単位は秒。デフォルトは0。
- group (str, optional): マッチさせるプロセスをグループ名で絞る場合に設定。デフォルトはNone。
- user (str, optional): マッチさせるプロセスをユーザ名で絞る場合に設定。デフォルトはNone。
- newest (bool, optional): Trueの場合はマッチした最新のプロセスのみ終了させる。デフォルトはFalse。
- oldest (bool, optional): Trueの場合はマッチした最古のプロセスのみ終了させる。デフォルトはFalse。
- exact (bool, optional): Trueの場合はプロセス名が完全一致したプロセスのみマッチさせる。デフォルトはFalse。
- kill_children (bool, optional): プロセスの子プロセスも終了させるかどうかの設定。デフォルトはFalse。
- full_match (bool, optional): Trueの場合はプロセス名だけでなくコマンドライン全体に対してマッチさせる。デフォルトはFalse。
- length (Union[int, float], optional): 障害シミュレーションの長さ。単位は秒。値の指定がない場合、プロセスキルは1度だけ実行される。デフォルトは -1。

## inject_traffic_control

ネットワークの遅延やパケットロスをシミュレーションする。送信トラフィックに対してのみ影響を与える。

 Args:

- params (Dict): ネットワーク遅延やパケットロスの設定をおこなうためのパラメーター群。以下のdeviceとtcをキーとして設定できる。
  - device (str, optional): 対象のネットワークデバイス名。デフォルトはeth0。
  - tc (List): シミュレーション設定のリスト。リストの要素は以下のキーを含む。
    - destination_ip_addresses (List[str], optional): 設定したIPアドレスにのみ影響を与える。指定がない場合はすべてのIPアドレスへの送信トラフィックに影響を与える。デフォルトは[]。
    - destination_ports (List[str], optional): 設定した宛先ポートへのトラフィックのみ影響を与える。指定がない場合はすべての宛先ポートに対する送信トラフィックに影響を与える。デフォルトは[]。
    - source_ports (List[str], optional): 設定した送信ポートからのトラフィックのみ影響を与える。指定がない場合はすべての送信ポートからのトラフィックに影響を与える。デフォルトは[]。
    - latency (int, optional): 設定した値分だけ遅延を発生させる。単位はms。値の設定がない場合、遅延は設定されない。デフォルトはNone。
    - loss (float, optional): パケットをロスさせる割合。単位は%。値の設定がない場合、パケットロスは設定されない。デフォルトはNone。
    - corrupt (bool, optional): Trueの場合パケットロスの代わりに指定した割合のパケット破損を発生させる。デフォルトはFalse。
    - protocol (List[str], optional): 指定したプロトコル (tcp, udp, icmp) の通信に対してのみ影響を与える。何も指定がない場合はすべてのプロトコル (tcp, udp, icmp) に対して影響を与える。デフォルトは["tcp", "udp", "icmp"]。

## rollback_traffic_control

ネットワークの遅延やパケットロスをシミュレーションするための設定を削除する。
inject_traffic_controlに渡した引数と同じものを渡すことで、inject_traffic_controlで設定した変更をロールバックすることができる。

Args:

inject_traffic_controlと同様

## inject_traffic_block

引数で指定した送信トラフィックをすべてドロップさせる

Args:

- destination_ip_addresses (List[str], optional): 指定したIPアドレスへのトラフィックにのみ影響する。指定しない場合はすべてのIPアドレスへの送信トラフィックに影響を与える。デフォルトはNone。
- device (str, optional): 影響を与えるネットワークインタフェース。デフォルトは"eth0"。
- destination_ports (List[str], optional): 指定した宛先ポートへのトラフィックにのみ影響する。指定がない場合はすべての宛先ポートに対する送信トラフィックに影響を与える。デフォルトはNone。
- source_ports (List[str], optional): 指定した送信元ポートからのトラフィックにのみ影響する。指定がない場合はすべての送信ポートからのトラフィックに影響を与える。デフォルトはNone。
- tcp (bool, optional): tcpプロトコルの通信を対象にするかの判定。デフォルトはTrue。
- udp (bool, optional): udpプロトコルの通信を対象にするかの判定。デフォルトはTrue。
- icmp (bool, optional): icmpプロトコルの通信を対象にするかの判定。デフォルトはTrue。

## rollback_traffic_block

inject_traffic_blockに渡した引数と同じものを渡すことで、inject_traffic_blockで設定した変更をロールバックすることができる。

Args:

inject_traffic_blockと同様

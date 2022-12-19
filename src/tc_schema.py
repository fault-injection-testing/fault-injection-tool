from cerberus import Validator

"""inject_traffic_control関数のパラメータ群のバリデーションと正規化をおこなうためのschema

__root_schema:
    device (str, optional): 対象のネットワークデバイス名. Defaults to eth0.
    tc (List): シミュレーション設定のリスト. 各要素のスキーマは__tc_schemaで定義.

__tc_schema:
    destination_ip_addresses (List[str], optional): 設定したIPアドレスにのみ影響を与える. 指定がない場合はすべてのIPアドレスへの送信トラフィックに影響を与える. Defaults to [].
    destination_ports (List[str], optional): 設定した宛先ポートへのトラフィックのみ影響を与える. 指定がない場合はすべての宛先ポートに対する送信トラフィックに影響を与える. Defaults to [].
    source_ports (List[str], optional): 設定した送信ポートからのトラフィックのみ影響を与える. 指定がない場合はすべての送信ポートからのトラフィックに影響を与える. Defaults to [].
    latency (int, optional): 設定した値分だけ遅延を発生させる.単位はms. 値の設定がない場合は遅延は設定されない. Defaults to None.
    loss (float, optional): パケットをロスさせる割合. 単位は%. 値の設定がない場合はパケットロスは設定されない. Defaults to None.
    corrupt (bool, optional): Trueの場合パケットロスの代わりに指定した割合のパケット破損を発生させる. Defaults to False.
    protocol (List[str], optional): 指定したプロトコル(tcp, udp, icmp)の通信に対してのみ影響を与える. 何も指定がない場合はすべてのプロトコル(tcp, udp, icmp)に対して影響を与える. Defaults to ["tcp", "udp", "icmp"].
"""

__tc_schema = {
    "destination_ip_addresses": {
        "type": "list",
        "schema": {"type": "string"},
        "default": [],
    },
    "destination_ports": {"type": "list", "schema": {"type": "string"}, "default": []},
    "source_ports": {"type": "list", "schema": {"type": "string"}, "default": []},
    "latency": {"type": "integer", "nullable": True, "default": None},
    "loss": {"type": "float", "max": 100, "nullable": True, "default": None},
    "corrupt": {"type": "boolean", "default": False},
    "protocol": {
        "type": "list",
        "empty": False,
        "allowed": ["tcp", "udp", "icmp"],
        "default": ["tcp", "udp", "icmp"],
    },
}


__root_schema = {
    "device": {"type": "string", "default": "eth0"},
    "tc": {
        "type": "list",
        "empty": False,
        "schema": {"type": "dict", "schema": __tc_schema},
    },
}

validator = Validator(__root_schema)

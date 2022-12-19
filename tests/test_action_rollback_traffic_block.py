from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture

from src.action import rollback_traffic_block
from tests.conftest import mock_ssh_client, target


@pytest.mark.parametrize(
    argnames="args,expected",
    argvalues=[
        # 0:何もパラメータを指定しない場合
        (
            {},
            [
                "sudo iptables -D OUTPUT -o eth0 -p tcp -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p udp -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -j DROP",
            ],
        ),
        # 1: 任意のデバイスを指定可能
        (
            {"device": "ens33"},
            [
                "sudo iptables -D OUTPUT -o ens33 -p tcp -j DROP",
                "sudo iptables -D OUTPUT -o ens33 -p udp -j DROP",
                "sudo iptables -D OUTPUT -o ens33 -p icmp -j DROP",
            ],
        ),
        # 2: 宛先ポートを1つ指定
        (
            {"destination_ports": ["80"]},
            [
                "sudo iptables -D OUTPUT -o eth0 -p tcp --match multiport --dports 80 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p udp --match multiport --dports 80 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -j DROP",
            ],
        ),
        # 3: 宛先ポートを複数指定
        (
            {"destination_ports": ["80", "22"]},
            [
                "sudo iptables -D OUTPUT -o eth0 -p tcp --match multiport --dports 80,22 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p udp --match multiport --dports 80,22 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -j DROP",
            ],
        ),
        # 4: 送信元ポートを1つ指定
        (
            {"source_ports": ["80"]},
            [
                "sudo iptables -D OUTPUT -o eth0 -p tcp --match multiport --sports 80 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p udp --match multiport --sports 80 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -j DROP",
            ],
        ),
        # 5: 送信元ポートを複数指定
        (
            {"source_ports": ["80", "22"]},
            [
                "sudo iptables -D OUTPUT -o eth0 -p tcp --match multiport --sports 80,22 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p udp --match multiport --sports 80,22 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -j DROP",
            ],
        ),
        # 6: 宛先ポートと送信元ポートを指定
        (
            {"destination_ports": ["80"], "source_ports": ["80", "22"]},
            [
                "sudo iptables -D OUTPUT -o eth0 -p tcp --match multiport --dports 80 --match multiport --sports 80,22 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p udp --match multiport --dports 80 --match multiport --sports 80,22 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -j DROP",
            ],
        ),
        # 7: ipアドレスを1つ指定
        (
            {"destination_ip_addresses": ["8.8.8.8"]},
            [
                "sudo iptables -D OUTPUT -o eth0 -p tcp -d 8.8.8.8 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p udp -d 8.8.8.8 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -d 8.8.8.8 -j DROP",
            ],
        ),
        # 8: ipアドレスを複数指定
        (
            {"destination_ip_addresses": ["8.8.8.8", "4.4.4.4"]},
            [
                "sudo iptables -D OUTPUT -o eth0 -p tcp -d 8.8.8.8 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p udp -d 8.8.8.8 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -d 8.8.8.8 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p tcp -d 4.4.4.4 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p udp -d 4.4.4.4 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -d 4.4.4.4 -j DROP",
            ],
        ),
        # 9: 特定プロトコルを除外
        (
            {"destination_ip_addresses": ["8.8.8.8"], "tcp": False},
            [
                "sudo iptables -D OUTPUT -o eth0 -p udp -d 8.8.8.8 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -d 8.8.8.8 -j DROP",
            ],
        ),
        # 10: 宛先ポートと送信元ポートを指定
        (
            {
                "destination_ip_addresses": ["8.8.8.8", "4.4.4.4"],
                "destination_ports": ["80", "22"],
                "source_ports": ["23"],
                "udp": False,
            },
            [
                "sudo iptables -D OUTPUT -o eth0 -p tcp --match multiport --dports 80,22 --match multiport --sports 23 -d 8.8.8.8 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -d 8.8.8.8 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p tcp --match multiport --dports 80,22 --match multiport --sports 23 -d 4.4.4.4 -j DROP",
                "sudo iptables -D OUTPUT -o eth0 -p icmp -d 4.4.4.4 -j DROP",
            ],
        ),
    ],
)
def test_inject_traffic_block_should_call_exec_command_with_iptables(
    target: target,
    mocker: MockerFixture,
    mock_ssh_client: mock_ssh_client,
    args,
    expected,
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    rollback_traffic_block(**args, target=target)
    spy_exec_command.assert_has_calls(
        list(map(lambda cmd: mocker.call(ANY, cmd), expected))
    )
    assert spy_exec_command.call_count == len(expected)


def test_inject_traffic_block_should_throw_ValueError_when_the_argument_target_is_invalid():
    invalid_target = {
        "hostname": "localhost",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        rollback_traffic_block(target=invalid_target)
    assert str(error_info.value) == "'username' is not found in target."

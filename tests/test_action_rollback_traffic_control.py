from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture

from src.action import rollback_traffic_control
from tests.conftest import mock_ssh_client, target


@pytest.mark.parametrize(
    argnames="input,expected",
    argvalues=[
        # 0:すべての通信に遅延をかける設定を削除
        (
            {"tc": [{"latency": 100}]},
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 1:すべての通信にパケットロスを発生させる設定を削除
        (
            {"tc": [{"loss": 0.1}]},
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 2:すべての通信にパケット破壊を発生させる設定を削除
        (
            {"tc": [{"loss": 0.5, "corrupt": True}]},
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 3:すべての通信に遅延とパケットロスを同時に発生させる設定を削除
        (
            {"tc": [{"latency": 100, "loss": 0.1}]},
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 4:特定のプロトコルに対して設定した変更を削除
        (
            {
                "tc": [
                    {
                        "latency": 100,
                        "loss": 0.1,
                        "protocol": ["tcp"],
                    }
                ]
            },
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 5:特定の1つの宛先ポートに対して設定した変更を削除
        (
            {"tc": [{"latency": 100, "destination_ports": ["80"]}]},
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp --match multiport --dports 80",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp --match multiport --dports 80",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 6:複数の宛先ポートに対しての設定した変更を削除
        (
            {"tc": [{"latency": 100, "destination_ports": ["80", "22"]}]},
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp --match multiport --dports 80,22",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp --match multiport --dports 80,22",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 7:特定の1つの送信元ポートに対して設定した変更を削除
        (
            {"tc": [{"latency": 100, "source_ports": ["80"]}]},
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp --match multiport --sports 80",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp --match multiport --sports 80",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 8:複数の送信元ポートに対して設定した変更を削除
        (
            {"tc": [{"latency": 100, "source_ports": ["80", "22"]}]},
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp --match multiport --sports 80,22",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp --match multiport --sports 80,22",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 9:宛先ポートと送信元ポートの両方を指定した変更を削除
        (
            {
                "tc": [
                    {
                        "latency": 100,
                        "destination_ports": ["80", "22"],
                        "source_ports": ["80"],
                    }
                ]
            },
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp --match multiport --dports 80,22 --match multiport --sports 80",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp --match multiport --dports 80,22 --match multiport --sports 80",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 10:特定のIPアドレスに対して設定した変更を削除
        (
            {"tc": [{"latency": 100, "destination_ip_addresses": ["8.8.8.8"]}]},
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp -d 8.8.8.8",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 11:複数のIPアドレスに対して設定した変更を削除
        (
            {
                "tc": [
                    {"latency": 100, "destination_ip_addresses": ["8.8.8.8", "4.4.4.4"]}
                ]
            },
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp -d 4.4.4.4",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p udp -d 4.4.4.4",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp -d 4.4.4.4",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 12:特定のプロトコル,宛先ポートとIPアドレスに対して設定した変更を削除
        (
            {
                "tc": [
                    {
                        "latency": 100,
                        "destination_ip_addresses": ["8.8.8.8", "4.4.4.4"],
                        "destination_ports": ["80", "22"],
                        "protocol": ["tcp", "icmp"],
                    }
                ]
            },
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp --match multiport --dports 80,22 -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp --match multiport --dports 80,22 -d 4.4.4.4",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp -d 4.4.4.4",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 13:複数の変更を削除
        (
            {
                "tc": [
                    {
                        "latency": 100,
                        "destination_ip_addresses": ["4.4.4.4"],
                        "destination_ports": ["80", "22"],
                        "protocol": ["tcp", "icmp"],
                    },
                    {
                        "loss": 0.5,
                        "destination_ip_addresses": ["8.8.8.8"],
                        "destination_ports": ["80"],
                        "source_ports": ["80"],
                    },
                ]
            },
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp --match multiport --dports 80,22 -d 4.4.4.4",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp -d 4.4.4.4",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:11 -p tcp --match multiport --dports 80 --match multiport --sports 80 -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:11 -p udp --match multiport --dports 80 --match multiport --sports 80 -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:11 -p icmp -d 8.8.8.8",
                "sudo tc qdisc del dev eth0 handle 10: root",
            ],
        ),
        # 14:デバイスを指定して設定を削除
        (
            {
                "device": "ens33",
                "tc": [
                    {
                        "latency": 100,
                        "destination_ip_addresses": ["8.8.8.8", "4.4.4.4"],
                        "destination_ports": ["80", "22"],
                        "protocol": ["tcp", "icmp"],
                    },
                    {
                        "loss": 0.5,
                        "destination_ip_addresses": ["8.8.8.8"],
                        "destination_ports": ["80"],
                        "source_ports": ["80"],
                    },
                ],
            },
            [
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp --match multiport --dports 80,22 -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p tcp --match multiport --dports 80,22 -d 4.4.4.4",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:10 -p icmp -d 4.4.4.4",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:11 -p tcp --match multiport --dports 80 --match multiport --sports 80 -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:11 -p udp --match multiport --dports 80 --match multiport --sports 80 -d 8.8.8.8",
                "sudo iptables -D POSTROUTING -t mangle -j CLASSIFY --set-class 10:11 -p icmp -d 8.8.8.8",
                "sudo tc qdisc del dev ens33 handle 10: root",
            ],
        ),
    ],
)
def test_inject_traffic_control_should_call_exec_command_with_tc_and_iptables(
    target: target,
    mocker: MockerFixture,
    mock_ssh_client: mock_ssh_client,
    input,
    expected,
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    rollback_traffic_control(params=input, target=target)
    spy_exec_command.assert_has_calls(
        list(map(lambda cmd: mocker.call(ANY, cmd), expected))
    )
    assert spy_exec_command.call_count == len(expected)


def test_inject_traffic_control_should_throw_ValueError_when_validating_params_failed():
    invalid_params = {"tc": []}
    with pytest.raises(ValueError, match=r"Validate arguments is failed:.*"):
        rollback_traffic_control(params=invalid_params)


def test_inject_traffic_control_should_throw_ValueError_when_the_argument_target_is_invalid():
    params = {
        "device": "eth0",
        "tc": [
            {
                "destination_ip_addresses": ["addr1"],
                "destination_ports": ["p1"],
                "source_ports": ["p2"],
                "loss": 0.1,
            }
        ],
    }
    invalid_target = {
        "hostname": "localhost",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        rollback_traffic_control(params=params, target=invalid_target)
    assert str(error_info.value) == "'username' is not found in target."

from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture

from src.action import inject_time_travel, rollback_time_travel
from tests.conftest import mock_ssh_client, target


def test_inject_time_travel_should_call_exec_command_with_date_cmd_generated_by_default_params(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_time_travel(target=target)
    spy_exec_command.assert_called_once_with(
        ANY,
        "sudo date -s `date --date='86400 seconds' +@%s`",
    )


def test_inject_time_travel_should_call_exec_command_with_date_cmd_generated_by_arb_params(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_time_travel(offset=-86400, target=target)
    spy_exec_command.assert_called_once_with(
        ANY,
        "sudo date -s `date --date='-86400 seconds' +@%s`",
    )


def test_inject_time_travel_should_call_exec_command_with_block_ntp_port_command_when_the_argument_disable_ntp_is_True(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_time_travel(disable_ntp=True, offset=3600, target=target)
    spy_exec_command.assert_has_calls(
        [
            mocker.call(ANY, "sudo iptables -A OUTPUT -p udp --dport 123 -j DROP"),
            mocker.call(ANY, "sudo date -s `date --date='3600 seconds' +@%s`"),
        ]
    )


def test_inject_time_travel_should_throw_ValueError_when_the_argument_target_is_invalid():
    invalid_target = {
        "hostname": "localhost",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        inject_time_travel(target=invalid_target)
    assert str(error_info.value) == "'username' is not found in target."


def test_rollback_time_travel_should_call_exec_command_with_chronyc_cmd(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    rollback_time_travel(target=target)
    spy_exec_command.assert_called_once_with(
        ANY,
        "sudo chronyc -a makestep",
    )


def test_rollback_time_travel_should_call_exec_command_with_iptables_cmd_when_enable_ntp_is_True(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    rollback_time_travel(enable_ntp=True, target=target)
    spy_exec_command.assert_has_calls(
        [
            mocker.call(ANY, "sudo iptables -D OUTPUT -p udp --dport 123 -j DROP"),
            mocker.call(
                ANY,
                "sudo chronyc -a makestep",
            ),
        ]
    )


def test_rollback_time_travel_should_throw_ValueError_when_target_is_invalid():
    invalid_target = {
        "hostname": "localhost",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        rollback_time_travel(target=invalid_target)
    assert str(error_info.value) == "'username' is not found in target."

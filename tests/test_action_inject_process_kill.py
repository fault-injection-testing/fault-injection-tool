from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture

from src.action import inject_process_kill
from tests.conftest import mock_ssh_client, target


def test_inject_process_kill_should_call_exec_command_with_kill_cmd_generated_by_default_param(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_kill(pid_lst=[12345], target=target)
    spy_exec_command.assert_called_once_with(ANY, "sudo kill -KILL 12345")


def test_inject_process_kill_should_call_exec_command_multi_times_when_length_greater_than_interval(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_kill(pid_lst=[12345], target=target, interval=0, length=0.1)
    assert spy_exec_command.call_count > 1


def test_inject_process_kill_should_call_exec_command_twice_when_kill_children_flag_is_true(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_kill(pid_lst=[12345], kill_children=True, target=target)
    spy_exec_command.assert_has_calls(
        [
            mocker.call(ANY, "sudo pkill -KILL -P 12345"),
            mocker.call(ANY, "sudo kill -KILL 12345"),
        ]
    )


def test_inject_process_kill_should_throw_ValueError_when_the_argument_pid_lst_is_empty(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_process_kill(pid_lst=[], target=target)
    assert str(error_info.value) == "The argument 'pid_lst' must not be empty."


def test_inject_process_kill_should_throw_ValueError_when_the_argument_target_is_invalid():
    invalid_target = {
        "username": "user",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        inject_process_kill(pid_lst=[12345], target=invalid_target)
    assert str(error_info.value) == "'hostname' is not found in target."


def test_inject_process_kill_should_throw_ValueError_when_the_argument_signal_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_process_kill(pid_lst=[12345], signal="FOO", target=target)
    assert str(error_info.value) == (
        "'FOO' is not a valid Signal."
        " The argument 'signal' must be chosen between"
        " ['HUP', 'INT', 'QUIT', 'ILL', 'TRAP', 'ABRT', 'FPE',"
        " 'KILL', 'SEGV', 'PIPE', 'ALRM', 'TERM', 'USR1', 'USR2']."
    )

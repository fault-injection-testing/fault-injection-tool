from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture

from src.action import inject_os_shutdown
from tests.conftest import mock_ssh_client, target


def test_inject_os_shutdown_should_call_exec_command_with_shutdown_cmd_generated_by_default_params(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_os_shutdown(target=target)
    spy_exec_command.assert_called_once_with(
        ANY,
        "sudo shutdown -r +1",
    )


def test_inject_os_shutdown_should_call_exec_command_with_shutdown_cmd_generated_by_arb_params(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_os_shutdown(delay=10, reboot=False, target=target)
    spy_exec_command.assert_called_once_with(
        ANY,
        "sudo shutdown -h +10",
    )


def test_inject_os_shutdown_should_throw_ValueError_when_the_argument_delay_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_os_shutdown(delay=-1, target=target)
    assert (
        str(error_info.value)
        == "The argument 'delay' must be greater than or equal to 0"
    )


def test_inject_os_shutdown_should_throw_ValueError_when_the_argument_target_is_invalid():
    invalid_target = {
        "hostname": "localhost",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        inject_os_shutdown(target=invalid_target)
    assert str(error_info.value) == "'username' is not found in target."

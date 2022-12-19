from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture

from src.action import inject_memory_stress
from tests.conftest import mock_ssh_client, target


def test_inject_memory_stress_should_call_exec_command_with_the_memory_stress_command_by_mb(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_memory_stress(mb=256, target=target)
    spy_exec_command.assert_called_once_with(
        ANY, "stress-ng -m 1 --vm-bytes 256m -t 60"
    )


def test_inject_memory_stress_should_call_exec_command_with_the_memory_stress_command_by_gb(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_memory_stress(gb=1, target=target)
    spy_exec_command.assert_called_once_with(ANY, "stress-ng -m 1 --vm-bytes 1g -t 60")


def test_inject_memory_stress_should_call_exec_command_with_the_memory_stress_command_by_percentage(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_memory_stress(percentage=50, length=10, target=target)
    spy_exec_command.assert_called_once_with(ANY, "stress-ng -m 1 --vm-bytes 50% -t 10")


def test_inject_memory_stress_should_throw_ValueError_when_the_argument_mb_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_memory_stress(mb=0, target=target)
    assert (
        str(error_info.value) == "The argument 'mb' must be greater than or equal to 1"
    )


def test_inject_memory_stress_should_throw_ValueError_when_the_argument_gb_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_memory_stress(gb=0, target=target)
    assert (
        str(error_info.value) == "The argument 'gb' must be greater than or equal to 1"
    )


def test_inject_memory_stress_should_throw_ValueError_when_the_argument_percentage_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_memory_stress(percentage=101, target=target)
    assert (
        str(error_info.value) == "The argument 'percentage' must be between 0 and 100"
    )


def test_inject_memory_stress_should_throw_ValueError_when_the_argument_target_is_invalid():
    invalid_target = {
        "hostname": "localhost",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        inject_memory_stress(target=invalid_target)
    assert str(error_info.value) == "'username' is not found in target."

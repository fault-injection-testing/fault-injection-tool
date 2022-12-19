from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture

from src.action import inject_disk_stress
from tests.conftest import mock_ssh_client, target


def test_inject_disk_stress_should_call_exec_command_with_the_disk_stress_command(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_disk_stress(target=target)
    spy_exec_command.assert_called_once_with(
        ANY,
        "stress-ng --temp-path /tmp -d 1 --hdd-write-size 64k --hdd-bytes 100% -t 60",
    )


def test_inject_disk_stress_should_throw_ValueError_when_the_argument_worker_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_disk_stress(workers=0, target=target)
    assert (
        str(error_info.value)
        == "The argument 'workers' must be greater than or equal to 1"
    )


def test_inject_disk_stress_should_throw_ValueError_when_the_argument_block_size_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_disk_stress(block_size=0, target=target)
    assert (
        str(error_info.value)
        == "The argument 'block_size' must be greater than or equal to 1"
    )


def test_inject_disk_stress_should_throw_ValueError_when_the_argument_volume_percentage_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_disk_stress(volume_percentage=0, target=target)
    assert (
        str(error_info.value)
        == "The argument 'volume_percentage' must be between 1 and 100"
    )


def test_inject_disk_stress_should_throw_ValueError_when_the_argument_target_is_invalid():
    invalid_target = {
        "hostname": "localhost",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        inject_disk_stress(target=invalid_target)
    assert str(error_info.value) == "'username' is not found in target."

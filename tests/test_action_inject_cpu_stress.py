from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture

from src.action import inject_cpu_stress
from tests.conftest import mock_ssh_client, target


def test_inject_cpu_stress_should_call_exec_command_with_the_cpu_stress_command(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_cpu_stress(cores=1, percent=50, length=30, target=target)
    spy_exec_command.assert_called_once_with(ANY, "stress-ng -c 1 -l 50 -t 30")


def test_inject_cpu_stress_should_throw_ValueError_when_the_argument_cores_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_cpu_stress(cores=0, target=target)
    assert (
        str(error_info.value)
        == "The argument 'cores' must be greater than or equal to 1"
    )


def test_inject_cpu_stress_should_throw_ValueError_when_the_argument_percent_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_cpu_stress(percent=-1, target=target)
    assert str(error_info.value) == "The argument 'percent' must be between 0 and 100"


def test_inject_cpu_stress_should_throw_ValueError_when_the_argument_target_is_invalid():
    invalid_target = {
        "hostname": "localhost",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        inject_cpu_stress(target=invalid_target)
    assert str(error_info.value) == "'username' is not found in target."

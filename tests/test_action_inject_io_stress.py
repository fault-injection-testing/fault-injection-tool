from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture

from src.action import inject_io_stress
from tests.conftest import mock_ssh_client, target


def test_inject_io_stress_should_call_exec_command_with_the_fio_command_generated_by_default_params(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_io_stress(target=target)
    spy_exec_command.assert_called_once_with(
        ANY,
        (
            "fio"
            " -thread -directory=/tmp"
            " -numjobs=1"
            " -rw=rw"
            " -bs=4k"
            " -size=4k"
            " -runtime=60"
            " -time_based -name=chaos -direct=1"
        ),
    )


def test_inject_io_stress_should_call_exec_command_with_the_r_mode_fio_cmd_generated_by_arb_params(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_io_stress(
        dir="/foo/baz/bar",
        workers=4,
        mode="r",
        block_size=2,
        block_count=10,
        length=10,
        target=target,
    )
    spy_exec_command.assert_called_once_with(
        ANY,
        (
            "fio"
            " -thread -directory=/foo/baz/bar"
            " -numjobs=4"
            " -rw=read"
            " -bs=2k"
            " -size=20k"
            " -runtime=10"
            " -time_based -name=chaos -direct=1"
        ),
    )


def test_inject_io_stress_should_call_exec_command_with_the_w_mode_fio_cmd_generated_by_arb_params(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_io_stress(
        dir="/foo/baz/bar",
        workers=2,
        mode="w",
        block_size=8,
        block_count=5,
        length=120,
        target=target,
    )
    spy_exec_command.assert_called_once_with(
        ANY,
        (
            "fio"
            " -thread -directory=/foo/baz/bar"
            " -numjobs=2"
            " -rw=write"
            " -bs=8k"
            " -size=40k"
            " -runtime=120"
            " -time_based -name=chaos -direct=1"
        ),
    )


def test_inject_io_stress_should_throw_ValueError_when_the_argument_workers_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_io_stress(workers=0, target=target)
    assert (
        str(error_info.value)
        == "The argument 'workers' must be greater than or equal to 1"
    )


def test_inject_io_stress_should_throw_ValueError_when_the_argument_mode_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_io_stress(mode="foo", target=target)
    assert (
        str(error_info.value)
        == "Invalid input: 'foo'. The argument 'mode' must be chosen between ['r', 'w', 'rw']."
    )


def test_inject_io_stress_should_throw_ValueError_when_the_argument_block_size_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_io_stress(block_size=0, target=target)
    assert (
        str(error_info.value)
        == "The argument 'block_size' must be greater than or equal to 1"
    )


def test_inject_io_stress_should_throw_ValueError_when_the_argument_block_count_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_io_stress(block_count=0, target=target)
    assert (
        str(error_info.value)
        == "The argument 'block_count' must be greater than or equal to 1"
    )


def test_inject_io_stress_should_throw_ValueError_when_the_argument_target_is_invalid():
    invalid_target = {
        "hostname": "localhost",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        inject_io_stress(target=invalid_target)
    assert str(error_info.value) == "'username' is not found in target."

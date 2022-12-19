from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture

from src.action import inject_process_pkill
from tests.conftest import mock_ssh_client, target


def test_inject_process_pkill_should_call_exec_command_with_pkill_cmd_generated_by_default_params(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_pkill(process_name_lst=["app1", "app2"], target=target)
    spy_exec_command.assert_called_once_with(
        ANY, "for pname in app1 app2; do sudo pkill -KILL $pname; done"
    )


def test_inject_process_pkill_should_call_exec_command_multi_times_when_length_greater_than_interval(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_pkill(
        process_name_lst=["app1"], target=target, interval=0, length=0.1
    )
    assert spy_exec_command.call_count > 1


def test_inject_process_pkill_should_also_kill_child_process_when_kill_children_flag_is_True(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_pkill(
        process_name_lst=["app1", "app2"],
        group="foo",
        user="baz",
        newest=True,
        exact=True,
        full_match=True,
        kill_children=True,
        target=target,
    )
    spy_exec_command.assert_has_calls(
        [
            mocker.call(
                ANY,
                (
                    "for pname in app1 app2;"
                    " do for pid in $(pgrep $pname -G foo -U baz -n -x -f);"
                    " do sudo pkill -KILL -P $pid; done;"
                    " done"
                ),
            ),
            mocker.call(
                ANY,
                "for pname in app1 app2; do sudo pkill -KILL $pname -G foo -U baz -n -x -f; done",
            ),
        ]
    )


def test_inject_process_pkill_should_throw_ValueError_when_the_argument_process_name_lst_is_empty(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_process_pkill(process_name_lst=[], target=target)
    assert str(error_info.value) == "The argument 'process_name_lst' must not be empty."


def test_inject_process_pkill_should_throw_ValueError_when_the_argument_target_is_invalid():
    invalid_target = {
        "username": "user",
        "key_filename": "/foo/baz/bar",
    }
    with pytest.raises(ValueError) as error_info:
        inject_process_pkill(process_name_lst=["sleep"], target=invalid_target)
    assert str(error_info.value) == "'hostname' is not found in target."


def test_inject_process_pkill_should_throw_ValueError_when_the_argument_signal_is_invalid(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_process_pkill(process_name_lst=["sleep"], signal="FOO", target=target)
    assert str(error_info.value) == (
        "'FOO' is not a valid Signal."
        " The argument 'signal' must be chosen between"
        " ['HUP', 'INT', 'QUIT', 'ILL', 'TRAP', 'ABRT', 'FPE',"
        " 'KILL', 'SEGV', 'PIPE', 'ALRM', 'TERM', 'USR1', 'USR2']."
    )


def test_inject_process_pkill_should_exec_pkill_cmd_with_group_option_when_group_parameter_is_passed(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_pkill(
        process_name_lst=["app1", "app2"],
        group="my-group",
        newest=True,
        full_match=True,
        target=target,
    )
    spy_exec_command.assert_called_with(
        ANY,
        "for pname in app1 app2; do sudo pkill -KILL $pname -G my-group -n -f; done",
    )


def test_inject_process_pkill_should_exec_pkill_cmd_with_user_option_when_user_parameter_is_passed(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_pkill(
        process_name_lst=["app1", "app2"],
        user="foo",
        oldest=True,
        exact=True,
        full_match=True,
        target=target,
    )
    spy_exec_command.assert_called_with(
        ANY,
        "for pname in app1 app2; do sudo pkill -KILL $pname -U foo -o -x -f; done",
    )


def test_inject_process_pkill_should_exec_pkill_cmd_with_newest_option_when_newest_flag_is_True(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_pkill(process_name_lst=["app1", "app2"], newest=True, target=target)
    spy_exec_command.assert_called_with(
        ANY,
        "for pname in app1 app2; do sudo pkill -KILL $pname -n; done",
    )


def test_inject_process_pkill_should_exec_pkill_command_with_oldest_option_when_oldest_flag_is_True(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_pkill(process_name_lst=["app1", "app2"], oldest=True, target=target)
    spy_exec_command.assert_called_with(
        ANY,
        "for pname in app1 app2; do sudo pkill -KILL $pname -o; done",
    )


def test_inject_process_pkill_should_throw_ValueError_when_both_newest_and_oldest_flags_are_True(
    target: target,
):
    with pytest.raises(ValueError) as error_info:
        inject_process_pkill(
            process_name_lst=["app1", "app2"],
            newest=True,
            oldest=True,
            target=target,
        )
    assert str(error_info.value) == "'newest' flag cannot be used with 'oldest' flag."


def test_inject_process_pkill_should_exec_pkill_command_with_exact_option_when_exact_flag_is_True(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_pkill(
        process_name_lst=["app1", "app2"], newest=True, exact=True, target=target
    )
    spy_exec_command.assert_called_with(
        ANY,
        "for pname in app1 app2; do sudo pkill -KILL $pname -n -x; done",
    )


def test_inject_process_pkill_should_exec_pkill_cmd_with_full_option_when_full_match_flag_is_True(
    target: target, mocker: MockerFixture, mock_ssh_client: mock_ssh_client
):
    spy_exec_command = mocker.spy(mock_ssh_client, "exec_command")
    inject_process_pkill(
        process_name_lst=["app1", "app2"],
        oldest=True,
        exact=True,
        full_match=True,
        target=target,
    )
    spy_exec_command.assert_called_with(
        ANY,
        "for pname in app1 app2; do sudo pkill -KILL $pname -o -x -f; done",
    )

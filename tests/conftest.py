from typing import Dict

import paramiko
import pytest


class MockSSHClient:
    def __init__(self) -> None:
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def set_missing_host_key_policy(self, policy):
        self.policy = policy

    def connect(self, hostname, username, key_filename):
        pass

    def exec_command(self, command):
        return None, MockStdout(), MockStderr()


class MockAutoAddPolicy:
    def __init__(self):
        pass


class MockStdout:
    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration


class MockStderr:
    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration


@pytest.fixture
def mock_ssh_client(monkeypatch: pytest.MonkeyPatch) -> MockSSHClient:
    ssh_client = MockSSHClient
    monkeypatch.setattr(paramiko, "SSHClient", ssh_client)
    monkeypatch.setattr(paramiko, "AutoAddPolicy", MockAutoAddPolicy)
    return ssh_client


@pytest.fixture
def target() -> Dict[str, str]:
    return {
        "hostname": "localhost",
        "username": "user",
        "key_filename": "/foo/baz/bar",
    }

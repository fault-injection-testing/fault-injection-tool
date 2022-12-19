import pytest

from src.target import Target


def test_target_build_success():
    conf = {
        "hostname": "localhost",
        "username": "user",
        "key_filename": "/foo/baz/bar",
    }
    target: Target = Target.from_(conf)
    assert target.hostname == "localhost"
    assert target.username == "user"
    assert target.key_filename == "/foo/baz/bar"


def test_target_build_failure():
    conf = {"username": "user", "key_filename": "/foo/baz/bar"}
    with pytest.raises(KeyError):
        Target.from_(conf)

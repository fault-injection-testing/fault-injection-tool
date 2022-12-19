from cerberus import Validator

from src import tc_schema


def test_validate_root_schema_return_True_when_validation_is_success():
    v = tc_schema.validator
    data = {
        "device": "eth0",
        "tc": [
            {
                "destination_ip_addresses": ["addr1"],
                "destination_ports": ["p1"],
                "source_ports": ["p2"],
                "latency": 100,
            },
            {
                "destination_ip_addresses": ["addr1"],
                "destination_ports": ["p1"],
                "source_ports": ["p2"],
                "loss": 0.1,
                "protocol": ["tcp"],
                "corrupt": True,
            },
        ],
    }
    assert v.validate(data)


def test_normalized_root_schema_can_set_default_value_for_missing_fields():
    v = tc_schema.validator
    data = {"tc": [{"loss": 0.1}, {"latency": 100}]}
    assert v.normalized(data) == {
        "device": "eth0",
        "tc": [
            {
                "destination_ip_addresses": [],
                "destination_ports": [],
                "source_ports": [],
                "latency": None,
                "loss": 0.1,
                "corrupt": False,
                "protocol": ["tcp", "udp", "icmp"],
            },
            {
                "destination_ip_addresses": [],
                "destination_ports": [],
                "source_ports": [],
                "latency": 100,
                "loss": None,
                "corrupt": False,
                "protocol": ["tcp", "udp", "icmp"],
            },
        ],
    }


def test_validate_root_schema_return_False_when_params_is_empty():
    v = tc_schema.validator
    data = {"tc": []}
    assert not v.validate(data)
    assert v.errors["tc"] == ["empty values not allowed"]


def test_validate_with_tc_schema_return_False_when_loss_greater_than_100():
    v = Validator(tc_schema.__tc_schema)
    data = {
        "destination_ip_addresses": ["addr"],
        "destination_ports": ["p1"],
        "source_ports": ["p2"],
        "loss": 101,
    }
    assert not v.validate(data)
    assert v.errors["loss"] == ["max value is 100"]


def test_validate_with_tc_schema_return_False_when_protocol_contains_unallowed_value():
    v = Validator(tc_schema.__tc_schema)
    data = {"protocol": ["foo"]}
    assert not v.validate(data)
    assert v.errors["protocol"] == ["unallowed values ('foo',)"]


def test_validate_with_tc_schema_return_False_when_protocol_is_empty():
    v = Validator(tc_schema.__tc_schema)
    data = {"protocol": []}
    assert not v.validate(data)
    assert v.errors["protocol"] == ["empty values not allowed"]

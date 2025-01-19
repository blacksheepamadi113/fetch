import pytest
from consumer import validate_and_transform

def test_missing_app_version():
    message = {"device_type": "android", "ip": "192.168.1.1"}
    valid, result = validate_and_transform(message)
    assert not valid
    assert result["reason"] == "missing_app_version"

def test_missing_ip():
    message = {"app_version": "1.2.3", "device_type": "ios"}
    valid, result = validate_and_transform(message)
    assert not valid
    assert result["reason"] == "missing_ip"

def test_invalid_ip():
    message = {"app_version": "1.2.3", "device_type": "ios", "ip": "999.999.999.999"}
    valid, result = validate_and_transform(message)
    assert not valid
    assert result["reason"] == "invalid_ip"

def test_valid_message():
    message = {"app_version": "1.2.3", "device_type": "ios", "ip": "127.0.0.1"}
    valid, result = validate_and_transform(message)
    assert valid
    assert "processed_timestamp" in result
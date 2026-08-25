import json

import pytest
import requests

import src.api_client as api_client


# Build a real requests.Response object for controlled client tests.
def make_response(
    status_code=200,
    json_data=None,
    raw_content=None,
):
    response = requests.Response()
    response.status_code = status_code
    response.url = "http://127.0.0.1:8000/api/v1/test"

    # raw_content is used for malformed JSON test cases.
    if raw_content is not None:
        response._content = raw_content
    else:
        response._content = json.dumps(json_data).encode("utf-8")

    response.headers["Content-Type"] = "application/json"

    return response


# A valid Control collection must be returned as Python data.
def test_get_controls_returns_valid_collection(monkeypatch):
    payload = [
        {
            "control_id": "CTRL-001",
            "risk_level": "Critical",
        },
        {
            "control_id": "CTRL-002",
            "risk_level": "High",
        },
    ]

    def fake_get(url, timeout):
        return make_response(json_data=payload)

    monkeypatch.setattr(
        api_client.requests,
        "get",
        fake_get,
    )

    result = api_client.get_controls()

    assert result == payload


# A valid individual Control must be returned correctly.
def test_get_control_returns_valid_control(monkeypatch):
    payload = {
        "control_id": "CTRL-003",
        "risk_level": "High",
    }

    def fake_get(url, timeout):
        return make_response(json_data=payload)

    monkeypatch.setattr(
        api_client.requests,
        "get",
        fake_get,
    )

    result = api_client.get_control("CTRL-003")

    assert result == payload


# HTTP 404 responses must become controlled ApiClientError exceptions.
def test_get_control_handles_404(monkeypatch):
    def fake_get(url, timeout):
        return make_response(status_code=404, json_data={})

    monkeypatch.setattr(
        api_client.requests,
        "get",
        fake_get,
    )

    with pytest.raises(
        api_client.ApiClientError,
        match="HTTP 404",
    ):
        api_client.get_control("CTRL-999")


# HTTP 500 responses must become controlled ApiClientError exceptions.
def test_get_controls_handles_500(monkeypatch):
    def fake_get(url, timeout):
        return make_response(status_code=500, json_data={})

    monkeypatch.setattr(
        api_client.requests,
        "get",
        fake_get,
    )

    with pytest.raises(
        api_client.ApiClientError,
        match="HTTP 500",
    ):
        api_client.get_controls()


# Network timeouts must be translated into ApiClientError.
def test_get_controls_handles_timeout(monkeypatch):
    def fake_get(url, timeout):
        raise requests.exceptions.Timeout(
            "simulated timeout"
        )

    monkeypatch.setattr(
        api_client.requests,
        "get",
        fake_get,
    )

    with pytest.raises(
        api_client.ApiClientError,
        match="API request timed out",
    ):
        api_client.get_controls()


# Connection failures must be translated into ApiClientError.
def test_get_controls_handles_connection_error(monkeypatch):
    def fake_get(url, timeout):
        raise requests.exceptions.ConnectionError(
            "simulated connection failure"
        )

    monkeypatch.setattr(
        api_client.requests,
        "get",
        fake_get,
    )

    with pytest.raises(
        api_client.ApiClientError,
        match="Could not connect to the API",
    ):
        api_client.get_controls()


# Malformed JSON must not escape as a low-level parsing exception.
def test_get_controls_handles_invalid_json(monkeypatch):
    def fake_get(url, timeout):
        return make_response(
            raw_content=b"this is not valid json"
        )

    monkeypatch.setattr(
        api_client.requests,
        "get",
        fake_get,
    )

    with pytest.raises(
        api_client.ApiClientError,
        match="API returned invalid JSON",
    ):
        api_client.get_controls()


# The collection endpoint must return a top-level JSON array.
def test_get_controls_rejects_wrong_top_level_structure(monkeypatch):
    payload = {
        "control_id": "CTRL-001",
        "risk_level": "Critical",
    }

    def fake_get(url, timeout):
        return make_response(json_data=payload)

    monkeypatch.setattr(
        api_client.requests,
        "get",
        fake_get,
    )

    with pytest.raises(
        api_client.ApiClientError,
        match="unexpected collection structure",
    ):
        api_client.get_controls()


# A Control missing a required public field must be rejected.
def test_get_controls_rejects_missing_field(monkeypatch):
    payload = [
        {
            "control_id": "CTRL-001",
        }
    ]

    def fake_get(url, timeout):
        return make_response(json_data=payload)

    monkeypatch.setattr(
        api_client.requests,
        "get",
        fake_get,
    )

    with pytest.raises(
        api_client.ApiClientError,
        match="unexpected Control structure",
    ):
        api_client.get_controls()


# Every real client request must use the explicit configured timeout.
def test_get_controls_uses_explicit_timeout(monkeypatch):
    captured_request = {}

    def fake_get(url, timeout):
        captured_request["url"] = url
        captured_request["timeout"] = timeout

        return make_response(json_data=[])

    monkeypatch.setattr(
        api_client.requests,
        "get",
        fake_get,
    )

    result = api_client.get_controls()

    assert result == []
    assert captured_request["url"] == (
        "http://127.0.0.1:8000/api/v1/controls"
    )
    assert captured_request["timeout"] == (
        api_client.DEFAULT_TIMEOUT_SECONDS
    )

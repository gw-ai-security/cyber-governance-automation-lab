from fastapi.testclient import TestClient

from api.mock_api import app


# Test the FastAPI application in-process without running Uvicorn.
client = TestClient(app)


# GET collection must return HTTP 200.
def test_get_controls_returns_200():
    response = client.get("/api/v1/controls")

    assert response.status_code == 200


# Canonical collection must contain exactly five Controls.
def test_get_controls_returns_five_controls():
    response = client.get("/api/v1/controls")
    controls = response.json()

    assert len(controls) == 5


# Controls must preserve the deterministic canonical source order.
def test_get_controls_preserves_canonical_order():
    response = client.get("/api/v1/controls")
    controls = response.json()

    assert [control["control_id"] for control in controls] == [
        "CTRL-001",
        "CTRL-002",
        "CTRL-003",
        "CTRL-004",
        "CTRL-005",
    ]


# Public Controls expose exactly the minimized API fields.
def test_get_controls_returns_expected_fields():
    response = client.get("/api/v1/controls")
    controls = response.json()

    for control in controls:
        assert set(control.keys()) == {
            "control_id",
            "risk_level",
        }


# Internal identity data must not be exposed by the API.
def test_get_controls_does_not_expose_owner_email():
    response = client.get("/api/v1/controls")
    controls = response.json()

    for control in controls:
        assert "owner_email" not in control


# Existing Control must return its exact public representation.
def test_get_control_returns_expected_control():
    response = client.get("/api/v1/controls/CTRL-001")

    assert response.status_code == 200
    assert response.json() == {
        "control_id": "CTRL-001",
        "risk_level": "Critical",
    }


# Unknown Control must return the frozen HTTP 404 contract.
def test_get_unknown_control_returns_404():
    response = client.get("/api/v1/controls/CTRL-999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "CONTROL_NOT_FOUND",
            "message": "Control CTRL-999 was not found.",
        }
    }


# Source failures must become the frozen HTTP 500 contract.
def test_control_source_failure_returns_500(monkeypatch):
    def raise_source_error(_):
        raise OSError("simulated source failure")

    monkeypatch.setattr(
        "api.mock_api.load_control_catalog",
        raise_source_error,
    )

    response = client.get("/api/v1/controls")

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "code": "CONTROL_SOURCE_ERROR",
            "message": "Control data could not be loaded.",
        }
    }


# Detail endpoint must use the same controlled source-error boundary.
def test_control_detail_source_failure_returns_500(monkeypatch):
    def raise_source_error(_):
        raise ValueError("simulated invalid source")

    monkeypatch.setattr(
        "api.mock_api.load_control_catalog",
        raise_source_error,
    )

    response = client.get("/api/v1/controls/CTRL-001")

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "code": "CONTROL_SOURCE_ERROR",
            "message": "Control data could not be loaded.",
        }
    }


# Internal paths and exception details must never leak to clients.
def test_control_source_failure_does_not_leak_internal_details(monkeypatch):
    sensitive_path = r"C:\Users\Example\secret\control_catalog.json"

    def raise_source_error(_):
        raise OSError(f"Could not open {sensitive_path}")

    monkeypatch.setattr(
        "api.mock_api.load_control_catalog",
        raise_source_error,
    )

    response = client.get("/api/v1/controls")

    assert response.status_code == 500
    assert sensitive_path not in response.text
    assert "Could not open" not in response.text

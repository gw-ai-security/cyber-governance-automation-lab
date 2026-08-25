import requests


# Local read-only REST API used by the Phase 10 integration.
BASE_URL = "http://127.0.0.1:8000/api/v1"

# Every real HTTP request must use an explicit timeout.
DEFAULT_TIMEOUT_SECONDS = 3

# Frozen public Control contract exposed by the API.
CONTROL_FIELDS = {
    "control_id",
    "risk_level",
}

# Allowed values of the external API risk-level field.
RISK_LEVELS = {
    "Low",
    "Medium",
    "High",
    "Critical",
}


# Controlled exception raised by this client for API-related failures.
class ApiClientError(RuntimeError):
    pass


# Perform one GET request and return the parsed JSON response.
def _get_json(endpoint: str):
    url = f"{BASE_URL}{endpoint}"

    try:
        response = requests.get(
            url,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        # Convert HTTP error responses such as 404 or 500 into HTTPError.
        response.raise_for_status()

    except requests.exceptions.Timeout as error:
        raise ApiClientError(
            "API request timed out."
        ) from error

    except requests.exceptions.ConnectionError as error:
        raise ApiClientError(
            "Could not connect to the API."
        ) from error

    except requests.exceptions.HTTPError as error:
        status_code = (
            error.response.status_code
            if error.response is not None
            else "unknown"
        )

        raise ApiClientError(
            f"API request failed with HTTP {status_code}."
        ) from error

    try:
        # Convert the HTTP JSON body into Python data.
        return response.json()

    except ValueError as error:
        raise ApiClientError(
            "API returned invalid JSON."
        ) from error


# Validate one Control against the frozen external API contract.
def _validate_control(control) -> dict[str, str]:
    if not isinstance(control, dict):
        raise ApiClientError(
            "API returned an invalid Control object."
        )

    # Reject missing or unexpected fields.
    if set(control.keys()) != CONTROL_FIELDS:
        raise ApiClientError(
            "API returned an unexpected Control structure."
        )

    control_id = control["control_id"]
    risk_level = control["risk_level"]

    # Both public Control fields must be strings.
    if not isinstance(control_id, str):
        raise ApiClientError(
            "API returned an invalid control_id."
        )

    if not isinstance(risk_level, str):
        raise ApiClientError(
            "API returned an invalid risk_level."
        )

    # risk_level must follow the frozen public enum.
    if risk_level not in RISK_LEVELS:
        raise ApiClientError(
            "API returned an unsupported risk_level."
        )

    # Return a clean representation of the validated public object.
    return {
        "control_id": control_id,
        "risk_level": risk_level,
    }


# Retrieve and validate the complete Control collection.
def get_controls() -> list[dict[str, str]]:
    data = _get_json("/controls")

    # The collection endpoint must return a top-level JSON array.
    if not isinstance(data, list):
        raise ApiClientError(
            "API returned an unexpected collection structure."
        )

    return [
        _validate_control(control)
        for control in data
    ]


# Retrieve and validate one Control by its technical identifier.
def get_control(control_id: str) -> dict[str, str]:
    data = _get_json(
        f"/controls/{control_id}"
    )

    return _validate_control(data)

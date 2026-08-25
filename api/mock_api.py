from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.extract import load_control_catalog


# FastAPI application used by Uvicorn.
app = FastAPI(
    title="Cyber Governance Control API",
    version="1.0.0",
    description=(
        "Local read-only Control projection for the Cyber Governance "
        "Automation Lab."
    ),
)


# Canonical Control Catalog path relative to the repository root.
CONTROL_CATALOG_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "reference"
    / "control_catalog.json"
)


# Public API model: expose only the required Control fields.
class ControlSummary(BaseModel):
    control_id: str
    risk_level: Literal["Low", "Medium", "High", "Critical"]


# Load Controls and translate source failures into a safe HTTP error.
def _load_controls() -> list[dict]:
    try:
        return load_control_catalog(CONTROL_CATALOG_PATH)

    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "CONTROL_SOURCE_ERROR",
                "message": "Control data could not be loaded.",
            },
        ) from error


# Return all canonical Controls as minimized API objects.
@app.get(
    "/api/v1/controls",
    response_model=list[ControlSummary],
)
def get_controls():
    controls = _load_controls()

    return [
        {
            "control_id": control["control_id"],
            "risk_level": control["risk_level"],
        }
        for control in controls
    ]


# Return one Control identified by its control_id.
@app.get(
    "/api/v1/controls/{control_id}",
    response_model=ControlSummary,
)
def get_control(control_id: str):
    controls = _load_controls()

    for control in controls:
        if control["control_id"] == control_id:
            return {
                "control_id": control["control_id"],
                "risk_level": control["risk_level"],
            }

    # Unknown Control IDs are returned as HTTP 404.
    raise HTTPException(
        status_code=404,
        detail={
            "code": "CONTROL_NOT_FOUND",
            "message": f"Control {control_id} was not found.",
        },
    )

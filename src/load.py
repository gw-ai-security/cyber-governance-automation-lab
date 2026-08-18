import json
from pathlib import Path

import pandas as pd


CURATED_CONTROL_STATUS_FILENAME = "curated_control_status.csv"
DATA_QUALITY_ISSUES_FILENAME = "data_quality_issues.csv"
AI_REVIEW_QUEUE_FILENAME = "ai_review_queue.json"


def write_curated_control_status(
    curated: pd.DataFrame,
    output_path: Path,
) -> None:
    """Serialize the prepared curated Control Status dataset to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    curated.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
        na_rep="",
        date_format="%Y-%m-%d",
        float_format="%.15g",
        lineterminator="\n",
    )


def write_data_quality_issues(
    dq_issues: pd.DataFrame,
    output_path: Path,
) -> None:
    """Serialize the prepared Data Quality Issue records to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dq_issues.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
        na_rep="",
        lineterminator="\n",
    )


def write_ai_review_queue(
    ai_review_queue: dict,
    output_path: Path,
) -> None:
    """Serialize the prepared AI review queue as strict UTF-8 JSON."""

    serialized = json.dumps(
        ai_review_queue,
        ensure_ascii=False,
        indent=2,
        allow_nan=False,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(serialized + "\n")


def write_pipeline_outputs(
    curated: pd.DataFrame,
    dq_issues: pd.DataFrame,
    ai_review_queue: dict,
    output_directory: Path,
) -> dict[str, Path]:
    """Write all three contractual Phase 3 output files."""

    output_directory.mkdir(parents=True, exist_ok=True)
    output_paths = {
        "curated_control_status": (
            output_directory / CURATED_CONTROL_STATUS_FILENAME
        ),
        "data_quality_issues": (
            output_directory / DATA_QUALITY_ISSUES_FILENAME
        ),
        "ai_review_queue": (
            output_directory / AI_REVIEW_QUEUE_FILENAME
        ),
    }

    write_curated_control_status(
        curated,
        output_paths["curated_control_status"],
    )
    write_data_quality_issues(
        dq_issues,
        output_paths["data_quality_issues"],
    )
    write_ai_review_queue(
        ai_review_queue,
        output_paths["ai_review_queue"],
    )

    return output_paths

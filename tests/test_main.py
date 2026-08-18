import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from src.transform import CURATED_COLUMNS


REPO_ROOT = Path(__file__).resolve().parents[1]
AI_ITEM_FIELDS = [
    "submission_id",
    "control_id",
    "control_name",
    "business_unit",
    "risk_level",
    "reporting_period",
    "submission_status",
    "due_date",
    "evidence_present",
    "days_overdue",
    "comment",
    "review_reasons",
]


def _copy_runtime_project(tmp_path):
    project_root = tmp_path / "project"
    shutil.copytree(REPO_ROOT / "src", project_root / "src")
    shutil.copytree(
        REPO_ROOT / "data/reference",
        project_root / "data/reference",
    )
    shutil.copytree(
        REPO_ROOT / "data/raw",
        project_root / "data/raw",
    )
    return project_root


def _run_cli(project_root, *arguments):
    return subprocess.run(
        [sys.executable, "src/main.py", *arguments],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )


def test_canonical_cli_end_to_end_acceptance(tmp_path):
    project_root = _copy_runtime_project(tmp_path)

    result = _run_cli(
        project_root,
        "--as-of-date",
        "2026-08-15",
    )

    assert result.returncode == 0, result.stderr
    for expected_line in [
        "Controls loaded: 5",
        "Submissions loaded: 15",
        "Actions loaded: 5",
        "DQ issues: 5",
        "Valid submissions: 10",
        "Invalid submissions: 5",
        "AI review queue items: 2",
    ]:
        assert expected_line in result.stdout

    output_directory = project_root / "data/curated"
    curated_path = output_directory / "curated_control_status.csv"
    issues_path = output_directory / "data_quality_issues.csv"
    queue_path = output_directory / "ai_review_queue.json"
    assert curated_path.is_file()
    assert issues_path.is_file()
    assert queue_path.is_file()

    with curated_path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        curated_rows = list(reader)
        assert reader.fieldnames == CURATED_COLUMNS

    assert len(curated_rows) == 15
    by_submission = {
        row["submission_id"]: row
        for row in curated_rows
    }
    assert sum(
        row["data_quality_status"] == "Valid"
        for row in curated_rows
    ) == 10
    assert sum(
        row["data_quality_status"] == "Invalid"
        for row in curated_rows
    ) == 5
    assert by_submission["SUB-004"]["submission_late"] == "True"
    assert by_submission["SUB-004"]["days_late"] == "2"
    assert by_submission["SUB-014"]["overdue_flag"] == "True"
    assert by_submission["SUB-014"]["days_overdue"] == "5"
    assert by_submission["SUB-015"]["control_name"] == ""
    assert "SUB-015" in by_submission
    assert "SUB-008" in by_submission
    assert "SUB-009" in by_submission

    issues = pd.read_csv(issues_path, keep_default_na=False)
    assert issues[["submission_id", "rule"]].to_records(
        index=False
    ).tolist() == [
        ("SUB-002", "DQ-004 Missing Evidence"),
        ("SUB-006", "DQ-003 Invalid Status"),
        ("SUB-008", "DQ-005 Duplicate Submission"),
        ("SUB-009", "DQ-005 Duplicate Submission"),
        ("SUB-015", "DQ-002 Unknown Control ID"),
    ]

    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    assert queue["as_of_date"] == "2026-08-15"
    assert [item["submission_id"] for item in queue["items"]] == [
        "SUB-005",
        "SUB-014",
    ]
    assert all(list(item) == AI_ITEM_FIELDS for item in queue["items"])


def test_cli_without_date_uses_default_processing_date(tmp_path):
    project_root = _copy_runtime_project(tmp_path)

    result = _run_cli(project_root)

    assert result.returncode == 0, result.stderr
    assert "Controls loaded: 5" in result.stdout
    queue_path = project_root / "data/curated/ai_review_queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    assert queue["as_of_date"]


@pytest.mark.parametrize(
    "invalid_date",
    ["20260815", "15-08-2026", "08/15/2026", "2026-02-30"],
)
def test_cli_rejects_invalid_as_of_date(tmp_path, invalid_date):
    project_root = _copy_runtime_project(tmp_path)

    result = _run_cli(
        project_root,
        "--as-of-date",
        invalid_date,
    )

    assert result.returncode != 0
    assert "as-of date" in result.stderr


def test_missing_required_input_returns_nonzero(tmp_path):
    project_root = _copy_runtime_project(tmp_path)
    (project_root / "data/raw/actions.csv").unlink()

    result = _run_cli(
        project_root,
        "--as-of-date",
        "2026-08-15",
    )

    assert result.returncode == 1
    assert "Pipeline failed:" in result.stderr
    assert "actions.csv" in result.stderr

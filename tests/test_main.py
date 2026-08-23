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
SUBMISSION_COLUMNS = [
    "submission_id",
    "control_id",
    "reporting_period",
    "due_date",
    "status",
    "evidence_reference",
    "submitted_at",
    "submitted_by",
    "comment",
]
ACTION_COLUMNS = [
    "action_id",
    "control_id",
    "submission_id",
    "owner_email",
    "created_at",
    "due_date",
    "status",
    "reminder_count",
    "last_reminder_at",
    "description",
]
OUTPUT_FILENAMES = [
    "curated_control_status.csv",
    "data_quality_issues.csv",
    "ai_review_queue.json",
]


def _external_control():
    return {
        "control_id": "EXT-CTRL-001",
        "control_name": "Synthetic Monthly Control",
        "control_statement": "Synthetic evidence must be reviewed monthly.",
        "business_unit": "IT Operations",
        "owner_role": "Synthetic Control Owner",
        "owner_email": "control-owner@example.com",
        "frequency": "Monthly",
        "risk_level": "High",
    }


def _external_submissions():
    return [
        {
            "submission_id": "EXT-SUB-001",
            "control_id": "EXT-CTRL-001",
            "reporting_period": "2026-07",
            "due_date": "2026-08-10",
            "status": "Not Submitted",
            "evidence_reference": "",
            "submitted_at": "",
            "submitted_by": "",
            "comment": "Synthetic overdue submission.",
        },
        {
            "submission_id": "EXT-SUB-002",
            "control_id": "EXT-CTRL-001",
            "reporting_period": "2026-08",
            "due_date": "2026-09-10",
            "status": "Pending",
            "evidence_reference": "",
            "submitted_at": "",
            "submitted_by": "",
            "comment": "Synthetic invalid status.",
        },
    ]


def _external_actions():
    return [
        {
            "action_id": "EXT-ACT-001",
            "control_id": "EXT-CTRL-001",
            "submission_id": "EXT-SUB-001",
            "owner_email": "action-owner@example.com",
            "created_at": "2026-08-11",
            "due_date": "2026-08-18",
            "status": "Open",
            "reminder_count": "2",
            "last_reminder_at": "2026-08-15",
            "description": "Synthetic missing-submission follow-up.",
        }
    ]


def _write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _write_external_snapshot(
    tmp_path,
    submissions=None,
    actions=None,
):
    snapshot_directory = tmp_path / "external snapshots"
    snapshot_directory.mkdir()
    paths = {
        "controls": snapshot_directory / "controls.json",
        "submissions": snapshot_directory / "submissions.csv",
        "actions": snapshot_directory / "actions.csv",
    }
    paths["controls"].write_text(
        json.dumps([_external_control()], indent=2),
        encoding="utf-8",
    )
    _write_csv(
        paths["submissions"],
        SUBMISSION_COLUMNS,
        _external_submissions() if submissions is None else submissions,
    )
    _write_csv(
        paths["actions"],
        ACTION_COLUMNS,
        _external_actions() if actions is None else actions,
    )
    return paths


def _external_arguments(paths, output_directory):
    return [
        "--as-of-date",
        "2026-08-15",
        "--controls-path",
        str(paths["controls"]),
        "--submissions-path",
        str(paths["submissions"]),
        "--actions-path",
        str(paths["actions"]),
        "--output-directory",
        str(output_directory),
    ]


def _output_paths(output_directory):
    return [output_directory / name for name in OUTPUT_FILENAMES]


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


def test_external_snapshot_paths_and_output_boundary_end_to_end(tmp_path):
    project_root = _copy_runtime_project(tmp_path)
    paths = _write_external_snapshot(tmp_path)
    output_directory = tmp_path / "external outputs"
    protected_paths = list(paths.values()) + [
        project_root / "data/reference/control_catalog.json",
        project_root / "data/raw/evidence_submissions.csv",
        project_root / "data/raw/actions.csv",
    ]
    bytes_before = {
        path: path.read_bytes()
        for path in protected_paths
    }

    result = _run_cli(
        project_root,
        *_external_arguments(paths, output_directory),
    )

    assert result.returncode == 0, result.stderr
    for expected_line in [
        "Controls loaded: 1",
        "Submissions loaded: 2",
        "Actions loaded: 1",
        "DQ issues: 1",
        "Valid submissions: 1",
        "Invalid submissions: 1",
        "AI review queue items: 1",
    ]:
        assert expected_line in result.stdout

    output_paths = _output_paths(output_directory)
    assert all(path.is_file() for path in output_paths)
    assert not (project_root / "data/curated").exists()

    with output_paths[0].open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        curated_rows = list(reader)
        assert reader.fieldnames == CURATED_COLUMNS

    assert [row["submission_id"] for row in curated_rows] == [
        "EXT-SUB-001",
        "EXT-SUB-002",
    ]
    assert "SUB-014" not in {
        row["submission_id"]
        for row in curated_rows
    }
    by_submission = {
        row["submission_id"]: row
        for row in curated_rows
    }
    overdue = by_submission["EXT-SUB-001"]
    assert overdue["overdue_flag"] == "True"
    assert overdue["days_overdue"] == "5"
    assert overdue["active_action_id"] == "EXT-ACT-001"
    assert overdue["active_action_status"] == "Open"
    assert overdue["active_action_due_date"] == "2026-08-18"
    assert overdue["reminder_count"] == "2"
    assert overdue["last_reminder_at"] == "2026-08-15"
    assert by_submission["EXT-SUB-002"]["data_quality_status"] == (
        "Invalid"
    )

    issues = pd.read_csv(output_paths[1], keep_default_na=False)
    assert issues[["submission_id", "rule", "severity"]].to_records(
        index=False
    ).tolist() == [
        ("EXT-SUB-002", "DQ-003 Invalid Status", "High")
    ]

    queue = json.loads(output_paths[2].read_text(encoding="utf-8"))
    assert queue["as_of_date"] == "2026-08-15"
    assert [item["submission_id"] for item in queue["items"]] == [
        "EXT-SUB-001"
    ]
    assert queue["items"][0]["days_overdue"] == 5

    assert {
        path: path.read_bytes()
        for path in protected_paths
    } == bytes_before


@pytest.mark.parametrize(
    "provided_sources",
    [
        ("controls",),
        ("submissions",),
        ("actions",),
        ("controls", "submissions"),
        ("controls", "actions"),
        ("submissions", "actions"),
    ],
)
def test_cli_rejects_every_partial_source_override(
    tmp_path,
    provided_sources,
):
    project_root = _copy_runtime_project(tmp_path)
    paths = _write_external_snapshot(tmp_path)
    flag_by_source = {
        "controls": "--controls-path",
        "submissions": "--submissions-path",
        "actions": "--actions-path",
    }
    arguments = ["--as-of-date", "2026-08-15"]
    for source in provided_sources:
        arguments.extend([flag_by_source[source], str(paths[source])])

    result = _run_cli(project_root, *arguments)

    assert result.returncode != 0
    assert "all three source paths must be supplied together" in result.stderr
    assert "Controls loaded:" not in result.stdout
    assert not (project_root / "data/curated").exists()


def test_missing_external_file_fails_without_canonical_fallback(tmp_path):
    project_root = _copy_runtime_project(tmp_path)
    paths = _write_external_snapshot(tmp_path)
    paths["submissions"] = (
        tmp_path / "external snapshots/missing-submissions.csv"
    )
    output_directory = tmp_path / "external outputs"

    result = _run_cli(
        project_root,
        *_external_arguments(paths, output_directory),
    )

    assert result.returncode == 1
    assert "Pipeline failed:" in result.stderr
    assert "missing-submissions.csv" in result.stderr
    assert "Submissions loaded: 15" not in result.stdout
    assert not all(path.exists() for path in _output_paths(output_directory))


def test_malformed_external_submission_contract_fails(tmp_path):
    project_root = _copy_runtime_project(tmp_path)
    paths = _write_external_snapshot(tmp_path)
    reordered_columns = SUBMISSION_COLUMNS[1:] + SUBMISSION_COLUMNS[:1]
    _write_csv(
        paths["submissions"],
        reordered_columns,
        _external_submissions(),
    )
    output_directory = tmp_path / "external outputs"

    result = _run_cli(
        project_root,
        *_external_arguments(paths, output_directory),
    )

    assert result.returncode == 1
    assert "Pipeline failed:" in result.stderr
    assert "Submission CSV header" in result.stderr
    assert "wrong order" in result.stderr
    assert "Submissions loaded: 15" not in result.stdout
    assert not all(path.exists() for path in _output_paths(output_directory))


def test_header_only_external_action_snapshot_is_supported(tmp_path):
    project_root = _copy_runtime_project(tmp_path)
    paths = _write_external_snapshot(
        tmp_path,
        submissions=[_external_submissions()[0]],
        actions=[],
    )
    output_directory = tmp_path / "empty action outputs"

    result = _run_cli(
        project_root,
        *_external_arguments(paths, output_directory),
    )

    assert result.returncode == 0, result.stderr
    for expected_line in [
        "Controls loaded: 1",
        "Submissions loaded: 1",
        "Actions loaded: 0",
        "DQ issues: 0",
        "Valid submissions: 1",
        "Invalid submissions: 0",
        "AI review queue items: 1",
    ]:
        assert expected_line in result.stdout
    assert all(path.is_file() for path in _output_paths(output_directory))

    with (
        output_directory / "curated_control_status.csv"
    ).open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["submission_id"] == "EXT-SUB-001"
    assert rows[0]["active_action_id"] == ""
    assert rows[0]["active_action_status"] == ""
    assert rows[0]["active_action_due_date"] == ""
    assert rows[0]["reminder_count"] == "0"
    assert rows[0]["last_reminder_at"] == ""


def test_output_override_works_with_canonical_sources(tmp_path):
    project_root = _copy_runtime_project(tmp_path)
    output_directory = tmp_path / "canonical outputs"

    result = _run_cli(
        project_root,
        "--as-of-date",
        "2026-08-15",
        "--output-directory",
        str(output_directory),
    )

    assert result.returncode == 0, result.stderr
    assert "Controls loaded: 5" in result.stdout
    assert "Submissions loaded: 15" in result.stdout
    assert "Actions loaded: 5" in result.stdout
    assert all(path.is_file() for path in _output_paths(output_directory))
    assert not (project_root / "data/curated").exists()

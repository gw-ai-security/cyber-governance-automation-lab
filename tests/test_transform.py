from datetime import date
from pathlib import Path

import pandas as pd

from src.extract import (
    load_actions,
    load_control_catalog,
    load_submissions,
)
from src.transform import (
    CURATED_COLUMNS,
    add_source_row_number,
    build_ai_review_queue,
    build_curated_control_status,
    normalize_actions,
    normalize_control_catalog,
    normalize_submissions,
)
from src.validate import validate_submissions


REPO_ROOT = Path(__file__).resolve().parents[1]


def _canonical_pipeline(as_of_date=date(2026, 8, 15)):
    controls = normalize_control_catalog(
        load_control_catalog(
            REPO_ROOT / "data/reference/control_catalog.json"
        )
    )
    submissions = add_source_row_number(
        normalize_submissions(
            load_submissions(
                REPO_ROOT / "data/raw/evidence_submissions.csv"
            )
        )
    )
    actions = normalize_actions(
        load_actions(REPO_ROOT / "data/raw/actions.csv")
    )
    issues = validate_submissions(submissions, controls)
    curated = build_curated_control_status(
        submissions,
        controls,
        actions,
        issues,
        as_of_date,
    )
    queue = build_ai_review_queue(
        curated,
        as_of_date,
    )
    return controls, submissions, actions, issues, curated, queue


def test_normalization_trims_without_semantic_correction():
    raw = pd.DataFrame(
        [
            {
                "submission_id": " SUB-001 ",
                "status": " compliant ",
                "comment": "   ",
            }
        ]
    )

    normalized = normalize_submissions(raw)

    assert normalized.loc[0, "submission_id"] == "SUB-001"
    assert normalized.loc[0, "status"] == "compliant"
    assert pd.isna(normalized.loc[0, "comment"])


def test_source_row_lineage_is_one_based_and_preserves_order():
    submissions = pd.DataFrame(
        {"submission_id": ["SUB-002", "SUB-001"]}
    )

    result = add_source_row_number(submissions)

    assert result["source_row_number"].tolist() == [1, 2]
    assert result["submission_id"].tolist() == [
        "SUB-002",
        "SUB-001",
    ]


def test_canonical_phase3_acceptance_results():
    controls, submissions, actions, issues, curated, queue = (
        _canonical_pipeline()
    )

    assert (len(controls), len(submissions), len(actions)) == (5, 15, 5)
    assert issues[["submission_id", "rule"]].to_records(
        index=False
    ).tolist() == [
        ("SUB-002", "DQ-004 Missing Evidence"),
        ("SUB-006", "DQ-003 Invalid Status"),
        ("SUB-008", "DQ-005 Duplicate Submission"),
        ("SUB-009", "DQ-005 Duplicate Submission"),
        ("SUB-015", "DQ-002 Unknown Control ID"),
    ]
    assert len(curated) == 15
    assert list(curated.columns) == CURATED_COLUMNS
    assert (curated["data_quality_status"] == "Valid").sum() == 10
    assert (curated["data_quality_status"] == "Invalid").sum() == 5
    assert [item["submission_id"] for item in queue["items"]] == [
        "SUB-005",
        "SUB-014",
    ]


def test_canonical_timing_and_left_join_exceptions():
    _, _, _, _, curated, _ = _canonical_pipeline()
    by_submission = curated.set_index("submission_id")

    assert bool(by_submission.loc["SUB-004", "submission_late"])
    assert by_submission.loc["SUB-004", "days_late"] == 2
    assert bool(by_submission.loc["SUB-014", "overdue_flag"])
    assert by_submission.loc["SUB-014", "days_overdue"] == 5
    assert by_submission.loc["SUB-015", "data_quality_status"] == "Invalid"
    assert pd.isna(by_submission.loc["SUB-015", "control_name"])


def test_submission_due_on_as_of_date_is_not_overdue():
    _, _, _, _, curated, _ = _canonical_pipeline(
        date(2026, 8, 10)
    )
    row = curated.set_index("submission_id").loc["SUB-014"]

    assert not bool(row["overdue_flag"])
    assert row["days_overdue"] == 0


def test_submission_received_on_due_date_is_not_late():
    controls, submissions, actions, _, _, _ = _canonical_pipeline()
    changed = submissions.copy()
    changed.loc[
        changed["submission_id"] == "SUB-004",
        "submitted_at",
    ] = "2026-04-10"
    changed_issues = validate_submissions(changed, controls)

    curated = build_curated_control_status(
        changed,
        controls,
        actions,
        changed_issues,
        date(2026, 8, 15),
    )
    row = curated.set_index("submission_id").loc["SUB-004"]

    assert not bool(row["submission_late"])
    assert row["days_late"] == 0


def test_action_aggregation_does_not_multiply_submission_rows():
    _, submissions, actions, issues, curated, _ = _canonical_pipeline()

    assert len(curated) == len(submissions)
    expected_reminders = actions.groupby("submission_id")[
        "reminder_count"
    ].sum()
    actual = curated.set_index("submission_id")
    for submission_id, reminder_count in expected_reminders.items():
        assert actual.loc[submission_id, "reminder_count"] == reminder_count


def test_unparseable_date_leaves_timing_metrics_unknown():
    _, submissions, actions, issues, _, _ = _canonical_pipeline()
    controls = normalize_control_catalog(
        load_control_catalog(
            REPO_ROOT / "data/reference/control_catalog.json"
        )
    )
    changed = submissions.copy()
    changed.loc[0, "due_date"] = "invalid-date"
    changed_issues = validate_submissions(changed, controls)

    curated = build_curated_control_status(
        changed,
        controls,
        actions,
        changed_issues,
        date(2026, 8, 15),
    )
    row = curated.loc[curated["source_row_number"] == 1].iloc[0]

    assert pd.isna(row["overdue_flag"])
    assert pd.isna(row["submission_late"])
    assert pd.isna(row["days_overdue"])
    assert pd.isna(row["days_late"])

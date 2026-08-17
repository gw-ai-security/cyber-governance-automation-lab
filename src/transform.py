from datetime import date

import pandas as pd


# Submission statuses that represent an active follow-up Action.
ACTIVE_ACTION_STATUSES = {
    "Open",
    "In Progress",
}


# Exact column order of the curated reporting dataset.
CURATED_COLUMNS = [
    "source_row_number",
    "submission_id",
    "control_id",
    "control_name",
    "business_unit",
    "owner_role",
    "owner_email",
    "frequency",
    "risk_level",
    "reporting_period",
    "due_date",
    "submission_status",
    "evidence_present",
    "submitted_at",
    "comment",
    "overdue_flag",
    "submission_late",
    "days_overdue",
    "days_late",
    "data_quality_status",
    "active_action_id",
    "active_action_status",
    "active_action_due_date",
    "reminder_count",
    "last_reminder_at",
]


def normalize_control_catalog(control_catalog: list[dict]) -> pd.DataFrame:
    """
    Convert the Control Catalog into a normalized pandas DataFrame.

    Only technical normalization is performed.
    Business meaning is not changed.
    """

    # Convert the list of Control dictionaries into tabular data.
    normalized = pd.DataFrame(control_catalog).copy()

    # Remove surrounding whitespace from string columns.
    for column in normalized.columns:
        if normalized[column].dtype == "object":
            normalized[column] = normalized[column].str.strip()

            # Convert truly empty strings into missing values.
            normalized[column] = normalized[column].replace("", pd.NA)

    return normalized


def normalize_submissions(submissions: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize raw Submission values without changing their business meaning.
    """

    # Work on a copy so the original raw DataFrame remains unchanged.
    normalized = submissions.copy()

    # Normalize every column because Extract loaded all values as strings.
    for column in normalized.columns:
        # Remove whitespace before and after each value.
        normalized[column] = normalized[column].str.strip()

        # Convert truly empty strings into pandas' missing-value representation.
        normalized[column] = normalized[column].replace("", pd.NA)

    return normalized


def normalize_actions(actions: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize raw Action values without changing their business meaning.
    """

    # Work on a copy so the original raw DataFrame remains unchanged.
    normalized = actions.copy()

    # Normalize every column because Extract loaded all values as strings.
    for column in normalized.columns:
        # Remove whitespace before and after each value.
        normalized[column] = normalized[column].str.strip()

        # Convert truly empty strings into pandas' missing-value representation.
        normalized[column] = normalized[column].replace("", pd.NA)

    # Convert reminder_count from a raw string into a nullable integer.
    normalized["reminder_count"] = pd.to_numeric(
        normalized["reminder_count"],
        errors="raise",
    ).astype("Int64")

    return normalized


def add_source_row_number(submissions: pd.DataFrame) -> pd.DataFrame:
    """
    Add the original 1-based CSV data-row number to every Submission.

    The CSV header is not counted.
    """

    # Work on a copy so the supplied DataFrame is not changed in place.
    result = submissions.copy()

    # Row 1 represents the first data row below the CSV header.
    result.insert(
        0,
        "source_row_number",
        range(1, len(result) + 1),
    )

    return result


def _parse_date_series(series: pd.Series) -> pd.Series:
    """
    Parse normalized YYYY-MM-DD strings into pandas datetime values.

    Invalid values become NaT here because Data Quality validation must
    already have recorded the corresponding problem before transformation.
    """

    return pd.to_datetime(
        series,
        format="%Y-%m-%d",
        errors="coerce",
    )


def _derive_timing_values(
    row: pd.Series,
    as_of_date: date,
) -> tuple:
    """
    Derive overdue and late metrics for one Submission.

    Non-evaluable timing states return missing values instead of creating
    misleading False or zero values.
    """

    due_date = row["_due_date_parsed"]
    submitted_at = row["_submitted_at_parsed"]

    raw_submitted_at = row["submitted_at"]

    # A missing or invalid due date makes timing calculations impossible.
    if pd.isna(due_date):
        return pd.NA, pd.NA, pd.NA, pd.NA

    # If submitted_at contains text but could not be parsed,
    # the timing state is also not safely evaluable.
    if pd.notna(raw_submitted_at) and pd.isna(submitted_at):
        return pd.NA, pd.NA, pd.NA, pd.NA

    as_of_timestamp = pd.Timestamp(as_of_date)

    # No Submission has been received yet.
    if pd.isna(submitted_at):
        overdue = as_of_timestamp > due_date

        days_overdue = (
            (as_of_timestamp - due_date).days
            if overdue
            else 0
        )

        return overdue, False, days_overdue, 0

    # A Submission exists, so it cannot still be currently overdue.
    submission_late = submitted_at > due_date

    days_late = (
        (submitted_at - due_date).days
        if submission_late
        else 0
    )

    return False, submission_late, 0, days_late


def _prepare_action_summary(actions: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate Action information to one row per Submission.

    Reminder counts include all related Actions.
    Active Action information uses Open or In Progress Actions.
    """

    # Work on a copy so the normalized Action data remains unchanged.
    working = actions.copy()

    # Parse Action dates only for transformation and aggregation.
    working["_created_at_parsed"] = _parse_date_series(
        working["created_at"]
    )

    working["_due_date_parsed"] = _parse_date_series(
        working["due_date"]
    )

    working["_last_reminder_at_parsed"] = _parse_date_series(
        working["last_reminder_at"]
    )

    # Aggregate reminder information across all Actions per Submission.
    reminder_summary = (
        working.groupby(
            "submission_id",
            dropna=False,
            as_index=False,
        )
        .agg(
            reminder_count=("reminder_count", "sum"),
            last_reminder_at=(
                "_last_reminder_at_parsed",
                "max",
            ),
        )
    )

    # Select only currently active Actions.
    active_actions = working[
        working["status"].isin(ACTIVE_ACTION_STATUSES)
    ].copy()

    # The project contract allows at most one active Action per Submission.
    # Sorting keeps the result deterministic if malformed input violates
    # that assumption.
    active_actions = active_actions.sort_values(
        by=[
            "submission_id",
            "_created_at_parsed",
            "action_id",
        ],
        na_position="last",
    )

    active_actions = active_actions.drop_duplicates(
        subset=["submission_id"],
        keep="first",
    )

    # Keep only the Action attributes required by the curated dataset.
    active_actions = active_actions[
        [
            "submission_id",
            "action_id",
            "status",
            "_due_date_parsed",
        ]
    ].rename(
        columns={
            "action_id": "active_action_id",
            "status": "active_action_status",
            "_due_date_parsed": "active_action_due_date",
        }
    )

    # Combine active Action information with reminder totals.
    action_summary = reminder_summary.merge(
        active_actions,
        on="submission_id",
        how="left",
    )

    # Convert parsed dates into plain date values.
    action_summary["last_reminder_at"] = (
        action_summary["last_reminder_at"].dt.date
    )

    action_summary["active_action_due_date"] = (
        action_summary["active_action_due_date"].dt.date
    )

    return action_summary


def build_curated_control_status(
    submissions: pd.DataFrame,
    control_catalog: pd.DataFrame,
    actions: pd.DataFrame,
    dq_issues: pd.DataFrame,
    as_of_date: date,
) -> pd.DataFrame:
    """
    Build the curated Control Status reporting dataset.

    The function preserves every raw Submission row, enriches it with
    Control and Action data, and derives reporting metrics.
    """

    # Work on a copy so earlier pipeline stages remain unchanged.
    curated = submissions.copy()

    # Preserve Submission status under its reporting-specific name.
    curated = curated.rename(
        columns={
            "status": "submission_status",
        }
    )

    # Select only Control attributes needed for reporting.
    control_columns = control_catalog[
        [
            "control_id",
            "control_name",
            "business_unit",
            "owner_role",
            "owner_email",
            "frequency",
            "risk_level",
        ]
    ].copy()

    # LEFT JOIN preserves Submissions even when control_id is unknown.
    curated = curated.merge(
        control_columns,
        on="control_id",
        how="left",
    )

    # Evidence presence is derived from the normalized source fact.
    curated["evidence_present"] = (
        curated["evidence_reference"].notna()
    )

    # Parse dates for deterministic timing calculations.
    curated["_due_date_parsed"] = _parse_date_series(
        curated["due_date"]
    )

    curated["_submitted_at_parsed"] = _parse_date_series(
        curated["submitted_at"]
    )

    # Derive overdue and late metrics row by row.
    timing_metrics = curated.apply(
        lambda row: pd.Series(
            _derive_timing_values(
                row,
                as_of_date,
            ),
            index=[
                "overdue_flag",
                "submission_late",
                "days_overdue",
                "days_late",
            ],
        ),
        axis=1,
    )

    # Add the timing metrics to the curated dataset.
    curated[
        [
            "overdue_flag",
            "submission_late",
            "days_overdue",
            "days_late",
        ]
    ] = timing_metrics

    # Convert valid parsed dates into plain Python date values.
    curated["due_date"] = (
        curated["_due_date_parsed"].dt.date
    )

    curated["submitted_at"] = (
        curated["_submitted_at_parsed"].dt.date
    )

    # Determine which original Submission rows have Data Quality Issues.
    if dq_issues.empty:
        invalid_source_rows = set()
    else:
        invalid_source_rows = set(
            dq_issues["source_row_number"]
            .dropna()
            .astype(int)
            .tolist()
        )

    # A Submission is Invalid if at least one DQ Issue references its row.
    curated["data_quality_status"] = (
        curated["source_row_number"]
        .apply(
            lambda row_number: (
                "Invalid"
                if row_number in invalid_source_rows
                else "Valid"
            )
        )
    )

    # Aggregate Action information without multiplying Submission rows.
    action_summary = _prepare_action_summary(actions)

    curated = curated.merge(
        action_summary,
        on="submission_id",
        how="left",
    )

    # Submissions without Actions have zero reminders.
    curated["reminder_count"] = (
        curated["reminder_count"]
        .fillna(0)
        .astype("Int64")
    )

    # Remove temporary technical columns.
    curated = curated.drop(
        columns=[
            "_due_date_parsed",
            "_submitted_at_parsed",
        ]
    )

    # Return only the agreed reporting columns in deterministic order.
    return curated[CURATED_COLUMNS]


def _json_safe_value(value):
    """
    Convert pandas and Python scalar values into JSON-safe values.
    """

    # Convert pandas missing values into JSON null.
    if pd.isna(value):
        return None

    # Convert Python dates into ISO strings.
    if isinstance(value, date):
        return value.isoformat()

    # Convert numpy scalar values into normal Python scalar values.
    if hasattr(value, "item"):
        return value.item()

    return value


def build_ai_review_queue(
    curated: pd.DataFrame,
    as_of_date: date,
) -> dict:
    """
    Build the controlled AI review queue.

    Only valid Non-Compliant or currently overdue Submissions are included.
    """

    # Only Data Quality-valid records may enter the AI review queue.
    valid_records = curated[
        curated["data_quality_status"] == "Valid"
    ].copy()

    # Determine which records match the AI review policy.
    non_compliant = (
        valid_records["submission_status"] == "Non-Compliant"
    )

    overdue = (
        valid_records["overdue_flag"]
        .eq(True)
        .fillna(False)
    )

    queue_records = valid_records[
        non_compliant | overdue
    ].copy()

    items = []

    # Build one minimized AI-review payload per selected Submission.
    for _, row in queue_records.iterrows():
        review_reasons = []

        if row["submission_status"] == "Non-Compliant":
            review_reasons.append("Non-Compliant")

        if (
            pd.notna(row["overdue_flag"])
            and bool(row["overdue_flag"])
        ):
            review_reasons.append("Overdue")

        item = {
            "submission_id": _json_safe_value(
                row["submission_id"]
            ),
            "control_id": _json_safe_value(
                row["control_id"]
            ),
            "control_name": _json_safe_value(
                row["control_name"]
            ),
            "business_unit": _json_safe_value(
                row["business_unit"]
            ),
            "risk_level": _json_safe_value(
                row["risk_level"]
            ),
            "reporting_period": _json_safe_value(
                row["reporting_period"]
            ),
            "submission_status": _json_safe_value(
                row["submission_status"]
            ),
            "due_date": _json_safe_value(
                row["due_date"]
            ),
            "evidence_present": _json_safe_value(
                row["evidence_present"]
            ),
            "days_overdue": _json_safe_value(
                row["days_overdue"]
            ),
            "comment": _json_safe_value(
                row["comment"]
            ),
            "review_reasons": review_reasons,
        }

        items.append(item)

    # Return the complete minimized AI queue structure.
    return {
        "as_of_date": as_of_date.isoformat(),
        "items": items,
    }
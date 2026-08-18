import re
from datetime import date

import pandas as pd


# Exact output schema for Data Quality Issue records.
DQ_ISSUE_COLUMNS = [
    "issue_id",
    "submission_id",
    "control_id",
    "source_row_number",
    "rule",
    "severity",
    "field",
    "message",
]


# These Submission fields are required by DQ-001.
REQUIRED_SUBMISSION_FIELDS = [
    "submission_id",
    "control_id",
    "reporting_period",
    "due_date",
    "status",
]


# Exact allowed Submission status values.
ALLOWED_SUBMISSION_STATUSES = {
    "Not Submitted",
    "In Review",
    "Compliant",
    "Non-Compliant",
}


# These statuses require submitted evidence.
REVIEWED_SUBMISSION_STATUSES = {
    "In Review",
    "Compliant",
    "Non-Compliant",
}


# Deterministic rule order for the final DQ output.
RULE_ORDER = {
    "DQ-001 Missing Required Field": 1,
    "DQ-002 Unknown Control ID": 2,
    "DQ-003 Invalid Status": 3,
    "DQ-004 Missing Evidence": 4,
    "DQ-005 Duplicate Submission": 5,
    "DQ-006 Invalid Reporting Period": 6,
    "DQ-007 Invalid Due Date": 7,
    "DQ-008 Invalid Submission State": 8,
    "DQ-009 Invalid Evidence State": 9,
    "DQ-010 Invalid Submitter Email": 10,
}


def _append_issue(
    issues: list,
    row: pd.Series,
    rule: str,
    severity: str,
    field: str,
    message: str,
) -> None:
    """
    Add one Data Quality Issue to the issue collection.
    """

    issues.append(
        {
            "issue_id": None,
            "submission_id": row["submission_id"],
            "control_id": row["control_id"],
            "source_row_number": row["source_row_number"],
            "rule": rule,
            "severity": severity,
            "field": field,
            "message": message,
        }
    )


def _is_valid_reporting_period(
    reporting_period,
    frequency,
) -> bool:
    """
    Check whether a reporting period matches the Control frequency.
    """

    if not isinstance(reporting_period, str):
        return False

    if frequency == "Monthly":
        pattern = r"\d{4}-(0[1-9]|1[0-2])"

    elif frequency == "Quarterly":
        pattern = r"\d{4}-Q[1-4]"

    elif frequency == "Annual":
        pattern = r"\d{4}"

    else:
        return False

    return re.fullmatch(
        pattern,
        reporting_period,
    ) is not None


def _expected_due_date(
    reporting_period: str,
    frequency: str,
):
    """
    Calculate the expected due date from reporting period and frequency.

    Monthly:
        10th calendar day of the following month.

    Quarterly:
        10th calendar day after quarter end.

    Annual:
        January 31 of the following year.
    """

    try:
        if frequency == "Monthly":
            year = int(reporting_period[:4])
            month = int(reporting_period[5:7])

            if month == 12:
                return date(
                    year + 1,
                    1,
                    10,
                )

            return date(
                year,
                month + 1,
                10,
            )

        if frequency == "Quarterly":
            year = int(reporting_period[:4])
            quarter = int(reporting_period[-1])

            if quarter == 1:
                return date(year, 4, 10)

            if quarter == 2:
                return date(year, 7, 10)

            if quarter == 3:
                return date(year, 10, 10)

            if quarter == 4:
                return date(
                    year + 1,
                    1,
                    10,
                )

        if frequency == "Annual":
            year = int(reporting_period)

            return date(
                year + 1,
                1,
                31,
            )

    except (ValueError, OverflowError):
        return None

    return None


def _parse_iso_date(value):
    """
    Parse a strict YYYY-MM-DD value.

    Invalid or missing values return None.
    """

    if pd.isna(value):
        return None

    # Already parsed date values are accepted.
    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        return None

    # Enforce the exact physical YYYY-MM-DD representation.
    if re.fullmatch(
        r"\d{4}-\d{2}-\d{2}",
        value,
    ) is None:
        return None

    try:
        return date.fromisoformat(value)

    except ValueError:
        return None


def validate_submissions(
    submissions: pd.DataFrame,
    control_catalog: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate normalized Submission data and return Data Quality Issues.

    The function implements DQ-001 through DQ-010.

    Submission data is never silently repaired, deleted, or deduplicated.
    """

    # Store all detected Data Quality Issues as dictionaries.
    issues = []

    # Collect all known Control IDs for referential-integrity checks.
    known_control_ids = set(
        control_catalog["control_id"].dropna()
    )

    # Map every Control ID to its reporting frequency.
    control_frequencies = dict(
        zip(
            control_catalog["control_id"],
            control_catalog["frequency"],
        )
    )

    # Identify all rows participating in duplicate submission_id values.
    duplicate_submission_mask = (
        submissions["submission_id"].notna()
        & submissions["submission_id"].duplicated(
            keep=False
        )
    )

    duplicate_submission_rows = set(
        submissions.loc[
            duplicate_submission_mask,
            "source_row_number",
        ]
    )

    # Identify all rows participating in duplicate business keys.
    business_key_available = (
        submissions["control_id"].notna()
        & submissions["reporting_period"].notna()
    )

    duplicate_business_key_mask = (
        business_key_available
        & submissions.duplicated(
            subset=[
                "control_id",
                "reporting_period",
            ],
            keep=False,
        )
    )

    duplicate_business_key_rows = set(
        submissions.loc[
            duplicate_business_key_mask,
            "source_row_number",
        ]
    )

    # Validate every Submission row independently.
    for _, row in submissions.iterrows():

        control_id = row["control_id"]
        status = row["status"]
        reporting_period = row["reporting_period"]
        due_date = row["due_date"]
        evidence_reference = row["evidence_reference"]
        submitted_at = row["submitted_at"]
        submitted_by = row["submitted_by"]
        source_row_number = row["source_row_number"]

        # ---------------------------------------------------------
        # DQ-001 Missing Required Field
        # ---------------------------------------------------------

        missing_fields = [
            field
            for field in REQUIRED_SUBMISSION_FIELDS
            if pd.isna(row[field])
        ]

        if missing_fields:
            field_text = ",".join(
                missing_fields
            )

            message_fields = ", ".join(
                missing_fields
            )

            _append_issue(
                issues=issues,
                row=row,
                rule="DQ-001 Missing Required Field",
                severity="High",
                field=field_text,
                message=(
                    f"Required field(s) missing: "
                    f"{message_fields}."
                ),
            )

        # Determine whether the Control reference can be resolved.
        control_resolved = (
            pd.notna(control_id)
            and control_id in known_control_ids
        )

        # ---------------------------------------------------------
        # DQ-002 Unknown Control ID
        # ---------------------------------------------------------

        if (
            pd.notna(control_id)
            and not control_resolved
        ):
            _append_issue(
                issues=issues,
                row=row,
                rule="DQ-002 Unknown Control ID",
                severity="High",
                field="control_id",
                message=(
                    f"Unknown control_id: {control_id}."
                ),
            )

        # Determine whether the Submission status is valid.
        status_valid = (
            pd.notna(status)
            and status in ALLOWED_SUBMISSION_STATUSES
        )

        # ---------------------------------------------------------
        # DQ-003 Invalid Status
        # ---------------------------------------------------------

        if (
            pd.notna(status)
            and not status_valid
        ):
            _append_issue(
                issues=issues,
                row=row,
                rule="DQ-003 Invalid Status",
                severity="High",
                field="status",
                message=(
                    f"Invalid submission status: {status}."
                ),
            )

        # ---------------------------------------------------------
        # DQ-004 Missing Evidence
        # ---------------------------------------------------------

        if (
            status_valid
            and status in REVIEWED_SUBMISSION_STATUSES
            and pd.isna(evidence_reference)
        ):
            _append_issue(
                issues=issues,
                row=row,
                rule="DQ-004 Missing Evidence",
                severity="High",
                field="evidence_reference",
                message=(
                    "Evidence reference is required "
                    f"when status is {status}."
                ),
            )

        # ---------------------------------------------------------
        # DQ-005 Duplicate Submission
        # ---------------------------------------------------------

        duplicate_fields = []
        duplicate_reasons = []

        if source_row_number in duplicate_submission_rows:
            duplicate_fields.append(
                "submission_id"
            )

            duplicate_reasons.append(
                "duplicate submission_id"
            )

        if source_row_number in duplicate_business_key_rows:
            duplicate_fields.extend(
                [
                    "control_id",
                    "reporting_period",
                ]
            )

            duplicate_reasons.append(
                "duplicate control_id + reporting_period"
            )

        if duplicate_fields:
            # Remove repeated field names while preserving order.
            unique_duplicate_fields = list(
                dict.fromkeys(
                    duplicate_fields
                )
            )

            _append_issue(
                issues=issues,
                row=row,
                rule="DQ-005 Duplicate Submission",
                severity="High",
                field=",".join(
                    unique_duplicate_fields
                ),
                message=(
                    "Duplicate Submission detected: "
                    + "; ".join(duplicate_reasons)
                    + "."
                ),
            )

        # ---------------------------------------------------------
        # DQ-006 Invalid Reporting Period
        # ---------------------------------------------------------

        reporting_period_valid = False
        frequency = None

        if (
            control_resolved
            and pd.notna(reporting_period)
        ):
            frequency = control_frequencies.get(
                control_id
            )

            reporting_period_valid = (
                _is_valid_reporting_period(
                    reporting_period,
                    frequency,
                )
            )

            if not reporting_period_valid:
                _append_issue(
                    issues=issues,
                    row=row,
                    rule="DQ-006 Invalid Reporting Period",
                    severity="Medium",
                    field="reporting_period",
                    message=(
                        f"Reporting period "
                        f"{reporting_period} does not match "
                        f"Control frequency {frequency}."
                    ),
                )

        # ---------------------------------------------------------
        # DQ-007 Invalid Due Date
        # ---------------------------------------------------------

        if (
            control_resolved
            and reporting_period_valid
            and pd.notna(due_date)
        ):
            expected_due_date = (
                _expected_due_date(
                    reporting_period,
                    frequency,
                )
            )

            actual_due_date = (
                _parse_iso_date(
                    due_date
                )
            )

            if (
                expected_due_date is not None
                and actual_due_date != expected_due_date
            ):
                _append_issue(
                    issues=issues,
                    row=row,
                    rule="DQ-007 Invalid Due Date",
                    severity="High",
                    field="due_date",
                    message=(
                        f"Invalid due_date {due_date}; "
                        f"expected "
                        f"{expected_due_date.isoformat()}."
                    ),
                )

        # ---------------------------------------------------------
        # DQ-008 Invalid Submission State
        # ---------------------------------------------------------

        invalid_state_fields = []

        if status_valid:

            if status == "Not Submitted":

                if pd.notna(submitted_at):
                    invalid_state_fields.append(
                        "submitted_at"
                    )

                if pd.notna(submitted_by):
                    invalid_state_fields.append(
                        "submitted_by"
                    )

            elif status in REVIEWED_SUBMISSION_STATUSES:

                if pd.isna(submitted_at):
                    invalid_state_fields.append(
                        "submitted_at"
                    )

        if invalid_state_fields:
            _append_issue(
                issues=issues,
                row=row,
                rule="DQ-008 Invalid Submission State",
                severity="High",
                field=",".join(
                    invalid_state_fields
                ),
                message=(
                    "Submission fields are inconsistent "
                    f"with status {status}: "
                    + ", ".join(invalid_state_fields)
                    + "."
                ),
            )

        # ---------------------------------------------------------
        # DQ-009 Invalid Evidence State
        # ---------------------------------------------------------

        if (
            status_valid
            and status == "Not Submitted"
            and pd.notna(evidence_reference)
        ):
            _append_issue(
                issues=issues,
                row=row,
                rule="DQ-009 Invalid Evidence State",
                severity="Medium",
                field="evidence_reference",
                message=(
                    "Evidence reference must be empty "
                    "when status is Not Submitted."
                ),
            )

        # ---------------------------------------------------------
        # DQ-010 Invalid Submitter Email
        # ---------------------------------------------------------

        if pd.notna(submitted_at):

            submitter_valid = (
                pd.notna(submitted_by)
                and "@"
                in str(submitted_by)
            )

            if not submitter_valid:
                _append_issue(
                    issues=issues,
                    row=row,
                    rule="DQ-010 Invalid Submitter Email",
                    severity="Medium",
                    field="submitted_by",
                    message=(
                        "submitted_by must be present "
                        "and contain '@' when "
                        "submitted_at is present."
                    ),
                )

    # Create the Data Quality Issue DataFrame.
    dq_issues = pd.DataFrame(
        issues,
        columns=DQ_ISSUE_COLUMNS,
    )

    # Return the correct empty schema when no issues exist.
    if dq_issues.empty:
        return dq_issues

    # Add a temporary rule-order value for deterministic sorting.
    dq_issues["_rule_order"] = (
        dq_issues["rule"].map(
            RULE_ORDER
        )
    )

    # Sort first by raw source row and then by DQ rule number.
    dq_issues = (
        dq_issues.sort_values(
            by=[
                "source_row_number",
                "_rule_order",
            ],
            kind="stable",
        )
        .reset_index(drop=True)
    )

    # Assign deterministic IDs only after final sorting.
    dq_issues["issue_id"] = [
        f"DQI-{index:04d}"
        for index in range(
            1,
            len(dq_issues) + 1,
        )
    ]

    # Remove the temporary internal sorting column.
    dq_issues = dq_issues.drop(
        columns=[
            "_rule_order",
        ]
    )

    # Return only the exact contractual output columns.
    return dq_issues[
        DQ_ISSUE_COLUMNS
    ]
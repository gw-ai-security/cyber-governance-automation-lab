# Data Quality Rules

## Purpose

This document defines the data quality rule catalog for the Cyber Governance Automation Lab. It documents the checks applied to submission data before it is used for reporting, without implementing them.

## Data Quality Principles

* Data quality rules validate the structure, referential integrity, and consistency of submitted data.
* Data quality rules do not evaluate whether a control is compliant, on time, or effective — those are separate business concepts.
* A data quality issue is a flag for review, not an automatic correction. Rules never silently change a submission's status.
* Rules are grouped by category: completeness, referential integrity, validity, consistency, and uniqueness.

## Rule Summary

| Rule | Category | Severity |
| --- | --- | --- |
| DQ-001 Missing Required Field | Completeness | High |
| DQ-002 Unknown Control ID | Referential Integrity | High |
| DQ-003 Invalid Status | Validity | High |
| DQ-004 Missing Evidence | Consistency | High |
| DQ-005 Duplicate Submission | Uniqueness | High |
| DQ-006 Invalid Reporting Period | Validity | Medium |
| DQ-007 Invalid Due Date | Validity | High |
| DQ-008 Invalid Submission State | Consistency | High |
| DQ-009 Invalid Evidence State | Consistency | Medium |
| DQ-010 Invalid Owner Email | Validity | Medium |

## DQ-001 Missing Required Field

**Category:** Completeness

Required fields:

```text
submission_id
control_id
reporting_period
due_date
status
```

**Severity:** High

## DQ-002 Unknown Control ID

**Category:** Referential Integrity

Condition:

```text
submission.control_id
must exist in
control.control_id
```

**Severity:** High

## DQ-003 Invalid Status

Allowed:

```text
Not Submitted
In Review
Compliant
Non-Compliant
```

Invalid examples:

```text
Open
Pending
Done
OK
Complete
compliant
```

**Severity:** High

## DQ-004 Missing Evidence

Condition:

```text
status = Compliant
AND
evidence_reference is null or empty
```

**Severity:** High

This rule does not automatically change the status to `Non-Compliant`. It is flagged as a data quality conflict for review, not resolved automatically.

## DQ-005 Duplicate Submission

Unique business key:

```text
control_id + reporting_period
```

**Severity:** High

## DQ-006 Invalid Reporting Period

Valid patterns:

```text
Monthly   -> YYYY-MM
Quarterly -> YYYY-Q1 ... YYYY-Q4
Annual    -> YYYY
```

The frequency of the related control and the format of the reporting period must match.

**Severity:** Medium

## DQ-007 Invalid Due Date

The due date must match the due-date rule defined for the control's frequency in [business_process.md](business_process.md#due-date-logic).

**Severity:** High

## DQ-008 Invalid Submission State

Rules:

```text
Not Submitted
-> submitted_at must be null
```

```text
In Review
Compliant
Non-Compliant
-> submitted_at must be present
```

**Severity:** High

## DQ-009 Invalid Evidence State

Rule:

```text
status = Not Submitted
-> evidence_reference must be null
```

**Severity:** Medium

## DQ-010 Invalid Owner Email

For this proof of concept, only a simple plausibility check is documented:

```text
value exists
AND
contains "@"
```

This is not a full RFC email validation.

**Severity:** Medium

## Severity Model

Data quality severity uses exactly:

```text
High
Medium
Low
```

There is no `Critical` severity for data quality issues. A control's `risk_level` (Low, Medium, High, Critical) and a data quality issue's `severity` (High, Medium, Low) are two different concepts and are not interchangeable.

## Data Quality Issue Output

Each triggered rule produces a Data Quality Issue record, as defined in [data_model.md](data_model.md#data-quality-issue):

```text
issue_id
submission_id
control_id
rule
severity
field
message
```

## Out of Scope

The following are explicitly not data quality errors:

```text
Non-Compliant
is NOT a data-quality error.
```

```text
Overdue
is NOT a data-quality error.
```

```text
Late Submission
is NOT a data-quality error.
```

These distinctions matter because they point to different types of problems:

```text
Missing control_id
-> Data Problem

Submission 12 days overdue
-> Process Problem

Backup recovery failed
-> Security / Control Problem
```

Data quality rules validate the shape and consistency of the data. They do not judge whether a control is effective, whether a deadline was met, or whether a security outcome was acceptable — those are governance and process concerns, handled elsewhere in this documentation.

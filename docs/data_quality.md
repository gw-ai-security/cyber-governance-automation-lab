# Data Quality Rules

## Document Role

**CURRENT-STATE FOUNDATION DOCUMENT — CURRENT THROUGH PHASE 10**

Documentation index: [README.md](README.md)

## Purpose

This document defines the implementation-independent Data Quality rule catalog for the Cyber Governance Automation Lab. Executable checks are implemented in `src/validate.py` and verified by the automated test suite.

Phase 10 does not add, execute, redefine, or renumber any Data Quality rule.

## 1. Data Quality Principles

- Data Quality rules validate the structure, referential integrity, validity, and consistency of Submission data.
- Data Quality rules do not evaluate compliance, timeliness, Control effectiveness, or AI review priority.
- A Data Quality Issue is a finding for review, not an automatic correction.
- Source facts are never silently repaired by a DQ rule.
- Dependent checks are not evaluated when prerequisite reference/state information is unavailable.

## 2. Rule Summary

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
| DQ-010 Invalid Submitter Email | Validity | Medium |

The catalog is exactly:

```text
DQ-001 through DQ-010
```

There is no DQ-011.

## 3. DQ-001 Missing Required Field

Required fields:

```text
submission_id
control_id
reporting_period
due_date
status
```

**Category:** Completeness  
**Severity:** High

## 4. DQ-002 Unknown Control ID

Condition:

```text
submission.control_id
must exist in
control.control_id
```

**Category:** Referential Integrity  
**Severity:** High

## 5. DQ-003 Invalid Status

Allowed Submission statuses:

```text
Not Submitted
In Review
Compliant
Non-Compliant
```

Invalid examples include `Open`, `Pending`, `Done`, `OK`, `Complete`, or case-mismatched values such as `compliant`.

**Category:** Validity  
**Severity:** High

## 6. DQ-004 Missing Evidence

Condition:

```text
status IN (
  In Review,
  Compliant,
  Non-Compliant
)
AND
evidence_reference is null or empty
```

Evidence must be present once a Submission enters review and for either final assessment outcome. A `Non-Compliant` result represents a reviewed control outcome; it does not mean evidence is missing.

**Category:** Consistency  
**Severity:** High

## 7. DQ-005 Duplicate Submission

DQ-005 enforces two separate uniqueness invariants:

```text
Technical identifier uniqueness:
submission_id

Business uniqueness:
control_id + reporting_period
```

DQ-005 is triggered when either invariant is duplicated. When both invariants overlap for one source row, the deterministic implementation emits one DQ-005 issue for that row rather than duplicate findings for the same rule.

**Category:** Uniqueness  
**Severity:** High

## 8. DQ-006 Invalid Reporting Period

Valid patterns:

```text
Monthly   → YYYY-MM
Quarterly → YYYY-Q1 ... YYYY-Q4
Annual    → YYYY
```

The related Control frequency and reporting-period format must match.

**Category:** Validity  
**Severity:** Medium

## 9. DQ-007 Invalid Due Date

The due date must match the synthetic due-date rule defined for the related Control frequency in [business_process.md](business_process.md#7-reporting-periods-and-synthetic-due-dates).

If the related Control cannot be resolved, this dependent rule is not evaluated rather than being automatically failed.

**Category:** Validity  
**Severity:** High

## 10. DQ-008 Invalid Submission State

Rules:

```text
Not Submitted
→ submitted_at must be null
→ submitted_by must be null
```

```text
In Review
Compliant
Non-Compliant
→ submitted_at must be present
```

The `submitted_by must be null` condition for `Not Submitted` prevents a submitter identity from existing when no submission has occurred. The reverse requirement is covered by DQ-010.

**Category:** Consistency  
**Severity:** High

## 11. DQ-009 Invalid Evidence State

Rule:

```text
status = Not Submitted
→ evidence_reference must be null
```

Together, DQ-004 and DQ-009 define the evidence-state relationship across the Submission lifecycle.

**Category:** Consistency  
**Severity:** Medium

## 12. DQ-010 Invalid Submitter Email

DQ-010 applies to `submitted_by` when `submitted_at` is present.

PoC plausibility rule:

```text
value exists
AND
contains "@"
```

This is not full RFC e-mail validation.

DQ-010 validates the Submission `submitted_by` field. It does not validate Control `owner_email`; all ten DQ rules intentionally operate at Submission-row level.

**Category:** Validity  
**Severity:** Medium

## 13. Severity Model

Data Quality severity uses exactly:

```text
High
Medium
Low
```

There is no `Critical` DQ severity.

```text
Control risk_level ∈ {Low, Medium, High, Critical}
DQ severity        ∈ {Low, Medium, High}
```

These are separate concepts and must not be mapped implicitly.

## 14. Rule Evaluation Order and Dependencies

Conceptual evaluation order:

1. completeness,
2. referential integrity,
3. basic validity,
4. cross-field consistency,
5. derived/downstream evaluation.

Dependent rules must not create misleading secondary failures when a prerequisite cannot be evaluated.

Example:

```text
control_id = CTRL-999
→ DQ-002 Unknown Control ID
→ DQ-006 / DQ-007 not evaluated because Control frequency is unavailable
```

`Not Evaluated` is evaluation behavior, not a DQ status, severity, or additional rule. It does not create a Data Quality Issue record.

A row may legitimately trigger multiple independent rules when each rule can be evaluated.

## 15. Data Quality Issue Output

Each triggered rule produces a Data Quality Issue with:

```text
issue_id
submission_id
control_id
source_row_number
rule
severity
field
message
```

`submission_id` and `control_id` can be null when the corresponding source identifier is missing. `source_row_number` preserves one-based raw-row traceability.

## 16. Out of Scope

The following are explicitly not Data Quality errors:

```text
Non-Compliant
Overdue
Late Submission
```

Example distinction:

```text
Missing control_id
→ Data problem

Submission 12 days overdue
→ Process problem

Backup recovery failed
→ Security / Control problem
```

Phase 10 REST transport errors are also not DQ rules:

```text
CONTROL_NOT_FOUND
CONTROL_SOURCE_ERROR
ApiClientError
```

They are integration/HTTP outcomes and must not be relabeled as DQ-011 or any other new DQ rule.

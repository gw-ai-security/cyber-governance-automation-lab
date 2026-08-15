# Phase 2 Dataset Coverage

## Purpose

The Phase 2 synthetic governance dataset intentionally combines valid records, invalid Data Quality records, valid process exceptions, valid `Non-Compliant` security outcomes, and follow-up Action records. This document provides the deterministic validation matrix for those scenarios; it is not implementation code.

The fixed reference date for deterministic overdue reasoning is:

```text
as_of_date = 2026-08-15
```

`as_of_date` is an evaluation parameter and is not stored in either raw CSV dataset.

## Dataset Inventory

| Dataset | Count | File |
| --- | ---: | --- |
| Controls | 5 | `data/reference/control_catalog.json` |
| Submissions | 15 | `data/raw/evidence_submissions.csv` |
| Actions | 5 | `data/raw/actions.csv` |

## Submission Scenario Matrix

| Submission | Control | Period | Expected classification | Expected DQ issue | Process / governance meaning |
| --- | --- | --- | --- | --- | --- |
| SUB-001 | CTRL-001 | 2026-Q1 | Valid | None | On-time Compliant Submission with reviewed evidence. |
| SUB-002 | CTRL-001 | 2026-Q2 | Invalid | DQ-004 Missing Evidence | Compliant status with an intentionally missing evidence reference. |
| SUB-003 | CTRL-001 | 2026-Q3 | Valid | None | Not Submitted but not yet due as of the reference date. |
| SUB-004 | CTRL-002 | 2026-Q1 | Valid | None | Late Submission, received 2 calendar days after its due date; lateness is not a DQ error. |
| SUB-005 | CTRL-002 | 2026-Q2 | Valid | None | Non-Compliant security/control outcome; non-compliance is not a DQ error. |
| SUB-006 | CTRL-002 | 2026-Q3 | Invalid | DQ-003 Invalid Status | Intentionally uses `Pending`, which is not a valid Submission status. |
| SUB-007 | CTRL-003 | 2026-Q1 | Valid | None | On-time Compliant recovery-test Submission. |
| SUB-008 | CTRL-003 | 2026-Q2 | Invalid due to duplicate business key | DQ-005 Duplicate Submission | First row in the intentional `CTRL-003 + 2026-Q2` duplicate pair. |
| SUB-009 | CTRL-003 | 2026-Q2 | Invalid due to duplicate business key | DQ-005 Duplicate Submission | Second row in the intentional `CTRL-003 + 2026-Q2` duplicate pair. |
| SUB-010 | CTRL-003 | 2026-Q3 | Valid | None | Not Submitted but not yet due as of the reference date. |
| SUB-011 | CTRL-004 | 2025 | Valid | None | On-time annual Compliant Submission. |
| SUB-012 | CTRL-004 | 2026 | Valid | None | Annual period remains open and is not overdue. |
| SUB-013 | CTRL-005 | 2026-06 | Valid | None | On-time monthly Compliant Submission. |
| SUB-014 | CTRL-005 | 2026-07 | Valid | None | Overdue process exception, 5 calendar days overdue as of 2026-08-15; overdue is not a DQ error. |
| SUB-015 | CTRL-999 | 2026-Q2 | Invalid | DQ-002 Unknown Control ID | Intentional unresolved Control reference. DQ-006 and DQ-007 are not evaluated because Control frequency cannot be resolved. |

For SUB-015, DQ-006 Invalid Reporting Period and DQ-007 Invalid Due Date are `not evaluated`, rather than failed, because `CTRL-999` does not provide resolvable Control frequency reference data.

## Intentional Data Quality Coverage

| Rule | Failure | Submission coverage |
| --- | --- | --- |
| DQ-002 | Unknown Control ID | SUB-015 |
| DQ-003 | Invalid Status | SUB-006 |
| DQ-004 | Missing Evidence | SUB-002 |
| DQ-005 | Duplicate Submission business key | SUB-008 and SUB-009 |

Phase 2 does not deliberately create failing examples for every rule DQ-001 through DQ-010. Rules without a deliberately failing dataset example remain part of the canonical rule catalog and will be tested through validation logic and unit tests in later phases. No additional invalid Submission records are added merely to trigger every rule.

## Non-DQ Business / Process Coverage

| Submission | Scenario | Expected meaning |
| --- | --- | --- |
| SUB-004 | Late by 2 calendar days | Process exception; not a Data Quality error. |
| SUB-005 | Non-Compliant | Security/control outcome; not a Data Quality error. |
| SUB-014 | Overdue by 5 calendar days as of 2026-08-15 | Process exception; not a Data Quality error. |

The dataset explicitly preserves:

```text
Data Problem
!=
Process Problem
!=
Security / Control Problem
```

## Action Coverage

| Action | Status | Submission | Purpose |
| --- | --- | --- | --- |
| ACT-001 | Open | SUB-014 | Open overdue-submission follow-up with reminder tracking. |
| ACT-002 | In Progress | SUB-005 | Remediation Action for a Non-Compliant Submission. |
| ACT-003 | Completed | SUB-004 | Completed missing-submission follow-up after evidence arrived and the Submission moved to In Review. |
| ACT-004 | Open | SUB-002 | Missing-evidence Data Quality follow-up without changing the intentional raw error. |
| ACT-005 | Open | SUB-006 | Invalid-status correction Action without changing the intentional raw error. |

The Action dataset covers:

* all Action statuses: `Open`, `In Progress`, and `Completed`,
* `reminder_count = 0` and `reminder_count > 0`,
* empty and populated `last_reminder_at`,
* the synthetic `due_date = created_at + 7 calendar days` rule,
* Action-to-Submission Control consistency, and
* at most one non-completed Action per Submission.

Action completion and Submission compliance remain independent. ACT-003 completes the task of obtaining a missing Submission; it does not assign `Compliant` status to SUB-004.

## Phase 2 Scope Boundaries

Phase 2 does not:

* implement Python validation,
* generate Data Quality Issue output files,
* generate curated reporting datasets,
* calculate or store derived metrics,
* implement Power Automate,
* implement Power BI, or
* implement AI workflows.

Those capabilities belong to later phases.

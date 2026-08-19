# Phase 4 Test Acceptance

## Purpose

Phase 4 verifies and hardens the Phase 3 Python pipeline through focused,
deterministic tests. It does not add business functionality, rules, schemas,
dependencies, or infrastructure.

## Scope

The review covered the repository contracts, canonical synthetic datasets,
all pipeline modules, and the complete existing test suite. Existing tests
were retained where they already protected a contract. New tests were added
only for meaningful uncovered invariants and boundary conditions.

## Baseline

- Starting branch: `main`
- Starting commit: `9b9d25054a9f475af4f7308ad4adbe5dd310ba09`
- Baseline command: `python -m pytest -q`
- Baseline result: `35 passed`

## Business-Rule Coverage

| Area | Acceptance coverage |
| --- | --- |
| DQ-001 | Missing required fields and deterministic aggregation of multiple missing fields into one finding |
| DQ-002 to DQ-004 | Unknown Control dependency handling, exact Submission statuses, and evidence requirements |
| DQ-005 | Technical-key duplicates, business-key duplicates, every participating row, and one finding per row when both invariants overlap |
| DQ-006 and DQ-007 | Frequency-specific reporting periods, derived due dates, and prerequisite-based rule skipping |
| DQ-008 to DQ-010 | Both sides of Submission-state consistency, evidence-state consistency, and malformed or missing submitters |
| DQ output | One-based lineage, deterministic source-row/rule ordering, deterministic issue IDs, and exact schema |
| Timing | Positive overdue/late cases, equality boundaries, and unknown results for non-evaluable dates |
| Curated data | Exact schema, source-row preservation, unknown-Control preservation, and Action aggregation without row multiplication |
| AI queue | Valid-record filtering, canonical selection, exact field set, source order, and data minimization |
| Serialization and CLI | Exact CSV/strict JSON serialization, deterministic date input, invalid-date rejection, fatal input behavior, and end-to-end output generation |

## New Tests Added

| Test | Protection added |
| --- | --- |
| `test_duplicate_submission_id_flags_every_participating_row_independently` | Proves technical-key duplication independently of the business key |
| `test_combined_duplicate_invariants_emit_one_issue_per_source_row` | Prevents duplicate DQ-005 records when both uniqueness invariants apply |
| `test_multiple_missing_required_fields_emit_one_deterministic_issue` | Protects one DQ-001 finding with stable field and message ordering |
| `test_reviewed_submission_without_submitted_at_triggers_dq_008_only` | Protects the reviewed-state requirement without manufacturing another rule |
| `test_submitted_timestamp_without_submitter_triggers_dq_010_only` | Protects the missing-submitter side of DQ-010 |
| `test_submission_due_on_as_of_date_is_not_overdue` | Protects the strict `as_of_date > due_date` boundary |
| `test_submission_received_on_due_date_is_not_late` | Protects the strict `submitted_at > due_date` boundary |

The existing deterministic issue-order test was also strengthened to assert
the exact rule order for multiple findings on one source row.

## Production Defects Found

None. The added tests passed against the existing Phase 3 production code, so
no files under `src/` were changed.

## Final Acceptance Result

- Focused validation and transformation tests: `26 passed`
- Complete suite: `42 passed`
- Canonical inventory: 5 Controls, 15 Submissions, 5 Actions
- Canonical result: 5 DQ issues, 10 Valid, 5 Invalid
- Canonical AI review queue: `SUB-005`, `SUB-014`
- Curated row count: 15

Phase 4 is accepted. The Phase 3 business rules, public schemas, canonical
source data, and output semantics remain unchanged.

## Intentional Limitations and Out of Scope

- This remains a flat-file portfolio proof of concept, not a production or
  enterprise platform.
- Action-specific DQ rule IDs and semantic Action validation remain out of
  scope.
- Power Automate, Power BI, external AI execution, APIs, authentication,
  databases, cloud infrastructure, and CI/CD are not implemented by Phase 4.
- No coverage-percentage, certification, or regulatory-compliance claim is
  made.

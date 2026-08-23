# Data Contract

## Purpose

This document defines the physical data contracts used by the Cyber Governance Automation Lab and the boundary between deterministic repository fixtures and private operational Phase 7 snapshots.

Logical entities, relationships, status models, and derived-state semantics remain defined in [data_model.md](data_model.md). Data Quality rules remain defined in [data_quality.md](data_quality.md).

## 1. Data-Plane Rule

The project maintains two distinct physical data planes:

```text
Canonical repository fixtures
!=
Operational Microsoft 365 state
```

Canonical data exists for reproducible engineering acceptance. Operational data evolves through Phase 5–7 workflow execution.

Phase 7 connects these planes through explicit private snapshot files. It does **not** overwrite canonical files.

## 2. Canonical Repository Inputs

Canonical files:

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

The deterministic acceptance baseline uses:

```text
as_of_date = 2026-08-15
```

Canonical inventory:

```text
Controls:    5
Submissions: 15
Actions:     5
```

All canonical identities and e-mail addresses are synthetic.

## 3. Common CSV Rules

Submission and Action CSV contracts use:

| Property | Contract |
| --- | --- |
| Encoding | UTF-8 |
| Delimiter | comma |
| Header | required |
| Dates | `YYYY-MM-DD` |
| Missing values | empty CSV field |
| Quoting | standard CSV double-quote escaping |
| Column set | exact |
| Column order | exact |

Literal strings such as:

```text
NULL
null
None
N/A
```

must not be used to represent a genuinely missing value.

Fields containing commas, quotes, or line breaks use normal CSV quoting rules.

## 4. Control Catalog Contract

Canonical reference file:

```text
data/reference/control_catalog.json
```

Phase 7 operational snapshot:

```text
security_control_snapshot_<snapshot_id>.json
```

Physical representation:

```text
UTF-8 JSON top-level array
```

Each Control contains exactly:

```text
control_id
control_name
control_statement
business_unit
owner_role
owner_email
frequency
risk_level
```

The operational snapshot may contain reachable operational ownership information and therefore remains private.

## 5. Submission Contract

Canonical file:

```text
data/raw/evidence_submissions.csv
```

Phase 7 operational snapshot:

```text
security_submission_snapshot_<snapshot_id>.csv
```

Exact column order:

```text
submission_id
control_id
reporting_period
due_date
status
evidence_reference
submitted_at
submitted_by
comment
```

Exact header:

```csv
submission_id,control_id,reporting_period,due_date,status,evidence_reference,submitted_at,submitted_by,comment
```

Physical rules:

- `due_date` uses `YYYY-MM-DD` when structurally present,
- `submitted_at` uses `YYYY-MM-DD` or is empty,
- actual evidence files are not part of the contract,
- all operational Submission rows are exported; Phase 7 does not pre-filter by compliance, timeliness, or DQ status.

Derived fields are excluded from the source contract:

```text
evidence_present
overdue_flag
submission_late
days_overdue
days_late
data_quality_status
as_of_date
```

`as_of_date` is execution/snapshot metadata rather than a row-level Submission source field.

## 6. Action Contract

Canonical file:

```text
data/raw/actions.csv
```

Phase 7 operational snapshot:

```text
security_action_snapshot_<snapshot_id>.csv
```

Exact column order:

```text
action_id
control_id
submission_id
owner_email
created_at
due_date
status
reminder_count
last_reminder_at
description
```

Exact header:

```csv
action_id,control_id,submission_id,owner_email,created_at,due_date,status,reminder_count,last_reminder_at,description
```

Physical rules:

- `created_at`: `YYYY-MM-DD`,
- `due_date`: `YYYY-MM-DD`,
- `last_reminder_at`: `YYYY-MM-DD` or empty,
- `reminder_count`: integer-compatible and non-negative under the logical model,
- missing values: empty CSV field.

The synthetic PoC Action due-date rule is:

```text
due_date = created_at + 7 calendar days
```

The operational Action snapshot preserves source facts such as:

```text
status
reminder_count
last_reminder_at
```

Phase 7 performs no Action aggregation during export.

## 7. Operational Excel Representation

The Microsoft 365 workbook uses:

```text
Cyber_Governance_Control_Register.xlsx
├── ControlCatalog
├── SubmissionRegister
└── ActionRegister
```

Excel Online / Power Automate may expose date values as ISO 8601 timestamps.

The Phase 7.2 reporting flow normalizes date representation to `YYYY-MM-DD` before serializing Submission and Action CSV snapshots.

This technical conversion does not change business meaning.

## 8. Phase 7 Snapshot Package Contract

Every successful snapshot package contains:

```text
security_control_snapshot_<snapshot_id>.json
security_submission_snapshot_<snapshot_id>.csv
security_action_snapshot_<snapshot_id>.csv
security_snapshot_manifest_<snapshot_id>.json
```

All artifacts share one `snapshot_id`.

The manifest contains exactly the agreed provenance/completion fields:

```text
snapshot_id
as_of_date
generated_at_local
control_file
submission_file
action_file
control_rows
submission_rows
action_rows
status
```

Successful status:

```text
complete
```

The manifest is created last. Source files without a corresponding `complete` manifest do not constitute a valid snapshot package.

The manifest is technical metadata, not a fifth business entity.

## 9. Snapshot Time Semantics

Phase 7 uses:

```text
W. Europe Standard Time
```

Target representations:

```text
snapshot_id = yyyyMMdd_HHmmss
as_of_date  = yyyy-MM-dd
```

Critical rule:

```text
Python as_of_date
=
matching manifest as_of_date
```

The Phase 7.3 CLI does not automatically parse the manifest. The caller supplies its date explicitly through `--as-of-date`.

## 10. Python Physical Input Boundary

Default mode:

```text
controls    = data/reference/control_catalog.json
submissions = data/raw/evidence_submissions.csv
actions     = data/raw/actions.csv
```

Explicit operational mode:

```text
--controls-path
--submissions-path
--actions-path
```

The three source overrides are **all-or-none**.

Valid:

```text
no source overrides
→ all canonical defaults
```

or:

```text
all three source overrides
→ one coherent explicit source set
```

Invalid partial combinations are rejected before processing. This prevents live operational state from being silently mixed with canonical synthetic state.

`--output-directory` is independent and controls where the existing three pipeline outputs are written.

## 11. Python Output Contract

The existing reporting outputs remain:

```text
curated_control_status.csv
data_quality_issues.csv
ai_review_queue.json
```

Phase 7 does not create an alternative set of transformation semantics for operational inputs.

Submission remains the curated grain.

The exact curated schema and AI queue contract are defined in [phase3_pipeline_contract.md](phase3_pipeline_contract.md).

## 12. Fatal Physical Failures vs. Data Quality

Fatal input-contract failures include unusable structures such as:

- missing required files,
- malformed JSON,
- malformed CSV,
- incorrect CSV header set/order,
- invalid Control Catalog top-level structure,
- missing required Control fields,
- duplicate `control_id` values in the Control Catalog.

These stop the pipeline.

Submission DQ findings remain business outputs and do **not** by themselves make the process fail.

```text
Physical input failure → non-zero execution
DQ finding             → successful run + DQ output
```

## 13. Empty Action Dataset

A valid Action source may contain only the exact header and zero data rows.

Phase 7.2 verified that Power Automate creates a header-only CSV for an empty `ActionRegister`, and Phase 7.3 verified that Python loads it successfully as:

```text
Actions loaded: 0
```

No special business rule or alternative schema is required.

## 14. Privacy Boundary

Operational snapshot artifacts remain private because they can contain:

```text
owner_email
submitted_by
comments
operational acceptance state
```

The following must not be committed:

- private operational snapshots,
- operational workbook copies,
- tenant/environment identifiers,
- OneDrive/workbook/table identifiers,
- connection credentials or tokens,
- private Power Platform deployment ZIPs.

Public repository evidence uses sanitized screenshots, sanitized workflow source, synthetic examples, and non-sensitive acceptance results.

## 15. Accepted Phase 7 Operational Contract

The final Phase 7 WP3 acceptance processed a private complete snapshot with manifest source counts:

```text
Controls:    5
Submissions: 17
Actions:     2
```

Python loaded exactly the same source counts and produced the existing contractual outputs without modifying canonical files.

Those operational counts are acceptance observations only. They do not replace the canonical `5 / 15 / 5` repository inventory.

See [phase7_end_to_end_acceptance.md](phase7_end_to_end_acceptance.md).

# Data Contract

## Document Role

**CURRENT-STATE FOUNDATION DOCUMENT — CURRENT THROUGH PHASE 10**

Documentation index: [README.md](README.md)

## Purpose

This document defines the physical data contracts used by the Cyber Governance Automation Lab, including the boundary between deterministic repository fixtures, private operational Phase 7 snapshots, generated outputs, and the Phase 10 external REST projection.

Logical entities and derived-state semantics are defined in [data_model.md](data_model.md). Data Quality rules are defined in [data_quality.md](data_quality.md).

## 1. Data-Plane Rule

The project maintains two distinct business-source data planes:

```text
Canonical repository fixtures
!=
Operational Microsoft 365 state
```

Canonical data exists for reproducible engineering acceptance. Operational data evolves through workflow execution.

Phase 7 connects operational source facts to Python through explicit private snapshots without overwriting canonical files.

Phase 10 does **not** add a third business-source data plane. It exposes a minimized read-only HTTP projection of the canonical Control Catalog only.

## 2. Canonical Repository Inputs

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

Canonical deterministic reference date:

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

Literal strings such as `NULL`, `null`, `None`, or `N/A` are not used to represent genuinely missing values.

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

Required Control fields:

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

The current canonical fixture contains exactly those eight properties per Control. The existing `src.extract.load_control_catalog()` loader enforces:

- top-level array,
- each entry is an object,
- all required fields are present,
- `control_id` is unique.

The loader does not currently implement a separate strict `additionalProperties = false` rule for internal Control JSON. Phase 10 therefore does not change the internal loader contract; instead its public response model explicitly projects only two approved fields.

Operational Control snapshots may contain reachable ownership information and therefore remain private.

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
- Phase 7 exports all operational rows without pre-filtering by compliance, timeliness, or DQ status.

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

Synthetic PoC Action due-date rule:

```text
due_date = created_at + 7 calendar days
```

Phase 7 preserves Action source facts and performs no Action aggregation during export.

## 7. Operational Excel Representation

Operational workbook:

```text
Cyber_Governance_Control_Register.xlsx
├── ControlCatalog
├── SubmissionRegister
└── ActionRegister
```

Excel Online / Power Automate can expose date values as ISO 8601 timestamps. Phase 7 normalizes snapshot date representation to `YYYY-MM-DD` before serializing Submission and Action CSV files. This is a technical representation conversion, not a business-state change.

## 8. Phase 7 Snapshot Package Contract

A successful snapshot package contains:

```text
security_control_snapshot_<snapshot_id>.json
security_submission_snapshot_<snapshot_id>.csv
security_action_snapshot_<snapshot_id>.csv
security_snapshot_manifest_<snapshot_id>.json
```

All artifacts share one `snapshot_id`.

The manifest contains:

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

The manifest is written last. Source files without a corresponding `complete` manifest do not constitute a valid completed snapshot package.

The manifest is technical metadata, not a fifth business entity.

## 9. Snapshot Time Semantics

Phase 7 uses:

```text
W. Europe Standard Time
```

Representations:

```text
snapshot_id = yyyyMMdd_HHmmss
as_of_date  = yyyy-MM-dd
```

Critical rule:

```text
Python as_of_date = matching manifest as_of_date
```

The Phase 7 Python CLI does not automatically parse the manifest; the caller supplies the date explicitly through `--as-of-date`.

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

The three source overrides are all-or-none.

```text
no overrides
→ coherent canonical source set

all three overrides
→ coherent explicit source set

partial overrides
→ rejected
```

`--output-directory` independently controls where generated pipeline outputs are written.

## 11. Python Output Contract

Generated outputs:

```text
curated_control_status.csv
data_quality_issues.csv
ai_review_queue.json
```

Submission remains the curated reporting grain. Phase 7 does not introduce alternative transformation semantics for operational inputs.

Detailed curated/AI queue schema is defined in [phase3_pipeline_contract.md](phase3_pipeline_contract.md).

## 12. Fatal Physical Failures vs. Data Quality

Fatal physical input failures include:

- missing required source file,
- malformed JSON,
- malformed CSV,
- incorrect CSV header set/order,
- invalid Control top-level structure,
- non-object Control entries,
- missing required Control fields,
- duplicate `control_id` values.

These stop processing.

Submission DQ findings are successful business outputs and do not by themselves make the pipeline execution fail.

```text
Physical input failure → non-zero execution
DQ finding             → successful run + DQ output
```

## 13. Empty Action Dataset

A valid Action source can contain only the exact header and zero rows.

Phase 7 verified both:

```text
Power Automate → header-only Action CSV
Python         → Actions loaded: 0
```

No alternate Action schema is required.

## 14. Phase 10 REST External Contract

Phase 10 reads only the canonical Control Catalog through:

```text
src.extract.load_control_catalog()
```

The external HTTP representation is deliberately smaller than the internal Control source:

```text
Internal Control source
├── control_id
├── control_name
├── control_statement
├── business_unit
├── owner_role
├── owner_email
├── frequency
└── risk_level

External ControlSummary
├── control_id
└── risk_level
```

Business endpoints:

```text
GET /api/v1/controls
GET /api/v1/controls/{control_id}
```

Successful response media type is JSON. The collection returns a top-level array in canonical source order; the detail endpoint returns one object.

Failure contracts:

```text
unknown Control → HTTP 404 / CONTROL_NOT_FOUND
source failure  → HTTP 500 / CONTROL_SOURCE_ERROR
```

The API does not silently fall back to operational snapshots or generated output when the canonical source is unavailable.

See [phase10_rest_api_contract.md](phase10_rest_api_contract.md) and [phase10_rest_api_acceptance.md](phase10_rest_api_acceptance.md).

## 15. Privacy Boundary

Operational artifacts remain private because they can contain:

```text
owner_email
submitted_by
comments
operational state
```

The following must not be committed:

- private operational snapshots,
- operational workbook copies,
- tenant/environment identifiers,
- OneDrive/workbook/table identifiers,
- connection credentials or tokens,
- private Power Platform deployment ZIPs.

Phase 10 does not process operational private data and intentionally excludes `owner_email` from its public Control response despite canonical e-mail values being synthetic.

## 16. Accepted Operational Observation vs. Canonical Baseline

The final Phase 7 private end-to-end acceptance observed:

```text
Controls:    5
Submissions: 17
Actions:     2
```

Those values are operational acceptance observations only. They do not replace the canonical repository baseline:

```text
Controls:    5
Submissions: 15
Actions:     5
```

Operational state and canonical deterministic fixtures remain separate by design.

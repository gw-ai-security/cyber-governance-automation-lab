# Phase 3 Python Pipeline Contract

## Purpose

Phase 3 converts the canonical Phase 0–2 specifications and synthetic datasets into executable Python logic. It implements the existing domain model; it does not redefine it.

Canonical upstream specifications:

- [business_process.md](business_process.md)
- [data_model.md](data_model.md)
- [data_contract.md](data_contract.md)
- [data_quality.md](data_quality.md)
- [phase2_dataset_coverage.md](phase2_dataset_coverage.md)

If implementation convenience conflicts with those documents, the implementation must change.

## Phase 3.0 Scope

Phase 3.0 fixes the implementation contract before code is written:

- pipeline stages,
- inputs and runtime parameters,
- module responsibilities,
- fatal-error boundaries,
- DQ issue emission semantics,
- curated output schema and grain,
- Action aggregation,
- AI queue policy,
- and deterministic acceptance results.

Executable ETL code begins in Phase 3.1.

## Pipeline

```text
EXTRACT
   ↓
NORMALIZE
   ↓
VALIDATE
   ↓
TRANSFORM / ENRICH
   ↓
DERIVE
   ↓
LOAD
```

Invalid Submission rows remain visible throughout the pipeline. They are flagged, not silently repaired, deleted, or deduplicated.

## Inputs

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

Roles:

- `control_catalog.json` — Control reference/master data.
- `evidence_submissions.csv` — primary Submission dataset validated by DQ-001 through DQ-010.
- `actions.csv` — follow-up workflow data used for reporting enrichment.

Action-specific DQ rule IDs are not introduced in Phase 3. The canonical Action dataset is treated as trusted synthetic workflow input after structural parsing.

## Runtime `as_of_date`

`as_of_date` is an execution parameter, not a raw Submission field.

Normal execution:

```bash
python src/main.py
```

uses the current processing date.

Deterministic execution:

```bash
python src/main.py --as-of-date 2026-08-15
```

uses the supplied `YYYY-MM-DD` value.

The canonical Phase 2 acceptance date is:

```text
2026-08-15
```

## Source Row Lineage

Every raw Submission data row receives:

```text
source_row_number
```

The numbering is 1-based and excludes the CSV header:

```text
1  = SUB-001
...
15 = SUB-015
```

This is the stable lineage key for DQ findings, including rows with missing or duplicated identifiers.

## Extract Contract

The Extract stage performs physical loading only.

CSV input must preserve raw string semantics. Pandas must not silently reinterpret prohibited literal null tokens such as `NULL`, `null`, `None`, or `N/A` as missing values merely because they are part of pandas' default NA vocabulary.

The implementation should therefore load CSV data as strings with default NA inference disabled and let normalization handle actual empty fields.

### Fatal structural failures

The pipeline stops with a non-zero exit code for unusable input structures, including:

- required file missing,
- malformed JSON,
- unreadable CSV,
- required CSV column missing,
- invalid Control Catalog top-level structure,
- required Control Catalog field missing,
- duplicate `control_id` values in the Control Catalog.

These are pipeline/input-contract failures, not Submission DQ issues.

## Normalize Contract

Normalization may change technical representation, not business meaning.

Allowed:

- trim surrounding whitespace,
- convert empty or whitespace-only CSV fields to missing values,
- prepare strict date parsing,
- convert Action `reminder_count` to integer for aggregation.

Not allowed:

- case-folding status values,
- mapping synonyms to allowed statuses,
- changing `Pending` to `In Review`,
- changing `compliant` to `Compliant`,
- fabricating evidence or submitters,
- replacing unknown Control IDs,
- deduplicating Submission rows,
- assigning a compliance result.

Thus:

```text
" Compliant " → "Compliant"
```

is technical normalization, while:

```text
"compliant" → "Compliant"
```

would be an impermissible semantic correction.

## Validate Contract

Phase 3 implements exactly the canonical ten Submission-level rules:

| Rule output value | Severity |
| --- | --- |
| `DQ-001 Missing Required Field` | High |
| `DQ-002 Unknown Control ID` | High |
| `DQ-003 Invalid Status` | High |
| `DQ-004 Missing Evidence` | High |
| `DQ-005 Duplicate Submission` | High |
| `DQ-006 Invalid Reporting Period` | Medium |
| `DQ-007 Invalid Due Date` | High |
| `DQ-008 Invalid Submission State` | High |
| `DQ-009 Invalid Evidence State` | Medium |
| `DQ-010 Invalid Submitter Email` | Medium |

The `rule` column in `data_quality_issues.csv` stores the full canonical label shown above.

No DQ-011 or additional rule is introduced without an explicit specification change.

### Issue emission

For one source row, one canonical DQ rule produces at most one issue record. A row may still produce multiple different DQ rules when independently evaluable.

If one rule concerns multiple fields, the `field` value lists them in deterministic comma-separated form.

| Rule | `field` |
| --- | --- |
| DQ-001 | missing required field name(s) |
| DQ-002 | `control_id` |
| DQ-003 | `status` |
| DQ-004 | `evidence_reference` |
| DQ-005 | `submission_id`, `control_id,reporting_period`, or combined relevant set |
| DQ-006 | `reporting_period` |
| DQ-007 | `due_date` |
| DQ-008 | `submitted_at`, `submitted_by`, or both |
| DQ-009 | `evidence_reference` |
| DQ-010 | `submitted_by` |

### Duplicate semantics

DQ-005 enforces both:

```text
submission_id
```

and:

```text
control_id + reporting_period
```

All rows participating in a duplicate invariant are flagged. They remain in curated output.

### Validation dependencies

Dependent rules execute only when prerequisites are available.

Example:

```text
control_id = CTRL-999
```

produces DQ-002. DQ-006 and DQ-007 are not evaluated because Control frequency cannot be resolved.

`Not evaluated` does not produce an issue record.

The same principle applies to missing prerequisite fields: DQ-001 captures the missing required value and dependent checks do not emit misleading secondary failures merely because their prerequisite is absent.

## Data Quality Issue Output

File:

```text
data/curated/data_quality_issues.csv
```

Exact column order:

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

Grain:

```text
one row per triggered DQ rule per raw Submission source row
```

Ordering:

1. `source_row_number` ascending,
2. DQ rule number ascending.

After sorting, deterministic IDs are assigned:

```text
DQI-0001
DQI-0002
...
```

Missing `submission_id` or `control_id` is serialized as an empty CSV field.

## Transform / Enrich Contract

Submission is the primary dataset.

Control enrichment uses:

```text
Submission LEFT JOIN Control
ON control_id
```

An inner join is forbidden because it would remove unresolved references such as `SUB-015 / CTRL-999` and hide DQ-002 failures.

The transformation preserves one row for every raw Submission source row, including duplicate business keys.

Resolved Control attributes added to curated data:

```text
control_name
business_unit
owner_role
owner_email
frequency
risk_level
```

If a Control does not resolve, these attributes remain empty while the Submission row remains present.

## Action Aggregation

Raw Action rows must not multiply Submission rows.

### Active Action

An active Action has status:

```text
Open
or
In Progress
```

The canonical model permits at most one non-completed Action per Submission.

Curated fields:

```text
active_action_id
active_action_status
active_action_due_date
```

If no active Action exists, these are empty.

### Reminder aggregation

For each Submission:

```text
reminder_count = SUM(Action.reminder_count)
```

across all related Actions. If there is no Action, the value is `0`.

```text
last_reminder_at = MAX(non-null Action.last_reminder_at)
```

across all related Actions. If no reminder exists, the field is empty.

This retains reminder history without changing Submission grain.

## Derived Metrics

Canonical derived values:

```text
evidence_present
overdue_flag
submission_late
days_overdue
days_late
data_quality_status
```

Their business formulas remain those defined in `data_model.md` and `business_process.md`.

DQ association uses `source_row_number`:

```text
0 DQ issues  → Valid
1+ DQ issues → Invalid
```

The implementation must preserve:

```text
Compliance != Timeliness != Data Quality
```

No derived process or DQ result may overwrite Submission status.

### Non-evaluable timing metrics

A malformed or missing prerequisite must not be represented as a known negative result.

If a timing metric cannot be calculated because a required date value is structurally unavailable or unparsable, the dependent derived timing fields are left empty/null rather than being forced to `False` or `0`.

Examples:

- missing/unparsable `due_date` → `overdue_flag`, `submission_late`, `days_overdue`, and `days_late` are not reliably evaluable;
- valid `due_date` with `submitted_at` legitimately empty → overdue logic remains evaluable using `as_of_date`;
- valid `submitted_at` and `due_date` → lateness logic is evaluable normally.

For the canonical Phase 2 dataset, all date values needed for the documented acceptance scenarios are parseable, so the expected derived results remain fully deterministic.

## Curated Control Status Output

File:

```text
data/curated/curated_control_status.csv
```

Grain:

```text
one row per raw Submission source row
```

Exact column order:

```text
source_row_number
submission_id
control_id
control_name
business_unit
owner_role
owner_email
frequency
risk_level
reporting_period
due_date
submission_status
evidence_present
submitted_at
comment
overdue_flag
submission_late
days_overdue
days_late
data_quality_status
active_action_id
active_action_status
active_action_due_date
reminder_count
last_reminder_at
```

`submission_status` is the curated name for raw Submission `status`, avoiding ambiguity with Action status.

`evidence_reference` and `submitted_by` are intentionally omitted from the reporting-oriented curated output. They remain in raw data and are still used by validation/derivation logic.

Serialization:

- UTF-8,
- comma delimiter,
- header required,
- dates as `YYYY-MM-DD`,
- missing values as empty CSV fields,
- evaluable booleans as `True` / `False`,
- evaluable day counts and `reminder_count` as non-negative integers,
- raw Submission source order preserved.

## AI Review Queue Policy

The AI queue prepares selected governance exceptions; it is not a Data Quality repair mechanism and it never assigns compliance.

Eligibility:

```text
data_quality_status = Valid
AND
(
    submission_status = Non-Compliant
    OR
    overdue_flag = True
)
```

Rationale:

- DQ-invalid rows go to deterministic DQ/human correction rather than AI reasoning over untrusted input.
- `Non-Compliant` is a reviewed security/control exception.
- `Overdue` is a process exception requiring follow-up.
- lateness alone does not qualify once evidence has arrived.
- ordinary `Compliant` and `In Review` rows do not qualify.

For `as_of_date = 2026-08-15`, the canonical queue contains exactly:

```text
SUB-005
SUB-014
```

DQ-invalid `SUB-002`, `SUB-006`, `SUB-008`, `SUB-009`, and `SUB-015` are excluded. Late-only `SUB-004` is also excluded.

## AI Review Queue Output

File:

```text
data/curated/ai_review_queue.json
```

Top-level structure:

```json
{
  "as_of_date": "2026-08-15",
  "items": []
}
```

Each item contains exactly:

```text
submission_id
control_id
control_name
business_unit
risk_level
reporting_period
submission_status
due_date
evidence_present
days_overdue
comment
review_reasons
```

`review_reasons` contains one or more of:

```text
Non-Compliant
Overdue
```

The payload deliberately excludes:

```text
owner_email
submitted_by
evidence_reference
Action description
```

This enforces input minimization. Queue items preserve curated source-row order.

## Module Responsibilities

```text
src/
├── main.py
├── extract.py
├── transform.py
├── validate.py
└── load.py
```

No class hierarchy, ORM, workflow engine, dependency-injection framework, or other unnecessary abstraction is required.

### `extract.py`

Physical input only:

- read Control Catalog JSON,
- read Submission CSV,
- read Action CSV,
- enforce required physical structure,
- return raw tabular data.

No DQ business rules or derived governance metrics.

### `transform.py`

Normalization and deterministic transformation:

- normalize source values without semantic correction,
- add source-row lineage,
- parse dates for downstream use,
- left-join Control data,
- aggregate Actions without changing Submission grain,
- compute derived metrics,
- build AI queue payload from validated/curated rows.

### `validate.py`

Submission DQ only:

```text
validate_submissions(...)
→ Data Quality Issue records
```

Implements DQ-001 through DQ-010 and dependency behavior. It does not mutate Submission status or silently repair invalid values.

### `load.py`

Serialization only:

- write `curated_control_status.csv`,
- write `data_quality_issues.csv`,
- write `ai_review_queue.json`,
- create `data/curated/` if required.

No business-rule calculations.

### `main.py`

Orchestration only:

```text
parse as_of_date
→ extract
→ normalize
→ validate
→ transform/enrich
→ derive
→ build AI queue
→ load
→ print run summary
```

`main.py` must not become the implementation container for all rules.

## Exit Semantics

A successful pipeline run returns exit code `0` even when DQ issues exist. DQ findings are expected business outputs, not pipeline crashes.

Non-zero exit codes are reserved for fatal execution/input-contract failures such as missing files, malformed required structures, invalid CLI date format, or unrecoverable serialization errors.

## Canonical Run Summary

For the Phase 2 dataset and `--as-of-date 2026-08-15`, expected counts are:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

Exact console wording is not contractual; the counts are.

## Phase 3 Acceptance Results

Command:

```bash
python src/main.py --as-of-date 2026-08-15
```

Expected DQ findings:

```text
SUB-002 → DQ-004 Missing Evidence
SUB-006 → DQ-003 Invalid Status
SUB-008 → DQ-005 Duplicate Submission
SUB-009 → DQ-005 Duplicate Submission
SUB-015 → DQ-002 Unknown Control ID
```

Expected total DQ issue rows:

```text
5
```

Expected valid business/process exceptions:

```text
SUB-004
→ data_quality_status = Valid
→ submission_late = True
→ days_late = 2

SUB-005
→ data_quality_status = Valid
→ submission_status = Non-Compliant
→ overdue_flag = False

SUB-014
→ data_quality_status = Valid
→ overdue_flag = True
→ days_overdue = 5
```

Row preservation:

```text
raw Submission rows = 15
curated rows = 15
```

`SUB-015` remains after the Control left join. `SUB-008` and `SUB-009` both remain after duplicate detection.

Expected AI queue:

```text
2 items: SUB-005, SUB-014
```

## Phase 3.0 Definition of Done

Phase 3.0 is complete when:

- pipeline stages and runtime semantics are fixed,
- source-row lineage is fixed,
- fatal-vs-DQ failure boundaries are fixed,
- DQ issue schema, values, ordering, and IDs are fixed,
- curated grain and exact columns are fixed,
- Action aggregation is fixed,
- non-evaluable derived-value behavior is fixed,
- AI queue eligibility and payload are fixed,
- module responsibilities are fixed,
- deterministic Phase 2 acceptance outcomes are documented,
- and no executable ETL logic has yet been introduced.

Next step:

```text
Phase 3.1 – Extract
```

## Known Scope Limitations

Phase 3 does not add new DQ rule IDs for Action-specific semantic validation or additional source-contract cases not covered by DQ-001 through DQ-010.

The canonical Phase 2 dataset conforms to those surrounding contracts. Expanding validation coverage later requires an explicit specification change rather than silently adding new semantics during implementation.

# Phase 3 Python Pipeline Contract

## Purpose

This document defines the implementation contract for Phase 3 of the Cyber Governance Automation Lab.

Phase 3 translates the business semantics, raw-data contracts, Data Quality rules, and deterministic Phase 2 scenarios into executable Python code. It does not redefine the domain model.

The canonical upstream specifications remain:

- [business_process.md](business_process.md)
- [data_model.md](data_model.md)
- [data_contract.md](data_contract.md)
- [data_quality.md](data_quality.md)
- [phase2_dataset_coverage.md](phase2_dataset_coverage.md)

If implementation convenience conflicts with those documents, the implementation must change rather than silently changing the business meaning.

## Phase 3.0 Scope

Phase 3.0 defines:

- exact pipeline stages,
- input files,
- runtime parameter semantics,
- module responsibilities,
- fatal-error boundaries,
- Data Quality issue emission behavior,
- curated output grain and schema,
- Action aggregation semantics,
- AI review queue selection policy and schema,
- deterministic ordering,
- and Phase 3 acceptance criteria.

Phase 3.0 does **not** implement Python ETL code. Executable code begins in Phase 3.1.

## Pipeline Model

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

The stages are deliberately explicit. Data Quality findings are preserved; the pipeline must not silently repair, delete, or deduplicate invalid Submission rows.

## Inputs

Phase 3 uses exactly these canonical inputs:

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

### Input roles

`control_catalog.json`
→ trusted reference/master data for Control attributes and frequency-dependent rules.

`evidence_submissions.csv`
→ raw period-specific Submission facts and the primary dataset validated by DQ-001 through DQ-010.

`actions.csv`
→ synthetic follow-up workflow data used to enrich the curated reporting output with deterministic Action/reminder information.

Action-specific Data Quality rule IDs are not introduced in Phase 3. The current canonical Action dataset is treated as trusted synthetic workflow input after structural parsing.

## Runtime Parameter: `as_of_date`

`as_of_date` remains an execution parameter, not a raw Submission attribute.

Normal execution:

```bash
python src/main.py
```

uses the current processing date.

Deterministic execution:

```bash
python src/main.py --as-of-date 2026-08-15
```

uses the explicitly supplied date.

The optional CLI parameter must use format:

```text
YYYY-MM-DD
```

The fixed Phase 2 acceptance date is:

```text
2026-08-15
```

No third-party CLI library is required; the Python standard library is sufficient.

## Source Row Traceability

Each raw Submission data row receives an internal and curated:

```text
source_row_number
```

The numbering is 1-based over data rows and excludes the CSV header:

```text
1 = SUB-001 row
2 = SUB-002 row
...
15 = SUB-015 row
```

`source_row_number` is the stable lineage key used to associate Data Quality Issues with the exact raw row, including cases where `submission_id` is missing or duplicated.

## Extract Contract

The Extract stage reads source files without applying business corrections.

### CSV loading

Submission and Action CSVs must be loaded in a way that preserves raw string semantics.

In particular, Python must not let pandas silently reinterpret prohibited literal null tokens such as:

```text
NULL
null
None
N/A
```

as missing values merely because they appear in pandas' default NA vocabulary.

The implementation should therefore preserve raw text on load, for example by using string-oriented loading with default NA inference disabled, and let the Normalize stage handle actual empty fields explicitly.

### Structural preconditions

The pipeline stops with a non-zero exit code when a required input cannot be processed structurally, including:

- required input file missing,
- malformed JSON,
- unreadable CSV,
- required dataset column missing,
- Control Catalog not represented as the expected JSON array/object structure,
- duplicate `control_id` values in the Control Catalog.

These are pipeline/input-contract failures, not Submission Data Quality Issues.

The Submission DQ engine is intended to evaluate row-level data problems, not compensate for an unusable reference dataset or missing physical schema.

## Normalize Contract

Normalization may change technical representation but must not change business meaning.

Allowed normalization includes:

- trim leading/trailing whitespace from strings,
- convert empty or whitespace-only CSV fields to a missing value representation,
- standardize internal date representations after validation/parsing,
- convert `reminder_count` to an integer for Action aggregation.

Normalization must **not**:

- case-fold status values,
- map synonyms to valid statuses,
- change `Pending` to `In Review`,
- change `compliant` to `Compliant`,
- fabricate missing evidence,
- fabricate a missing submitter,
- replace an unknown Control ID,
- deduplicate Submission rows,
- or assign a compliance outcome.

Example:

```text
" Compliant "
→ "Compliant"
```

is technical whitespace normalization.

But:

```text
"compliant"
→ "Compliant"
```

would be a semantic correction and is not allowed. The lowercase value remains invalid under DQ-003.

## Validate Contract

Phase 3 implements exactly the ten canonical Submission-level Data Quality rules:

```text
DQ-001 Missing Required Field
DQ-002 Unknown Control ID
DQ-003 Invalid Status
DQ-004 Missing Evidence
DQ-005 Duplicate Submission
DQ-006 Invalid Reporting Period
DQ-007 Invalid Due Date
DQ-008 Invalid Submission State
DQ-009 Invalid Evidence State
DQ-010 Invalid Submitter Email
```

No DQ-011 or additional rule is introduced in Phase 3 without an explicit specification change.

### Issue emission policy

For a given source row, a single canonical DQ rule produces at most one issue record.

If one rule concerns multiple fields, the `field` value lists the relevant fields in a deterministic comma-separated form and the message explains the combined violation.

Examples:

```text
DQ-001
field = submission_id,status
```

when both fields are missing on the same row.

```text
DQ-008
field = submitted_at,submitted_by
```

when the row violates multiple state-consistency conditions under that same rule.

A row may still produce multiple **different** DQ rules when those rules are independently evaluable.

### Field mapping

| Rule | `field` value |
| --- | --- |
| DQ-001 | missing required field name(s), comma-separated |
| DQ-002 | `control_id` |
| DQ-003 | `status` |
| DQ-004 | `evidence_reference` |
| DQ-005 | `submission_id`, `control_id,reporting_period`, or the combined relevant set |
| DQ-006 | `reporting_period` |
| DQ-007 | `due_date` |
| DQ-008 | `submitted_at`, `submitted_by`, or `submitted_at,submitted_by` |
| DQ-009 | `evidence_reference` |
| DQ-010 | `submitted_by` |

### DQ-005 duplicate semantics

Both duplicate invariants remain active:

```text
submission_id
```

and:

```text
control_id + reporting_period
```

All source rows participating in a duplicate invariant are flagged. Duplicate rows are preserved in downstream data and are not automatically removed.

### Validation dependencies

Dependent rules are evaluated only when their prerequisites are available.

For example:

```text
control_id = CTRL-999
```

produces:

```text
DQ-002 = fail
```

while DQ-006 and DQ-007 are not evaluated because the Control frequency cannot be resolved.

`Not evaluated` does not create an issue record.

Missing prerequisite source values follow the same principle. A missing required value is primarily captured by DQ-001; dependent rules do not need to emit misleading secondary failures when the required input for their evaluation is absent.

## Data Quality Issue Output Contract

File:

```text
data/curated/data_quality_issues.csv
```

Columns, in exact order:

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

The grain is:

```text
one row per triggered DQ rule per raw Submission source row
```

### Deterministic issue IDs

Issues are ordered by:

1. `source_row_number` ascending,
2. DQ rule number ascending.

After ordering, issue IDs are assigned sequentially:

```text
DQI-0001
DQI-0002
DQI-0003
...
```

The same input and rules therefore produce the same issue IDs.

Missing `submission_id` or `control_id` is serialized as an empty CSV field.

## Transform / Enrich Contract

The Submission dataset is the primary side of the enrichment.

Control reference data is joined using:

```text
Submission LEFT JOIN Control
ON control_id
```

An inner join is forbidden because it would remove unresolved references such as `SUB-015 / CTRL-999` and hide DQ-002 failures.

The transformation must preserve one curated row for every raw Submission source row, including duplicate business keys.

### Control enrichment

When the Control reference resolves, the following attributes are added:

```text
control_name
business_unit
owner_role
owner_email
frequency
risk_level
```

When the Control reference does not resolve, those fields remain empty/null in the curated row. The Submission itself remains present.

## Action Aggregation Contract

The curated output remains at Submission-row grain; raw Action rows must therefore not be joined in a way that multiplies Submission rows.

For each Submission:

### Active Action

The active Action is the related Action whose status is:

```text
Open
or
In Progress
```

The Phase 1 model permits at most one non-completed Action per Submission.

The curated fields are:

```text
active_action_id
active_action_status
active_action_due_date
```

If no non-completed Action exists, these fields are empty.

### Reminder aggregation

`reminder_count` in the curated dataset is:

```text
SUM(Action.reminder_count)
for all Actions related to the Submission
```

If no related Action exists:

```text
reminder_count = 0
```

`last_reminder_at` is:

```text
MAX(non-null Action.last_reminder_at)
for all Actions related to the Submission
```

If no reminder exists, it is empty.

This preserves one-row-per-Submission reporting while retaining useful reminder history even when an older Action is already `Completed`.

## Derived Metrics Contract

The following canonical metrics are computed downstream from source facts:

```text
evidence_present
overdue_flag
submission_late
days_overdue
days_late
data_quality_status
```

The formulas remain exactly those defined in `data_model.md` and `business_process.md`.

### Data Quality status

DQ association uses `source_row_number`, not only `submission_id`, so malformed or duplicate technical IDs remain traceable.

```text
0 DQ Issues for source_row_number
→ Valid

1 or more DQ Issues for source_row_number
→ Invalid
```

### Independence rule

The implementation must preserve:

```text
Compliance
!=
Timeliness
!=
Data Quality
```

Therefore the pipeline must not change Submission status because a row is late, overdue, or Data Quality Invalid.

## Curated Control Status Output Contract

File:

```text
data/curated/curated_control_status.csv
```

### Grain

```text
one row per raw Submission source row
```

This is deliberately **not** one row per unique business key because duplicate source rows must remain visible for DQ-005 and traceability.

### Columns

Columns, in exact order:

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

`submission_status` is the curated/reporting name for the raw Submission field `status`. Renaming it in the curated output avoids ambiguity with Action status.

The raw `evidence_reference` and `submitted_by` fields are intentionally not copied into this reporting-oriented output because Power BI does not require them for the planned management/control-monitoring use case. They remain available in the raw Submission dataset and are still used by validation and derivation logic.

### Serialization

- UTF-8
- comma delimiter
- header required
- dates serialized as `YYYY-MM-DD`
- missing values serialized as empty CSV fields
- booleans serialized consistently as `True` / `False`
- `days_overdue`, `days_late`, and `reminder_count` serialized as non-negative integers

Rows preserve raw Submission source order.

## AI Review Queue Policy

The AI queue is a controlled exception-preparation output. It is not a second Data Quality engine and it does not make compliance decisions.

### Eligibility

A Submission enters the AI review queue only when:

```text
data_quality_status = Valid
AND
(
    submission_status = Non-Compliant
    OR
    overdue_flag = True
)
```

This Phase 3.0 rule is deliberate:

- Data Quality Invalid rows are routed to deterministic DQ/human correction rather than AI reasoning over untrusted or internally inconsistent input.
- `Non-Compliant` is a reviewed security/control exception suitable for summarization and follow-up support.
- `Overdue` is a process exception suitable for follow-up support.
- A late submission by itself does not enter the AI queue once evidence has arrived.
- `Compliant` and ordinary `In Review` rows do not enter the queue.

The AI queue policy prepares candidates only. It does not imply that an external AI call will necessarily be made.

### Expected Phase 2 queue

With:

```text
as_of_date = 2026-08-15
```

the expected queue contains exactly:

```text
SUB-005
→ valid Non-Compliant Submission

SUB-014
→ valid currently overdue Submission
```

The following intentional DQ failures are excluded from the AI queue:

```text
SUB-002
SUB-006
SUB-008
SUB-009
SUB-015
```

`SUB-004` is also excluded because lateness alone is not an AI-queue criterion.

## AI Review Queue Output Contract

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

`review_reasons` is an array containing one or more of:

```text
Non-Compliant
Overdue
```

The AI input deliberately excludes:

```text
owner_email
submitted_by
evidence_reference
Action description
```

This follows the project's input-minimization principle and keeps the AI payload focused on the information needed for controlled exception review.

Queue items preserve curated source-row order.

## Module Responsibility Contract

Phase 3 implementation uses the existing simple module structure:

```text
src/
├── main.py
├── extract.py
├── transform.py
├── validate.py
└── load.py
```

No framework, class hierarchy, ORM, workflow engine, or dependency-injection layer is required.

### `extract.py`

Responsibility:

```text
physical input only
```

Expected public responsibilities:

- read Control Catalog JSON,
- read Submission CSV,
- read Action CSV,
- check required physical columns/structure,
- return raw tabular data.

It must not implement DQ business rules or derived governance metrics.

### `transform.py`

Responsibility:

```text
normalization + enrichment + deterministic derived values
```

Expected public responsibilities:

- normalize source values without semantic correction,
- add source row lineage,
- parse dates for downstream use,
- left-join Control reference data,
- aggregate Action information without changing Submission grain,
- compute canonical derived metrics,
- build the deterministic AI queue payload from already validated/curated records.

### `validate.py`

Responsibility:

```text
Submission Data Quality rules only
```

Expected public responsibility:

```text
validate_submissions(...)
→ Data Quality Issue records
```

The module implements DQ-001 through DQ-010 and their dependency behavior. It must not change raw Submission status or silently correct invalid values.

### `load.py`

Responsibility:

```text
output serialization only
```

Expected public responsibilities:

- write `curated_control_status.csv`,
- write `data_quality_issues.csv`,
- write `ai_review_queue.json`,
- create the curated output directory when needed,
- preserve the serialization rules in this contract.

It must not contain business-rule calculations.

### `main.py`

Responsibility:

```text
orchestration only
```

Expected flow:

```text
parse as_of_date
    ↓
extract inputs
    ↓
normalize
    ↓
validate Submissions
    ↓
transform / enrich
    ↓
derive metrics
    ↓
build AI queue
    ↓
load outputs
    ↓
print concise run summary
```

`main.py` must not become a container for the implementation details of all DQ rules.

## Process Exit Semantics

A successful run returns exit code `0` even when Data Quality Issues are found.

Data Quality Issues are expected business outputs of this project, not pipeline crashes.

A non-zero exit code is reserved for fatal execution/input-contract failures such as missing files, malformed required structures, invalid CLI date format, or unrecoverable serialization errors.

## Console Run Summary

A successful run should print a concise summary such as:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
Outputs written to: data/curated/
```

Exact wording is not a business contract, but the counts must be deterministic for the canonical Phase 2 dataset when run with `--as-of-date 2026-08-15`.

## Canonical Phase 2 Acceptance Results

For:

```bash
python src/main.py --as-of-date 2026-08-15
```

Phase 3 must reproduce the following outcomes.

### Expected DQ failures

```text
SUB-002 → DQ-004
SUB-006 → DQ-003
SUB-008 → DQ-005
SUB-009 → DQ-005
SUB-015 → DQ-002
```

Expected total DQ issue records:

```text
5
```

### Expected valid business/process exceptions

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

### Expected row preservation

```text
raw Submission rows = 15
curated Submission rows = 15
```

`SUB-015` must remain present after Control enrichment.

`SUB-008` and `SUB-009` must both remain present after duplicate detection.

### Expected AI queue

```text
item_count = 2
items = SUB-005, SUB-014
```

## Phase 3.0 Definition of Done

Phase 3.0 is complete when:

- pipeline stages are fixed,
- runtime `as_of_date` semantics are fixed,
- source-row lineage semantics are fixed,
- fatal-vs-DQ error boundaries are fixed,
- DQ issue emission and ordering are fixed,
- curated output grain and exact columns are fixed,
- Action aggregation semantics are fixed,
- AI queue eligibility and exact payload fields are fixed,
- module responsibilities are fixed,
- deterministic Phase 2 acceptance outcomes are documented,
- and no executable Phase 3 ETL logic has yet been introduced.

The next step is **Phase 3.1 – Extract**, implementing only the input-reading and physical-structure responsibilities defined here.

## Known Scope Limitations

Phase 3 does not add new Data Quality rule IDs for:

- Action-specific semantic validation,
- malformed Control reference values beyond the structural/reference preconditions required to run the pipeline,
- or additional date-format rules not already represented by DQ-001 through DQ-010.

The canonical Phase 2 dataset conforms to those surrounding source contracts. Expanding validation coverage later requires an explicit specification change rather than silently adding new validation semantics during implementation.

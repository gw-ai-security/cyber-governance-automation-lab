# Raw Data Contract

## Purpose

This document defines the physical serialization and representation rules for the canonical raw flat-file datasets used by the deterministic repository pipeline established in Phases 2–3. It is a physical data contract, not a business-model definition; logical entities and relationships remain defined in [data_model.md](data_model.md).

The materialized canonical datasets are:

```text
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

This document defines their contract. It does not generate or mutate those datasets.

## Common CSV Rules

| Property | Contract |
| --- | --- |
| Encoding | UTF-8 |
| Delimiter | comma |
| Header | required |
| Dates | `YYYY-MM-DD` |
| Missing / null values | empty CSV field |
| Strings | plain UTF-8 text |

An empty CSV field is interpreted downstream as missing. The literal strings `NULL`, `null`, `None`, and `N/A` must not be used to represent missing values.

Fields containing commas, double quotes, or line breaks must use standard CSV double-quote escaping. Within a quoted field, each literal double quote is escaped as two double quotes.

All identities, e-mail addresses, and references stored in canonical repository data are synthetic. No real company information, internal system names, credentials, secrets, or personal operational data may be stored.

## Raw Submission Dataset

File:

```text
data/raw/evidence_submissions.csv
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

- `due_date`: required date formatted as `YYYY-MM-DD` when structurally present,
- `submitted_at`: date formatted as `YYYY-MM-DD`, or empty,
- timestamps and timezone information are not used in the canonical repository CSV,
- only `evidence_reference` is stored; actual evidence files are not stored in repository data.

Example expected record with no submitted evidence:

```csv
SUB-001,CTRL-001,2026-Q1,2026-04-10,Not Submitted,,,,
```

The following derived fields and runtime parameters are excluded from raw Submission data:

```text
evidence_present
overdue_flag
submission_late
days_overdue
days_late
data_quality_status
as_of_date
```

Derived metrics are computed downstream. `as_of_date` is an execution parameter, not a Submission source field.

## Raw Action Dataset

File:

```text
data/raw/actions.csv
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

- `created_at`: required date formatted as `YYYY-MM-DD`,
- `due_date`: required date formatted as `YYYY-MM-DD`,
- `last_reminder_at`: date formatted as `YYYY-MM-DD`, or empty,
- `reminder_count`: non-negative integer,
- `owner_email`: required synthetic e-mail address containing `@`,
- missing values: empty CSV field.

The canonical synthetic Action due-date rule is:

```text
due_date = created_at + 7 calendar days
```

Example with a comma in `description` and a contract-consistent Action due date:

```csv
ACT-001,CTRL-001,SUB-001,owner@example.com,2026-04-11,2026-04-18,Open,0,,"Evidence reviewed, remediation required."
```

The logical Action constraints, status values, Action-to-Submission consistency rule, reminder invariants, and active-Action cardinality rule are defined in [data_model.md](data_model.md#action-data-constraints).

## Operational Microsoft 365 Boundary

The Phase 5–6 operational workbook can serialize date values differently through Excel Online / Power Automate, for example as ISO 8601 timestamps. That operational representation does not change this canonical repository CSV contract.

The operational workbook is intentionally separate from `data/raw/*` until Phase 7 implements the planned reporting snapshot/export boundary.

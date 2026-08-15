# Raw Data Contract

## Purpose

This document defines the serialization and representation rules for raw flat-file data used by the proof-of-concept implementation in later Phase 2 and Phase 3 work. It is a physical data contract, not a new business entity. The logical entities and relationships remain defined in [data_model.md](data_model.md).

No raw CSV files are created as part of this specification.

## Common CSV Rules

| Property | Contract |
| --- | --- |
| Encoding | UTF-8 |
| Delimiter | comma |
| Header | required |
| Dates | `YYYY-MM-DD` |
| Missing / null values | empty CSV field |
| Strings | plain UTF-8 text |

An empty CSV field is interpreted by Python as null / `None`. The literal strings `NULL`, `null`, `None`, and `N/A` must not be used to represent missing values.

All identities, email addresses, and references must be synthetic. No real company information, internal system names, credentials, secrets, or personal data may be stored.

## Raw Submission Dataset

The raw Submission CSV columns, in order, are exactly:

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

The header row is therefore:

```csv
submission_id,control_id,reporting_period,due_date,status,evidence_reference,submitted_at,submitted_by,comment
```

`due_date` is a date formatted as `YYYY-MM-DD`. `submitted_at` is also date only, formatted as `YYYY-MM-DD`, or empty. Timestamps and timezone information are not used for this proof of concept.

Example row with missing evidence and submission details:

```csv
SUB-001,CTRL-001,2026-Q1,2026-04-10,Not Submitted,,,,
```

Only `evidence_reference` is stored. No actual evidence file is stored in repository data.

The following derived fields and execution parameters are specifically excluded from raw Submission data:

```text
evidence_present
overdue_flag
submission_late
days_overdue
days_late
data_quality_status
as_of_date
```

Derived booleans and metrics are computed downstream and are not stored in raw input. `as_of_date` is an execution parameter, not a raw Submission column.

## Raw Action Dataset

The expected raw Action CSV contract for later Phase 2.4 work uses these existing Action fields, in order:

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

The header row is therefore:

```csv
action_id,control_id,submission_id,owner_email,created_at,due_date,status,reminder_count,last_reminder_at,description
```

Physical field rules:

* `created_at`: required date formatted as `YYYY-MM-DD`.
* `due_date`: required date formatted as `YYYY-MM-DD`.
* `last_reminder_at`: date formatted as `YYYY-MM-DD`, or an empty field.
* `reminder_count`: non-negative integer.
* Missing values: empty CSV field.

The logical Action constraints, including status values and reminder tracking invariants, are defined in [data_model.md](data_model.md#action-data-constraints).

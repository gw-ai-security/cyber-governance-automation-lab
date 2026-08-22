# Phase 7 Reporting Export Contract

## Status

**PHASE 7.0 CONTRACT DEFINED — IMPLEMENTATION PLANNED**

Phase 7.0 defines the reporting-snapshot boundary between the operational Microsoft 365 data plane established in Phases 5–6 and the deterministic Python/reporting pipeline established in Phases 2–4.

No Power Automate export flow, operational snapshot files, Python input-path extension, or Power BI report is implemented by Phase 7.0 itself.

## 1. Purpose

Phase 7 must create a controlled, reproducible export of the current operational governance state without overwriting the canonical repository acceptance fixtures.

The target flow is:

```text
Operational Microsoft 365 workbook
        ↓
Power Automate reporting snapshot
        ↓
Versioned private snapshot package
        ↓
Python Data Quality / transformation pipeline
        ↓
Curated reporting outputs
        ↓
Phase 8 Power BI
```

Core design rule:

```text
Power Automate exports source facts.
Python owns Data Quality, enrichment, Action aggregation, and derived metrics.
```

Phase 7 therefore does not duplicate the Phase 3 business logic inside Power Automate.

## 2. Scope

Phase 7 is responsible for:

- scheduled export of the operational `ControlCatalog`, `SubmissionRegister`, and `ActionRegister`,
- one shared snapshot identity across all exported artifacts,
- deterministic field selection and field order,
- normalization of operational date representations to the existing repository-compatible date contract where applicable,
- preservation of missing values without semantic substitution,
- private OneDrive storage of operational snapshot artifacts,
- explicit snapshot metadata and completion state,
- a controlled Python input boundary for processing an explicit operational snapshot,
- end-to-end acceptance proving that the exported snapshot can be processed without altering canonical repository fixtures.

Phase 7 does **not** implement:

- Power BI dashboards or DAX measures,
- AI model invocation,
- REST APIs,
- compliance decisions,
- automatic remediation or source-data repair,
- new Submission Data Quality rule IDs,
- evidence-file storage,
- production data warehousing,
- transactional snapshot guarantees across Excel tables,
- automatic publication of operational data to GitHub.

## 3. Data-Plane Boundary

The project continues to maintain two distinct data planes.

### Canonical repository plane

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

These files are deterministic synthetic acceptance fixtures. They remain unchanged by Phase 7 operational runs.

### Operational Microsoft 365 plane

```text
Cyber_Governance_Control_Register.xlsx
├── ControlCatalog
├── SubmissionRegister
└── ActionRegister
```

These tables contain the current operational proof-of-concept state produced or consumed by the Phase 5 evidence-intake and Phase 6 reminder workflows.

Phase 7 creates an explicit reporting snapshot from this operational state. It does not redefine the canonical fixtures as live data.

## 4. Why All Three Operational Tables Are Exported

Phase 5 operationalizes Submission state. Phase 6 operationalizes Action and reminder state. `ControlCatalog` remains the operational reference source used to resolve Control metadata and accountable owners.

A coherent operational reporting snapshot therefore requires:

```text
Control state
+
Submission state
+
Action/reminder state
```

Using live Submissions and Actions while enriching them against only the synthetic repository Control Catalog would mix operational and canonical reference state in one reporting run. Phase 7 avoids that mixed-state boundary by snapshotting all three operational tables.

This does not add a new business entity. The logical model remains exactly:

```text
Control
Submission
Action
Data Quality Issue
```

## 5. Snapshot Package

Every successful Phase 7 run produces one logical snapshot package identified by one shared `snapshot_id`.

Canonical Phase 7 file naming:

```text
security_control_snapshot_<snapshot_id>.json
security_submission_snapshot_<snapshot_id>.csv
security_action_snapshot_<snapshot_id>.csv
security_snapshot_manifest_<snapshot_id>.json
```

Example:

```text
security_control_snapshot_20260824_090000.json
security_submission_snapshot_20260824_090000.csv
security_action_snapshot_20260824_090000.csv
security_snapshot_manifest_20260824_090000.json
```

The timestamp portion is generated once per flow run and reused for every artifact.

`snapshot_id` is technical lineage metadata. It is not a fifth core business entity and is not added to the Control, Submission, or Action source schema.

## 6. Snapshot Time Semantics

The flow resolves two related values once at the beginning of the run:

```text
snapshot_id
as_of_date
```

Target representations:

```text
snapshot_id = yyyyMMdd_HHmmss
as_of_date  = yyyy-MM-dd
```

Both values use:

```text
W. Europe Standard Time
```

so the operational snapshot follows the same Central European local-date basis used by the Phase 5/6 workflows.

Critical rule:

```text
Python as_of_date
=
manifest as_of_date
```

The processing date must represent the snapshot evaluation date, not an unrelated later date on which somebody happens to run Python.

`as_of_date` remains runtime/snapshot metadata. It is **not** added as a source field to every Submission row.

## 7. Control Snapshot Contract

Source:

```text
ControlCatalog
```

Output:

```text
security_control_snapshot_<snapshot_id>.json
```

Physical representation:

```text
UTF-8 JSON array
```

Each Control object contains exactly the existing Control source fields:

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

The Control snapshot must preserve source values without semantic correction.

No derived reporting fields are added.

The operational `owner_email` may contain a reachable organizational address. Therefore the Control snapshot is private operational data and must not be committed to the public repository.

## 8. Submission Snapshot Contract

Source:

```text
SubmissionRegister
```

Output:

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

Grain:

```text
one row per operational SubmissionRegister row
```

The export includes all operational Submission rows. It must not filter the dataset to only Compliant, Non-Compliant, overdue, valid, or otherwise selected states.

The snapshot intentionally excludes derived fields such as:

```text
evidence_present
overdue_flag
submission_late
days_overdue
days_late
data_quality_status
```

Those remain Python responsibilities.

## 9. Action Snapshot Contract

Source:

```text
ActionRegister
```

Output:

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

Grain:

```text
one row per operational ActionRegister row
```

Phase 7 performs no Action aggregation in Power Automate.

In particular, the following Phase 6 operational fields must be preserved:

```text
status
reminder_count
last_reminder_at
```

Action aggregation remains a Python transformation responsibility so Submission grain cannot be multiplied accidentally by multiple Action rows.

## 10. Serialization Rules

### CSV

Submission and Action snapshots use:

| Property | Contract |
| --- | --- |
| Encoding | UTF-8 |
| Delimiter | comma |
| Header | required |
| Dates | `YYYY-MM-DD` |
| Missing values | empty CSV field |
| Quoting | standard CSV double-quote escaping |

Operational Excel/connector values may be represented as ISO 8601 timestamps. Phase 7 must normalize exported date fields to `YYYY-MM-DD` before creating the CSV artifact.

The export must not use literal missing-value tokens such as:

```text
NULL
null
None
N/A
```

when the underlying value is actually missing.

### Control JSON

The Control snapshot uses strict UTF-8 JSON with a top-level array of Control objects.

The export must not add comments, wrapper objects, tenant identifiers, connection identifiers, or Power Automate-specific metadata to the Control array.

## 11. Snapshot Manifest Contract

A successful snapshot package ends with:

```text
security_snapshot_manifest_<snapshot_id>.json
```

The manifest is created **only after** all three source-data artifacts have been written successfully. It acts as the completion marker for the logical package.

Required manifest fields:

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

Required successful status:

```text
complete
```

Example shape:

```json
{
  "snapshot_id": "20260824_090000",
  "as_of_date": "2026-08-24",
  "generated_at_local": "2026-08-24T09:00:00",
  "control_file": "security_control_snapshot_20260824_090000.json",
  "submission_file": "security_submission_snapshot_20260824_090000.csv",
  "action_file": "security_action_snapshot_20260824_090000.csv",
  "control_rows": 5,
  "submission_rows": 17,
  "action_rows": 7,
  "status": "complete"
}
```

The example row counts above illustrate the schema only and are not contractual acceptance counts for the live workbook.

The manifest is technical provenance metadata, not a business-domain entity.

## 12. Storage Boundary

Operational snapshot artifacts are stored in a private OneDrive reporting location.

Conceptual location:

```text
Cyber Governance/
└── Reporting Snapshots/
```

The exact tenant-specific path is an implementation detail and must not be hard-coded into public documentation if it exposes sensitive organizational information.

The snapshot files must not be automatically committed to GitHub because they may contain:

```text
submitted_by
owner_email
comments
operational acceptance-test data
```

Repository documentation may contain sanitized screenshots and synthetic examples only.

## 13. Power Automate Responsibility Boundary

The planned Phase 7 Power Automate flow may:

- schedule the export,
- resolve one local snapshot identity,
- read the three operational tables,
- select exact source fields,
- normalize technical date representation,
- create source snapshots,
- calculate row counts for manifest metadata,
- create the completion manifest,
- fail explicitly when required export steps fail.

The flow must not:

- determine compliance,
- derive overdue or lateness metrics,
- evaluate DQ-001 through DQ-010,
- aggregate Actions into Submission rows,
- silently repair missing or malformed source values,
- deduplicate source rows,
- overwrite canonical repository fixtures.

## 14. Planned Flow Structure

Target flow name:

```text
Cyber Governance - Weekly Reporting Snapshot
```

Target schedule:

```text
Weekly
W. Europe Standard Time
```

The exact weekday is an implementation choice for Phase 7.2.

The flow should execute after the daily 08:00 Phase 6 reminder workflow so the snapshot can include the latest confirmed reminder tracking. A 09:00 local execution is the current preferred PoC default unless implementation constraints require another time.

Logical structure:

```text
Recurrence
    ↓
Resolve snapshot_id + as_of_date
    ↓
TRY - Build Reporting Snapshot
    ├── Read ControlCatalog
    ├── Read SubmissionRegister
    ├── Read ActionRegister
    ├── Build Control JSON
    ├── Build Submission CSV
    ├── Build Action CSV
    ├── Write three source artifacts
    └── Write completion manifest

CATCH - Reporting Snapshot Failure
    ↓
Failure notification / explicit failed run
```

The concrete Power Automate implementation should use Scopes and `Configure run after` rather than pretending that a partially written package is complete.

## 15. Consistency and Concurrency Boundary

Excel Online / OneDrive does not provide a transactional multi-table snapshot for this proof of concept.

The three source tables are therefore read sequentially within one flow run. A concurrent Phase 5/6 write could theoretically occur between reads.

Phase 7 does not claim ACID or point-in-time transactional snapshot semantics.

Mitigations for the PoC are:

- one shared `snapshot_id`,
- short sequential read/export execution,
- scheduled execution after the normal daily reminder run,
- completion manifest written only after all artifacts exist,
- explicit documentation of the limitation.

A production architecture requiring stronger consistency would normally use a datastore with stronger transactional and snapshot semantics.

## 16. Planned Python Integration Boundary

The current repository CLI reads fixed canonical paths:

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

Phase 7 implementation must add an explicit external-input path while preserving those defaults.

Planned CLI parameters:

```text
--controls-path
--submissions-path
--actions-path
--output-directory
```

Existing behavior must remain valid:

```bash
python src/main.py --as-of-date 2026-08-15
```

An operational snapshot run should become possible without replacing repository fixtures, conceptually:

```bash
python src/main.py \
  --as-of-date 2026-08-24 \
  --controls-path <control-snapshot.json> \
  --submissions-path <submission-snapshot.csv> \
  --actions-path <action-snapshot.csv> \
  --output-directory <operational-output-directory>
```

The external files must pass the same existing Extract contracts. Phase 7 must not create a second set of business semantics for operational data.

## 17. Python Processing Responsibilities Remain Unchanged

After loading an explicit operational snapshot, Python continues to own:

```text
NORMALIZE
    ↓
VALIDATE DQ-001 ... DQ-010
    ↓
CONTROL ENRICHMENT
    ↓
ACTION AGGREGATION
    ↓
DERIVED TIMING / GOVERNANCE METRICS
    ↓
CURATED OUTPUTS
```

The existing semantic rules remain unchanged, including:

```text
Evidence Present != Compliant
Not Submitted != Non-Compliant
Non-Compliant != Overdue
Compliance != Timeliness
Compliance != Data Quality
Submission Status != Action Status
Unknown != False
Not Evaluated != Failed
```

## 18. Reporting Outputs Produced Downstream

When the snapshot is processed by Python, the existing contractual outputs remain:

```text
curated_control_status.csv
data_quality_issues.csv
ai_review_queue.json
```

Phase 7 does not redesign those outputs merely because the source is operational rather than canonical.

Phase 8 may decide whether additional Action-grain reporting output is required for Power BI. That decision is intentionally not pulled forward into Phase 7.0.

## 19. Process-Impact Dependency

Phase 6 operationalizes:

```text
reminder_count
last_reminder_at
```

Phase 7 must carry those facts into the reporting process so Phase 8 can support evidence-backed measures such as:

```text
Total Automated Reminders
Submissions Requiring Follow-up
Average Reminder Count
Open Actions
```

Phase 7 does not invent labour-savings, ROI, or time-saved claims.

## 20. Known Lifecycle Limitation Preserved

Phase 6 documents that a missing-submission Action is not yet automatically completed when Phase 5 later receives evidence and the Submission moves to `In Review`.

Phase 7 must export that operational state as stored. It must not infer or repair the Action lifecycle during reporting export.

```text
Reporting export
!=
Operational state repair
```

## 21. Error Handling Contract

A snapshot is successful only when all required source artifacts are written and the completion manifest is created.

If a required read, serialization, or file-write step fails:

- the flow run must be marked failed or handled through an explicit failure path,
- no `complete` manifest may be written,
- the failure must not be presented as a valid reporting snapshot,
- already written partial files may remain for troubleshooting but are not a complete package.

The PoC does not require an enterprise telemetry platform.

## 22. Acceptance Contract for Later Phase 7 Implementation

Phase 7 implementation is not complete until all of the following are proven.

### Snapshot creation

- one Control JSON exists,
- one Submission CSV exists,
- one Action CSV exists,
- one completion manifest exists,
- all four artifacts share the same `snapshot_id`.

### Source completeness

- `control_rows` equals the operational `ControlCatalog` row count observed for the run,
- `submission_rows` equals the operational `SubmissionRegister` row count observed for the run,
- `action_rows` equals the operational `ActionRegister` row count observed for the run.

No fixed 5 / 15 / 5 live acceptance counts are required because the operational workbook intentionally evolves independently from canonical fixtures.

### Physical contracts

- Control JSON is a top-level array with the exact required Control fields,
- Submission CSV has the exact required header and order,
- Action CSV has the exact required header and order,
- dates are exported as `YYYY-MM-DD`,
- missing CSV values remain empty fields,
- CSV quoting handles commas, quotes, and line breaks correctly,
- `reminder_count` is integer-compatible.

### Phase 6 state propagation

At least one operational Action with reminder history is demonstrated in the Action snapshot so `reminder_count` and `last_reminder_at` are proven to cross the reporting boundary.

### Python integration

- explicit snapshot paths are accepted,
- the operational snapshot can be processed end to end,
- fatal input-contract failures still fail explicitly,
- DQ findings remain business outputs rather than pipeline crashes,
- canonical default-path execution remains unchanged.

### Regression

The complete existing test suite must remain green and the canonical acceptance run must still produce the documented Phase 2–4 results for:

```text
as_of_date = 2026-08-15
```

### Privacy and repository governance

- operational snapshot files are not committed,
- public screenshots are sanitized,
- no credentials, tokens, tenant identifiers, connection identifiers, or reachable private addresses are published.

## 23. Phase 7.0 Definition of Done

Phase 7.0 is complete when the repository contains a reviewed contract that fixes:

- the Phase 7 purpose and scope,
- the three operational source tables,
- the snapshot package and naming convention,
- the shared snapshot-time semantics,
- the Control JSON schema,
- the Submission CSV schema and grain,
- the Action CSV schema and grain,
- serialization and missing-value rules,
- the completion manifest,
- the private storage boundary,
- the Power Automate responsibility boundary,
- the non-transactional Excel consistency limitation,
- the planned Python external-input boundary,
- the preservation of canonical repository fixtures,
- the later implementation acceptance criteria.

No runtime implementation is required for Phase 7.0.

**Phase 7.0 status: COMPLETE**

**Phase 7 runtime implementation status: NOT IMPLEMENTED**

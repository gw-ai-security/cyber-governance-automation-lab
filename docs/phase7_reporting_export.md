# Phase 7 Reporting Export Contract

## Status

**PHASE 7 COMPLETE — IMPLEMENTED AND END-TO-END ACCEPTED**

Work-package status:

```text
Phase 7.0 Reporting export contract          = COMPLETE
Phase 7.1 Implementation preparation         = COMPLETE
Phase 7.2 Power Automate reporting snapshot  = COMPLETE / acceptance-tested
Phase 7.3 Python external input boundary     = COMPLETE / automated-tested
Phase 7 WP3 private end-to-end acceptance    = COMPLETE
Full Phase 7                                 = COMPLETE
```

Phase 7 implements the controlled reporting bridge between the operational Microsoft 365 state established in Phases 5–6 and the deterministic Python/reporting pipeline established in Phases 2–4.

Core boundary:

```text
Power Automate exports source facts.
Python owns Data Quality, Control enrichment,
Action aggregation, and derived metrics.
```

## 1. Purpose

Phase 7 creates a controlled and reproducible export of current operational governance state without replacing the canonical repository fixtures.

Implemented path:

```text
Operational Microsoft 365 workbook
        ↓
Power Automate reporting snapshot
        ↓
private snapshot package
        ↓
explicit Python source paths
        ↓
existing deterministic pipeline
        ↓
curated reporting outputs
        ↓
Phase 8 Power BI — planned
```

Phase 7 reuses the existing Python semantics. It does not duplicate Phase 3 business logic inside Power Automate.

## 2. Scope

Phase 7 implements:

- weekly export of operational `ControlCatalog`, `SubmissionRegister`, and `ActionRegister`,
- one shared `snapshot_id` and local `as_of_date`,
- exact source-field selection and serialization contracts,
- date normalization to repository-compatible `YYYY-MM-DD` representation,
- private OneDrive snapshot storage,
- a completion manifest written after all source artifacts succeed,
- explicit failure behavior for incomplete snapshot attempts,
- an explicit all-or-none Python external-input boundary,
- custom output-directory support,
- real private operational snapshot → Python end-to-end acceptance,
- preservation of the deterministic canonical baseline.

Phase 7 does **not** implement:

- Power BI reports or DAX measures,
- AI model invocation,
- REST APIs,
- compliance decisions,
- automatic remediation or source-data repair,
- new DQ rule IDs,
- evidence-file storage,
- transactional snapshot guarantees across Excel tables,
- automatic snapshot discovery or scheduled Python execution,
- automatic publication of operational data to GitHub.

## 3. Data-Plane Boundary

### Canonical repository plane

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

These are deterministic synthetic acceptance fixtures and remain unchanged by operational Phase 7 processing.

### Operational Microsoft 365 plane

```text
Cyber_Governance_Control_Register.xlsx
├── ControlCatalog
├── SubmissionRegister
└── ActionRegister
```

These tables represent current PoC operational state produced or consumed by the Phase 5 evidence-intake and Phase 6 reminder workflows.

Phase 7 snapshots all three operational tables to avoid mixed-state runs such as live Submissions/Actions enriched against only the synthetic repository Control Catalog.

This does not create another business entity. The logical model remains exactly:

```text
Control
Submission
Action
Data Quality Issue
```

## 4. Snapshot Package

Every successful Phase 7 run creates one logical package with one shared `snapshot_id`:

```text
security_control_snapshot_<snapshot_id>.json
security_submission_snapshot_<snapshot_id>.csv
security_action_snapshot_<snapshot_id>.csv
security_snapshot_manifest_<snapshot_id>.json
```

`snapshot_id` is technical lineage metadata, not a business entity.

## 5. Snapshot Time Semantics

The flow resolves once per run:

```text
snapshot_id
as_of_date
generated_at_local
```

Time zone:

```text
W. Europe Standard Time
```

Representations:

```text
snapshot_id        = yyyyMMdd_HHmmss
as_of_date         = yyyy-MM-dd
generated_at_local = yyyy-MM-ddTHH:mm:ss
```

Critical rule:

```text
Python as_of_date
=
matching manifest as_of_date
```

The Phase 7.3 CLI does not automatically parse the manifest. The caller supplies the manifest date explicitly through `--as-of-date`.

## 6. Control Snapshot Contract

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
UTF-8 JSON top-level array
```

Exact Control source fields:

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

No derived reporting fields or Power Automate wrapper metadata are added.

## 7. Submission Snapshot Contract

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

All source rows are exported. Power Automate does not filter to selected compliance, timeliness, or DQ states.

## 8. Action Snapshot Contract

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

Phase 7 preserves Phase 6 source facts including:

```text
status
reminder_count
last_reminder_at
```

Action aggregation remains a Python responsibility.

## 9. Serialization Rules

Submission and Action CSV snapshots use:

| Property | Contract |
| --- | --- |
| Encoding | UTF-8 |
| Delimiter | comma |
| Header | required |
| Dates | `YYYY-MM-DD` |
| Missing values | empty CSV field |
| Quoting | standard CSV double-quote escaping |

The export does not invent literal missing-value tokens such as `NULL`, `None`, or `N/A` for genuinely missing data.

The Control snapshot is strict JSON with a top-level array.

## 10. Completion Manifest

A successful package ends with:

```text
security_snapshot_manifest_<snapshot_id>.json
```

Required fields:

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

The manifest is created **after** all three source artifacts succeed and acts as the package completion marker.

```text
partial source artifacts
without completion manifest
!=
valid snapshot package
```

## 11. Private Storage Boundary

Operational snapshots are stored in a private OneDrive reporting location conceptually represented as:

```text
Cyber Governance/
└── Reporting Snapshots/
```

Snapshot files are not committed because they can contain:

```text
owner_email
submitted_by
comments
operational acceptance state
```

Public repository evidence uses sanitized screenshots, sanitized workflow source, and non-sensitive acceptance observations.

## 12. Implemented Power Automate Runtime

Flow:

```text
Cyber Governance - Weekly Reporting Snapshot
```

Schedule:

```text
Frequency: Weekly
Interval: 1
Day: Monday
Local time: 09:00
Time zone: W. Europe Standard Time
```

The 09:00 Monday schedule follows the Phase 6 daily 08:00 reminder run so the reporting snapshot can include current confirmed reminder tracking.

Implemented logical structure:

```text
Recurrence
↓
Resolve Snapshot ID
↓
Resolve As Of Date
↓
Resolve Generated At Local
↓
TRY Build Reporting Snapshot
   ├── List Control Catalog
   ├── List Submission Register
   ├── List Action Register
   ├── Select Control Fields
   ├── Select Submission Fields
   ├── Select Action Fields
   ├── Create Control JSON
   ├── Create Submission CSV
   ├── Create Action CSV
   ├── Create Control Snapshot File
   ├── Create Submission Snapshot File
   ├── Create Action Snapshot File
   ├── Count Control Rows
   ├── Count Submission Rows
   ├── Count Action Rows
   ├── Build Snapshot Manifest
   └── Create Snapshot Manifest File
↓
CATCH Reporting Snapshot Failure
   ├── Send Snapshot Failure Notification
   └── Terminate Snapshot Flow as Failed
```

All three Excel reads use ISO 8601 connector date output and pagination threshold 5000.

## 13. Power Automate Responsibility Boundary

The flow may:

- schedule the export,
- resolve run-level snapshot metadata,
- read the three operational source tables,
- select exact source fields,
- normalize technical date representation,
- create source artifacts,
- count source rows for provenance,
- create the completion manifest,
- fail explicitly on export failure.

The flow must not:

- determine compliance,
- derive overdue or lateness,
- evaluate DQ-001 through DQ-010,
- aggregate Actions into Submission rows,
- repair malformed source values,
- deduplicate source rows,
- overwrite canonical repository fixtures.

## 14. Failure Semantics

If a required read, serialization, or write fails:

- TRY fails,
- CATCH executes,
- a failure notification is issued,
- the run is explicitly terminated as Failed,
- no successful completion manifest is created for that run.

Already written partial files may remain privately for troubleshooting but are not a valid reporting snapshot.

Phase 7.2 acceptance proved this behavior with a reversible deterministic failure injection.

## 15. Empty Action Dataset

Phase 7.2 acceptance verified an `ActionRegister` with zero data rows.

Observed package semantics:

```text
action_rows = 0
status      = complete
```

The Action snapshot was emitted as a header-only CSV with the exact ten-column Action header.

Phase 7.3 automated tests independently proved that this header-only CSV is processed successfully as:

```text
Actions loaded: 0
```

## 16. Consistency and Concurrency Boundary

Excel Online / OneDrive does not provide a transactional multi-table snapshot.

The source tables are read sequentially. A concurrent Phase 5/6 write could theoretically occur between reads.

PoC mitigations:

- one shared `snapshot_id`,
- short sequential reads,
- snapshot scheduled after the normal reminder run,
- completion manifest written only after all source artifacts exist,
- explicit documentation of the limitation.

Phase 7 does not claim ACID or point-in-time transactional consistency.

## 17. Python Integration Boundary

Canonical defaults remain:

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

Phase 7.3 adds:

```text
--controls-path
--submissions-path
--actions-path
--output-directory
```

Source overrides are all-or-none:

```text
none supplied      → all canonical defaults
all three supplied → one explicit coherent source set
partial set        → rejected
```

An explicitly requested missing or malformed external source fails; it does not fall back to canonical data.

Both modes reuse the existing:

```text
EXTRACT → NORMALIZE → VALIDATE → TRANSFORM / ENRICH → DERIVE → LOAD
```

pipeline.

## 18. Python Responsibilities Remain Unchanged

Python continues to own:

```text
DQ-001 through DQ-010
Control enrichment
Action aggregation
evidence_present
overdue_flag
submission_late
days_overdue
days_late
data_quality_status
AI review queue eligibility
```

Critical semantic separations remain unchanged:

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

## 19. Existing Reporting Outputs

Operational and canonical inputs both produce the same contractual outputs:

```text
curated_control_status.csv
data_quality_issues.csv
ai_review_queue.json
```

Phase 7 does not add another processing model merely because the source is operational.

## 20. End-to-End Acceptance Result

The final WP3 acceptance processed one real private operational snapshot with:

```text
snapshot_id = 20260823_112030
as_of_date  = 2026-08-23
status      = complete
```

Manifest source counts:

```text
Controls:    5
Submissions: 17
Actions:     2
```

Python loaded exactly:

```text
Controls loaded: 5
Submissions loaded: 17
Actions loaded: 2
```

and produced:

```text
DQ issues: 5
Valid submissions: 12
Invalid submissions: 5
AI review queue items: 3
```

Acceptance additionally proved:

- 17 operational Submission rows remained 17 curated rows,
- five DQ findings remained non-fatal outputs,
- `reminder_count` and `last_reminder_at` crossed the reporting boundary,
- the operational AI queue followed the existing eligibility policy,
- the canonical `2026-08-15` regression remained unchanged,
- the full suite remained 53 passing tests,
- canonical source fixtures remained unchanged.

See [phase7_end_to_end_acceptance.md](phase7_end_to_end_acceptance.md).

## 21. Process-Impact Dependency

Phase 6 operationalizes:

```text
reminder_count
last_reminder_at
```

Phase 7 has now proven these facts across the reporting boundary. Phase 8 can therefore base later evidence-backed reporting measures on actual curated reminder state, for example:

```text
Total Automated Reminders
Submissions Requiring Follow-up
Average Reminder Count
Open Actions
```

Phase 7 does not invent labour-savings, ROI, or time-saved claims.

## 22. Lifecycle Limitation Preserved

The current PoC does not automatically complete a missing-submission Action when later Phase 5 evidence moves the related Submission to `In Review`.

Phase 7 exports and processes the actual stored Action state.

```text
Reporting bridge
!=
Operational lifecycle repair
```

## 23. Privacy and Repository Governance

- operational snapshots remain private,
- public screenshots are sanitized,
- private tenant Solution ZIPs are not committed,
- credentials, tokens, tenant identifiers, connection identifiers, and reachable private addresses are not published,
- the public workflow source uses deployment placeholders,
- canonical repository fixtures remain synthetic.

## 24. Phase 7 Definition of Done

Phase 7 is complete because:

- [x] the snapshot contract is defined,
- [x] the Power Automate runtime is implemented,
- [x] the weekly Monday 09:00 schedule is implemented,
- [x] all three operational source tables are exported,
- [x] exact physical contracts are acceptance-tested,
- [x] completion-manifest semantics are acceptance-tested,
- [x] failure behavior is acceptance-tested,
- [x] empty Action behavior is acceptance-tested,
- [x] public Power Automate source is sanitized,
- [x] Python accepts explicit coherent source paths,
- [x] partial source sets are rejected,
- [x] fatal external input failures do not silently fall back,
- [x] the real private operational snapshot was processed end to end,
- [x] manifest counts matched Python load counts,
- [x] reminder state reached curated reporting,
- [x] DQ behavior remained unchanged,
- [x] the canonical regression remained unchanged,
- [x] all 53 automated tests passed after acceptance,
- [x] canonical fixtures remained unchanged,
- [x] private operational data remained outside GitHub.

**Final Phase 7 status: COMPLETE**

Phase 8 Power BI is the next planned project phase and is not implemented by this contract.

## References

- [phase7_implementation_plan.md](phase7_implementation_plan.md) — historical Phase 7.1 implementation plan
- [phase7_power_automate_acceptance.md](phase7_power_automate_acceptance.md) — Phase 7.2 runtime acceptance
- [phase7_python_external_input.md](phase7_python_external_input.md) — Phase 7.3 Python input-boundary acceptance
- [phase7_end_to_end_acceptance.md](phase7_end_to_end_acceptance.md) — final WP3 acceptance

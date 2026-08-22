# Phase 7.1 Reporting Export Implementation Plan

## Status

**PHASE 7.1 IMPLEMENTATION PREPARATION COMPLETE — RUNTIME IMPLEMENTATION NOT STARTED**

Phase 7.1 converts the Phase 7.0 reporting-export contract into an executable implementation plan. It fixes the concrete Power Automate build order, action names, schedule, data mappings, failure-path structure, Python handoff sequence, test order, and evidence requirements before runtime implementation begins.

Phase 7.1 does not itself create the live Power Automate flow, generate operational snapshot files, or change the Python CLI.

Canonical upstream contract:

- [phase7_reporting_export.md](phase7_reporting_export.md)
- [architecture.md](architecture.md)
- [data_contract.md](data_contract.md)
- [phase6_reminder_automation.md](phase6_reminder_automation.md)

If implementation convenience conflicts with those contracts, the implementation must change rather than silently changing the business or data semantics.

## 1. Implementation Objective

The Phase 7 runtime must implement this boundary:

```text
Cyber_Governance_Control_Register.xlsx
├── ControlCatalog
├── SubmissionRegister
└── ActionRegister
        ↓
Cyber Governance - Weekly Reporting Snapshot
        ↓
private OneDrive snapshot package
        ├── Control JSON
        ├── Submission CSV
        ├── Action CSV
        └── completion manifest
        ↓
Python pipeline using explicit snapshot paths
        ↓
existing curated outputs
```

Power Automate exports source facts. Python remains responsible for Data Quality, Control enrichment, Action aggregation, and derived metrics.

## 2. Fixed Schedule Decision

Flow name:

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

Rationale:

- Phase 6 runs daily at 08:00 local time.
- A 09:00 reporting run allows the normal Monday reminder run to complete first.
- The snapshot can therefore include current `reminder_count` and `last_reminder_at` values produced by Phase 6.
- The choice is a PoC operating convention, not a regulatory requirement.

The flow must use the named Windows time-zone identifier rather than a hard-coded UTC offset.

## 3. Private Storage Convention

Target logical private folder:

```text
Cyber Governance/
└── Reporting Snapshots/
```

The tenant-specific OneDrive path is selected during Phase 7.2 implementation and is not published in repository documentation.

Each run writes four artifacts directly into the reporting-snapshot folder using one shared `snapshot_id`:

```text
security_control_snapshot_<snapshot_id>.json
security_submission_snapshot_<snapshot_id>.csv
security_action_snapshot_<snapshot_id>.csv
security_snapshot_manifest_<snapshot_id>.json
```

Operational snapshot files are not committed to GitHub.

## 4. Power Automate Action Naming Contract

The implementation should use stable descriptive display names. Internal Power Automate identifiers may differ, but documentation and screenshots use the following logical names.

```text
Recurrence
Resolve Snapshot ID
Resolve As-Of Date
Resolve Generated At Local

TRY - Build Reporting Snapshot
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

CATCH - Reporting Snapshot Failure
├── Send Snapshot Failure Notification
└── Terminate Snapshot Flow
```

The names deliberately distinguish `List`, `Select`, `Create`, `Count`, and `Build` responsibilities.

## 5. Snapshot Context Expressions

The three run-level values are resolved once before the TRY scope.

### `Resolve Snapshot ID`

Target value:

```text
formatDateTime(
  convertTimeZone(utcNow(),'UTC','W. Europe Standard Time'),
  'yyyyMMdd_HHmmss'
)
```

Example:

```text
20260824_090000
```

### `Resolve As-Of Date`

Target value:

```text
formatDateTime(
  convertTimeZone(utcNow(),'UTC','W. Europe Standard Time'),
  'yyyy-MM-dd'
)
```

Example:

```text
2026-08-24
```

### `Resolve Generated At Local`

Target value:

```text
formatDateTime(
  convertTimeZone(utcNow(),'UTC','W. Europe Standard Time'),
  'yyyy-MM-ddTHH:mm:ss'
)
```

Example:

```text
2026-08-24T09:00:00
```

Every filename and manifest field must reuse these resolved values. Later actions must not call `utcNow()` again to construct a second snapshot identity.

## 6. Source Read Order

Inside `TRY - Build Reporting Snapshot`, read tables sequentially in this order:

```text
1. ControlCatalog
2. SubmissionRegister
3. ActionRegister
```

All three tables come from:

```text
Cyber_Governance_Control_Register.xlsx
```

The flow must not filter the source rows during the export read.

Expected connector action type:

```text
Excel Online (Business)
→ List rows present in a table
```

The implementation should keep concurrency low/sequential for this small PoC workbook rather than creating parallel Excel reads that complicate the consistency boundary.

## 7. Control Mapping

`Select Control Fields` maps every operational Control row to exactly:

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

No field is derived, renamed, case-corrected, or enriched.

Logical mapping:

| Output field | Source |
| --- | --- |
| `control_id` | current Control row `control_id` |
| `control_name` | current Control row `control_name` |
| `control_statement` | current Control row `control_statement` |
| `business_unit` | current Control row `business_unit` |
| `owner_role` | current Control row `owner_role` |
| `owner_email` | current Control row `owner_email` |
| `frequency` | current Control row `frequency` |
| `risk_level` | current Control row `risk_level` |

`Create Control JSON` serializes the selected array as the top-level JSON array. It must not add a wrapper object or Power Automate metadata.

## 8. Submission Mapping

`Select Submission Fields` maps every operational Submission row to exactly:

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

Exact output order is contractual.

### Date normalization

`due_date` is required by the source contract. The export representation is normalized to:

```text
yyyy-MM-dd
```

`submitted_at` may be empty. Its mapping must preserve an empty source as an empty output rather than attempting to format an empty value.

Logical expression shape:

```text
if(
  empty(item()?['submitted_at']),
  '',
  formatDateTime(item()?['submitted_at'],'yyyy-MM-dd')
)
```

The equivalent conditional pattern is used anywhere an optional date can be empty.

The flow must not generate:

```text
NULL
null
None
N/A
```

for a genuinely missing CSV value.

## 9. Action Mapping

`Select Action Fields` maps every operational Action row to exactly:

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

Exact output order is contractual.

Date fields are normalized to `yyyy-MM-dd`.

`last_reminder_at` uses the same empty-value guard as optional `submitted_at`.

`reminder_count` is exported as the source integer-compatible value. Phase 7 does not increment, aggregate, reset, or otherwise modify it.

The flow must preserve Phase 6 reminder facts:

```text
status
reminder_count
last_reminder_at
```

## 10. CSV Creation Contract

`Create Submission CSV` and `Create Action CSV` use the normalized selected arrays as their source.

The CSV actions must be configured so the generated headers and order match the contracts exactly.

Submission header:

```csv
submission_id,control_id,reporting_period,due_date,status,evidence_reference,submitted_at,submitted_by,comment
```

Action header:

```csv
action_id,control_id,submission_id,owner_email,created_at,due_date,status,reminder_count,last_reminder_at,description
```

Phase 7.2 must verify actual connector output for:

- commas in `comment` or `description`,
- embedded double quotes,
- empty optional values,
- empty Action dataset behavior.

If the connector does not emit a header-only CSV for an empty Action array, Phase 7.2 must add an explicit empty-dataset branch that emits the exact contractual Action header. This is a serialization edge case, not a business-rule change.

## 11. Snapshot File Creation Order

Write the three source artifacts before the completion manifest:

```text
1. Create Control Snapshot File
2. Create Submission Snapshot File
3. Create Action Snapshot File
4. Create Snapshot Manifest File
```

The manifest is the final completion marker and may only be created after all three source files succeed.

Filename expressions conceptually concatenate the fixed prefix with the output of `Resolve Snapshot ID`.

Example:

```text
security_submission_snapshot_<snapshot_id>.csv
```

No file may overwrite the canonical repository fixtures.

## 12. Row Count Contract

The manifest records the number of rows read from each operational table.

Logical counts:

```text
control_rows    = length(body('List_Control_Catalog')?['value'])
submission_rows = length(body('List_Submission_Register')?['value'])
action_rows     = length(body('List_Action_Register')?['value'])
```

Actual Power Automate internal action references may differ from the display names and must be inserted using the expression editor rather than manually guessing escaped identifiers.

The counts describe the source rows observed by the flow. They are not fixed to canonical repository counts.

## 13. Snapshot Manifest Build

`Build Snapshot Manifest` creates exactly the required metadata fields:

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

Conceptual payload:

```json
{
  "snapshot_id": "<resolved snapshot id>",
  "as_of_date": "<resolved as-of date>",
  "generated_at_local": "<resolved local timestamp>",
  "control_file": "security_control_snapshot_<snapshot_id>.json",
  "submission_file": "security_submission_snapshot_<snapshot_id>.csv",
  "action_file": "security_action_snapshot_<snapshot_id>.csv",
  "control_rows": 0,
  "submission_rows": 0,
  "action_rows": 0,
  "status": "complete"
}
```

The zero counts above illustrate field types only. Runtime counts come from the source actions.

The manifest file is created only after all three source snapshot files succeed.

## 14. Failure Path Design

Use two Scopes:

```text
TRY - Build Reporting Snapshot
CATCH - Reporting Snapshot Failure
```

`CATCH - Reporting Snapshot Failure` is configured with `Configure run after` so it runs when the TRY scope:

```text
has failed
has timed out
```

A deliberate cancel is not treated as a successful package.

Failure behavior:

```text
TRY fails
    ↓
CATCH runs
    ↓
Send Snapshot Failure Notification
    ↓
Terminate Snapshot Flow = Failed
```

The failure notification should contain only operational metadata needed to identify the failed flow execution. It must not include evidence contents, credentials, tokens, or snapshot file contents.

No `complete` manifest may be created from the CATCH path.

Partial source files may remain in private storage for troubleshooting and are not valid snapshots without the completion manifest.

## 15. Power Automate Build Sequence

Phase 7.2 should be implemented in this exact order:

1. Create scheduled cloud flow with the fixed name.
2. Configure Monday 09:00 / `W. Europe Standard Time` recurrence.
3. Add and test the three snapshot-context Compose actions.
4. Add `TRY - Build Reporting Snapshot` scope.
5. Add the three sequential Excel table reads.
6. Inspect actual connector output for date representation before writing formatting expressions.
7. Add `Select Control Fields` and validate one sample object.
8. Add `Select Submission Fields` with date/missing-value handling.
9. Add `Select Action Fields` with date/missing-value handling.
10. Add Control JSON serialization.
11. Add Submission CSV serialization with exact header/order.
12. Add Action CSV serialization with exact header/order.
13. Add the three source file writes to the private reporting folder.
14. Add the three row-count Compose actions.
15. Add manifest construction.
16. Add manifest file creation last.
17. Add the CATCH scope and failure notification.
18. Configure run-after semantics.
19. Save the flow and resolve any Power Automate template-reference errors before testing.
20. Execute manual acceptance tests before enabling reliance on the weekly schedule.

No Python modification is required before the Power Automate source export has produced a contract-valid manual snapshot.

## 16. Manual Acceptance Test Sequence

The first Power Automate acceptance run must verify the export independently of Python.

### Test 1 — Snapshot context

Verify:

```text
snapshot_id uses yyyyMMdd_HHmmss
as_of_date uses yyyy-MM-dd
generated_at_local uses local time
```

All four filenames must share the same `snapshot_id`.

### Test 2 — Control snapshot

Verify:

- top-level JSON array,
- exact eight Control fields,
- no wrapper metadata,
- manifest `control_rows` equals rows read from `ControlCatalog`.

### Test 3 — Submission snapshot

Verify:

- exact nine-column header and order,
- all operational Submission rows are present,
- dates are `YYYY-MM-DD`,
- empty `submitted_at` remains empty,
- a comment containing a comma remains one CSV field.

### Test 4 — Action snapshot

Verify:

- exact ten-column header and order,
- all operational Action rows are present,
- `reminder_count` and `last_reminder_at` are preserved,
- one Phase 6 reminder-history row is visibly propagated,
- a description containing a comma remains one CSV field.

### Test 5 — Manifest completion semantics

Verify:

- manifest is created after the three source artifacts,
- filenames match the actual files,
- row counts match the source reads,
- `status = complete`.

### Test 6 — Failure path

Create a reversible test failure, for example by temporarily pointing one file-creation action at an invalid test location or another safe implementation-specific method.

Verify:

- TRY fails,
- CATCH executes,
- failure notification is produced,
- flow ends Failed,
- no `complete` manifest is created for that run.

The failure test must not damage the operational workbook or canonical repository data.

## 17. Evidence Capture Plan

After acceptance, sanitized repository evidence should be stored under:

```text
docs/screenshots/phase-7-reporting-export/
```

Planned files:

```text
phase7_flow_overview.webp
phase7_snapshot_context.webp
phase7_source_reads.webp
phase7_serialization.webp
phase7_snapshot_files.webp
phase7_manifest.webp
phase7_failure_path.webp
```

Screenshots must redact or exclude:

- real `owner_email`,
- authenticated `submitted_by`,
- tenant identifiers,
- connection identifiers,
- private OneDrive paths when revealing them would expose organizational metadata,
- secrets or tokens.

## 18. Python Handoff Sequence

Python integration starts only after the Power Automate export passes the physical snapshot acceptance tests.

Planned repository implementation order:

```text
1. Extend CLI argument parsing
2. Preserve current default paths
3. Pass explicit paths into run_pipeline(...)
4. Add explicit output-directory support
5. Add focused CLI/input-path tests
6. Run complete regression suite
7. Process one private operational snapshot locally
8. Compare manifest/source counts with Python load counts
9. Preserve canonical acceptance result
```

Planned CLI surface:

```text
--controls-path
--submissions-path
--actions-path
--output-directory
```

The existing command remains valid:

```bash
python src/main.py --as-of-date 2026-08-15
```

The runtime snapshot `as_of_date` must be taken from the matching manifest and supplied explicitly to Python.

## 19. Repository Change Boundaries for Runtime Implementation

Expected Python-phase files:

```text
src/main.py
tests/test_main.py
```

Additional source modules should not be introduced unless implementation evidence shows that `main.py` cannot remain a thin orchestrator without duplication.

Files that must remain unchanged merely because live operational state differs:

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

Generated private operational snapshots are not repository fixtures.

## 20. Work Packages

Phase 7 runtime work is divided into four work packages.

### WP1 — Power Automate Snapshot Flow

Deliver:

- scheduled flow,
- snapshot context,
- three source reads,
- three source serializers,
- three source files,
- completion manifest,
- failure scope.

Exit condition:

- manual contract-valid snapshot exists in private OneDrive.

### WP2 — Python External Input Boundary

Deliver:

- explicit input-path CLI parameters,
- explicit output-directory parameter,
- unchanged default behavior,
- focused automated tests.

Exit condition:

- both canonical and explicit-path runs work.

### WP3 — End-to-End Acceptance

Deliver:

- process one real operational snapshot,
- verify load counts and DQ behavior,
- verify Phase 6 reminder fields reach curated reporting,
- rerun canonical regression.

Exit condition:

- operational snapshot produces existing contractual outputs without mutating canonical fixtures.

### WP4 — Documentation and Evidence

Deliver:

- update Phase 7 contract status,
- update README/current architecture,
- add sanitized screenshots,
- document actual acceptance observations and limitations.

Exit condition:

- repository claims exactly match implemented evidence.

## 21. Definition of Done — Phase 7.1

Phase 7.1 is complete when:

- the weekly schedule is fixed,
- Power Automate action naming is fixed,
- snapshot-context expressions are fixed,
- source read order is fixed,
- Control/Submission/Action mappings are explicit,
- date and missing-value handling is specified,
- CSV edge cases to test are identified,
- file-write and manifest order is fixed,
- failure-path run-after semantics are specified,
- the manual Power Automate acceptance sequence is fixed,
- the screenshot/evidence plan is fixed,
- the Python handoff order is fixed,
- runtime work packages and exit criteria are defined,
- no runtime implementation is falsely claimed.

**Phase 7.1 status: COMPLETE**

**Phase 7 runtime implementation status: NOT IMPLEMENTED**

## 22. Next Step

Phase 7.2 begins the actual Power Automate implementation of:

```text
Cyber Governance - Weekly Reporting Snapshot
```

The build must follow Sections 2–17 of this plan and the authoritative Phase 7.0 contract.
# Phase 7.2 — Power Automate Reporting Snapshot Acceptance

## Status

**POWER AUTOMATE RUNTIME IMPLEMENTED AND ACCEPTANCE-TESTED**

Phase 7.2 implements the scheduled Power Automate reporting snapshot defined by the Phase 7.0 contract and prepared in Phase 7.1.

This document records the observed runtime evidence for the Power Automate portion only. The Python external-input bridge remains a separate Phase 7 work package.

## Implemented Flow

```text
Cyber Governance - Weekly Reporting Snapshot
```

Schedule:

```text
Weekly
Monday
09:00
W. Europe Standard Time
```

Implemented structure:

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

CATCH Reporting Snapshot Failure
   ├── Send Snapshot Failure Notification
   └── Terminate Snapshot Flow
```

## Source Reads

All three Excel Online (Business) reads use:

```text
dateTimeFormat = ISO 8601
pagination = enabled
pagination threshold = 5000
```

The final runtime source is the operational workbook with:

```text
ControlCatalog
SubmissionRegister
ActionRegister
```

No test table or failure-injection action remains in the final exported solution.

## Normal Happy-Path Acceptance

A successful operational run produced one logical package with a shared snapshot ID.

Observed clean acceptance counts:

```text
Controls:     5
Submissions: 17
Actions:      2
status: complete
```

Physical outputs:

```text
security_control_snapshot_<snapshot_id>.json
security_submission_snapshot_<snapshot_id>.csv
security_action_snapshot_<snapshot_id>.csv
security_snapshot_manifest_<snapshot_id>.json
```

Validated properties:

- Control snapshot is a JSON top-level array.
- Control objects contain exactly the eight source fields.
- Submission CSV contains exactly nine contractual columns.
- Action CSV contains exactly ten contractual columns.
- Dates serialize as `YYYY-MM-DD`.
- missing optional values remain empty rather than synthetic missing-value tokens.
- CSV quoting preserves fields containing commas.
- Action `reminder_count` and `last_reminder_at` cross the reporting boundary.
- manifest file names match the three generated source artifacts.
- manifest row counts match the exported source rows.
- `status = complete`.
- CATCH is skipped on a successful run.

## Source-Data Hygiene Finding

The first happy-path run exposed one fully blank Excel table row in `ControlCatalog` and one fully blank row in `SubmissionRegister`.

The flow correctly exported the source facts; it did not silently filter them.

The operational workbook was corrected by removing the blank table rows. A repeat run then produced:

```text
control_rows = 5
submission_rows = 17
action_rows = 2
```

No filter was added to Power Automate because the project boundary remains:

```text
Power Automate exports source facts.
Python owns deterministic validation.
```

## Failure-Path Acceptance

A temporary deterministic runtime failure was injected inside the TRY scope using a division-by-zero expression.

Observed behavior:

```text
TRY Build Reporting Snapshot       → Failed
Create Snapshot Manifest File      → Skipped
CATCH Reporting Snapshot Failure   → Executed
Send Snapshot Failure Notification → Succeeded
Terminate Snapshot Flow            → Executed as Failed
Overall flow run                    → Failed
```

The three source artifacts written before the injected failure could exist, but the completion manifest for that snapshot ID did not exist.

This proves the intended completion rule:

```text
partial source files
without completion manifest
!=
valid snapshot package
```

The failure-injection action was removed after acceptance.

## Empty-Action Acceptance

A temporary header-only Excel table with the Action schema was used to test a source state with zero Actions without deleting operational Action records.

Observed manifest:

```text
control_rows = 5
submission_rows = 17
action_rows = 0
status = complete
```

The Action CSV was successfully generated as a **header-only CSV** with the exact contractual header:

```csv
action_id,control_id,submission_id,owner_email,created_at,due_date,status,reminder_count,last_reminder_at,description
```

Therefore no special empty-dataset branch is required.

The temporary test table was removed and the final flow was restored to `ActionRegister`.

## Final Smoke Run

After all test-only modifications were removed, a final normal run completed successfully with:

```text
control_rows = 5
submission_rows = 17
action_rows = 2
status = complete
```

This confirms the final runtime was restored after acceptance testing.

## Flow-as-Code / ALM Evidence

The Phase 7 flow was not built entirely through manual designer clicks.

The implementation used this controlled loop:

```text
real tenant unmanaged Solution scaffold
        ↓
export
        ↓
inspect workflow JSON and connector bindings
        ↓
programmatically extend workflow definition
        ↓
pack/import Solution
        ↓
bind existing Connection References
        ↓
Power Automate designer validation
        ↓
runtime acceptance tests
```

The generated Solution imported successfully and the generated workflow rendered correctly in the Power Automate designer.

Final private unmanaged export inspected for this acceptance:

```text
Version: 1.0.0.5
Managed: 0
SHA-256: ac8cedbea709c7ac06d928ed77de8f685f17b79e0cb20a126263a77efaea4213
```

The private deployment ZIP itself is intentionally not committed.

## Public Source-Control Boundary

The repository contains a sanitized workflow representation under:

```text
power_automate/solutions/cyber_governance_automation/
```

The public source removes or replaces:

- reachable notification recipient,
- OneDrive drive identifier,
- workbook file identifier,
- Excel table identifiers,
- tenant-specific Connection Reference logical names.

Operational snapshot files remain private because they can contain responder identity, Control-owner e-mail, comments, and acceptance-test state.

## Acceptance Matrix

| Test | Result |
| --- | --- |
| Solution import | PASS |
| Connection Reference mapping | PASS |
| Workflow designer rendering | PASS |
| Weekly schedule | PASS |
| Snapshot context | PASS |
| ISO-8601 reads | PASS |
| Pagination | PASS |
| Happy-path package | PASS |
| Shared snapshot ID | PASS |
| Control JSON contract | PASS |
| Submission CSV contract | PASS |
| Action CSV contract | PASS |
| Manifest consistency | PASS |
| Reminder-state propagation | PASS |
| Failure path | PASS |
| Failure notification | PASS |
| Explicit failed termination | PASS |
| No manifest for failed partial package | PASS |
| Empty ActionRegister | PASS |
| Header-only Action CSV | PASS |
| Final cleanup/smoke run | PASS |

## Remaining Phase 7 Work

Phase 7 is not fully complete yet.

The next work package is the Python external-input boundary:

```text
--controls-path
--submissions-path
--actions-path
--output-directory
```

The canonical repository defaults and the deterministic `as_of_date = 2026-08-15` acceptance baseline must remain unchanged.

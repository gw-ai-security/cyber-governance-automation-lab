# Phase 7.1 — Reporting Export Implementation Plan

## Document Role

**HISTORICAL IMPLEMENTATION PLAN — PHASE 7.1 COMPLETE**

This document records the implementation plan that was fixed before Phase 7 runtime work began. It is retained as design/engineering evidence rather than rewritten as if it had originally described the completed system.

Current outcome:

```text
Phase 7.1 planning                         = COMPLETE
Phase 7.2 Power Automate runtime           = COMPLETE / acceptance-tested
Phase 7.3 Python external input            = COMPLETE / automated-tested
Phase 7 WP3 private end-to-end acceptance  = COMPLETE
Full Phase 7                               = COMPLETE
```

Authoritative current-state evidence:

- [phase7_reporting_export.md](phase7_reporting_export.md)
- [phase7_power_automate_acceptance.md](phase7_power_automate_acceptance.md)
- [phase7_python_external_input.md](phase7_python_external_input.md)
- [phase7_end_to_end_acceptance.md](phase7_end_to_end_acceptance.md)

## 1. Planning Objective

Phase 7.1 converted the Phase 7.0 reporting contract into an executable implementation sequence before any runtime changes were made.

The implementation plan fixed:

- flow naming,
- weekly schedule,
- snapshot metadata,
- source read order,
- exact Control/Submission/Action mappings,
- date and missing-value representation,
- source file and manifest write order,
- failure semantics,
- empty Action behavior to verify,
- private storage boundary,
- Python handoff order,
- acceptance work packages.

No business semantics were to be moved from Python into Power Automate.

## 2. Fixed Runtime Target

Planned and subsequently implemented flow:

```text
Cyber Governance - Weekly Reporting Snapshot
```

Schedule fixed by Phase 7.1 and implemented in Phase 7.2:

```text
Weekly
Monday
09:00
W. Europe Standard Time
```

Run-level snapshot values:

```text
snapshot_id        = yyyyMMdd_HHmmss
as_of_date         = yyyy-MM-dd
generated_at_local = yyyy-MM-ddTHH:mm:ss
```

The schedule intentionally follows the daily Phase 6 08:00 reminder run.

## 3. Planned Source Read Order

The runtime was required to read the operational source tables sequentially:

```text
1. ControlCatalog
2. SubmissionRegister
3. ActionRegister
```

All three sources had to be included to avoid mixed-state reporting where live Submissions or Actions were combined with only canonical synthetic reference data.

The actual Phase 7.2 implementation follows this order.

## 4. Exact Source Mappings

### Control

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

### Submission

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

### Action

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

The field order and physical serialization were contractual.

## 5. Date and Missing-Value Plan

Submission and Action date fields were to be normalized to:

```text
YYYY-MM-DD
```

Optional dates such as `submitted_at` and `last_reminder_at` had to preserve a missing source as an empty CSV value.

The flow was explicitly forbidden from inventing:

```text
NULL
null
None
N/A
```

for genuinely missing values.

Phase 7.2 acceptance confirmed this behavior.

## 6. Serialization Plan

Control output:

```text
security_control_snapshot_<snapshot_id>.json
```

Submission output:

```text
security_submission_snapshot_<snapshot_id>.csv
```

Action output:

```text
security_action_snapshot_<snapshot_id>.csv
```

Submission header:

```csv
submission_id,control_id,reporting_period,due_date,status,evidence_reference,submitted_at,submitted_by,comment
```

Action header:

```csv
action_id,control_id,submission_id,owner_email,created_at,due_date,status,reminder_count,last_reminder_at,description
```

The plan required physical testing for quoted commas, empty values, dates, and empty Action data.

## 7. Manifest and File Order

Required write order:

```text
1. Control source artifact
2. Submission source artifact
3. Action source artifact
4. Completion manifest
```

The manifest had to be the final completion marker.

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

The actual Phase 7.2 implementation follows this contract.

## 8. Failure-Path Plan

Planned logical scopes:

```text
TRY Build Reporting Snapshot
CATCH Reporting Snapshot Failure
```

Failure path:

```text
TRY fails
    ↓
CATCH runs
    ↓
Send Snapshot Failure Notification
    ↓
Terminate Snapshot Flow = Failed
```

A failed run was not allowed to create a successful completion manifest.

Phase 7.2 later proved this behavior with a reversible deterministic failure injection.

## 9. Empty Action Test Plan

The plan explicitly required verifying the connector behavior when:

```text
Action rows = 0
```

Required outcome:

```text
header-only Action CSV
```

If the connector had failed to emit a header, an explicit serialization branch would have been required.

Observed Phase 7.2 result:

```text
header-only Action CSV produced correctly
special branch not required
```

## 10. Power Automate Build Sequence

The runtime implementation order was fixed as:

1. create/configure scheduled flow,
2. resolve snapshot context,
3. add TRY scope,
4. read all three source tables,
5. inspect connector date representation,
6. map exact Control fields,
7. map exact Submission fields,
8. map exact Action fields,
9. serialize Control JSON,
10. serialize Submission CSV,
11. serialize Action CSV,
12. create source files,
13. count source rows,
14. build manifest,
15. create manifest last,
16. add CATCH and notification,
17. configure run-after semantics,
18. execute manual acceptance,
19. remove test-only artifacts,
20. final smoke run.

Phase 7.2 followed this planned structure.

## 11. Manual Acceptance Plan

The planned Power Automate acceptance included:

- snapshot context,
- Control JSON structure,
- Submission CSV contract,
- Action CSV contract,
- reminder field propagation,
- shared snapshot identity,
- manifest source counts,
- manifest-last semantics,
- failure path,
- empty Action behavior,
- final restored smoke run.

Results are recorded in [phase7_power_automate_acceptance.md](phase7_power_automate_acceptance.md).

## 12. Python Handoff Plan

Python work was intentionally scheduled after the Power Automate physical export contract had been proven.

Planned sequence:

```text
1. Extend CLI argument parsing
2. Preserve canonical defaults
3. Add explicit Control path
4. Add explicit Submission path
5. Add explicit Action path
6. Add output-directory override
7. Add focused tests
8. Run complete regression suite
9. Process one private operational snapshot
10. Reconcile manifest and Python counts
11. Verify reminder state
12. Re-run canonical regression
```

Implemented CLI surface:

```text
--controls-path
--submissions-path
--actions-path
--output-directory
```

Phase 7.3 added the all-or-none source rule to strengthen the original plan and prevent accidental canonical/operational source mixing.

## 13. Work Packages

### WP1 — Power Automate Snapshot Flow

Planned deliverables:

- scheduled flow,
- snapshot context,
- three source reads,
- three source serializers,
- three source files,
- completion manifest,
- explicit failure scope.

Final status:

```text
COMPLETE / acceptance-tested
```

### WP2 — Python External Input Boundary

Planned deliverables:

- explicit input paths,
- explicit output directory,
- unchanged canonical defaults,
- focused automated tests.

Final status:

```text
COMPLETE / automated-tested
```

### WP3 — End-to-End Acceptance

Planned deliverables:

- process one real private operational snapshot,
- verify manifest/load counts,
- verify DQ remains non-fatal,
- verify Phase 6 reminder fields reach curated reporting,
- rerun canonical acceptance.

Final status:

```text
COMPLETE
```

### WP4 — Documentation and Evidence

Planned deliverables:

- current-state README/architecture,
- acceptance observations,
- sanitized public evidence,
- explicit limitations.

Final status:

```text
COMPLETE
```

## 14. Definition of Done — Phase 7.1

Phase 7.1 was complete when the implementation decisions and acceptance sequence were fixed before runtime work began.

**Phase 7.1 status: COMPLETE**

The historical planned next step was Phase 7.2. That work, Phase 7.3, and the final WP3 acceptance have subsequently been completed.

**Current full Phase 7 status: COMPLETE**

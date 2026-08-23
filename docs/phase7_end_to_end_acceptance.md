# Phase 7 — End-to-End Reporting Bridge Acceptance

## Status

**PHASE 7 END-TO-END ACCEPTANCE COMPLETE**

This document records the final WP3 acceptance of the Phase 7 reporting bridge. It proves that one real private operational snapshot produced by the Phase 7.2 Power Automate flow can be processed through the existing Phase 3 Python semantics using the Phase 7.3 explicit input boundary, while preserving the deterministic repository baseline.

Phase 7 is complete after this acceptance.

Phase 8 Power BI remains planned and has not started.

## 1. Acceptance Boundary

The accepted end-to-end path is:

```text
Operational Microsoft 365 workbook
        ↓
Phase 7.2 Power Automate Reporting Snapshot
        ↓
private Control / Submission / Action source artifacts
        +
completion manifest
        ↓
Phase 7.3 explicit Python source paths
        ↓
existing deterministic Python pipeline
        ↓
curated_control_status.csv
data_quality_issues.csv
ai_review_queue.json
```

No operational snapshot file was copied over the canonical repository fixtures.

The responsibility boundary remained unchanged:

```text
Power Automate exports source facts.
Python owns Data Quality, Control enrichment,
Action aggregation, and derived metrics.
```

## 2. Accepted Private Snapshot

The private snapshot selected for WP3 used:

```text
snapshot_id        = 20260823_112030
as_of_date         = 2026-08-23
generated_at_local = 2026-08-23T11:20:30
status             = complete
```

Manifest-declared source counts:

```text
control_rows    = 5
submission_rows = 17
action_rows     = 2
```

The corresponding source filenames followed the Phase 7 contract:

```text
security_control_snapshot_20260823_112030.json
security_submission_snapshot_20260823_112030.csv
security_action_snapshot_20260823_112030.csv
security_snapshot_manifest_20260823_112030.json
```

The private snapshot files are not committed because operational source data can contain authenticated identities, reachable owner addresses, and operational comments.

## 3. Python Invocation

The private operational snapshot was processed using the existing CLI contract. Public documentation uses generic private paths rather than the local acceptance-test filesystem location:

```bash
python src/main.py \
  --as-of-date 2026-08-23 \
  --controls-path "/private/snapshots/security_control_snapshot_20260823_112030.json" \
  --submissions-path "/private/snapshots/security_submission_snapshot_20260823_112030.csv" \
  --actions-path "/private/snapshots/security_action_snapshot_20260823_112030.csv" \
  --output-directory "/private/processed/20260823_112030"
```

The `as_of_date` was taken from the matching completion manifest. Phase 7.3 intentionally does not auto-discover or parse the manifest.

## 4. Manifest-to-Python Count Reconciliation

Observed Python summary:

```text
Controls loaded: 5
Submissions loaded: 17
Actions loaded: 2
DQ issues: 5
Valid submissions: 12
Invalid submissions: 5
AI review queue items: 3
```

Source-count reconciliation:

| Dataset | Manifest | Python | Result |
| --- | ---: | ---: | --- |
| Controls | 5 | 5 | PASS |
| Submissions | 17 | 17 | PASS |
| Actions | 2 | 2 | PASS |

The manifest's `status = complete` and exact source counts therefore describe the source set that Python actually processed.

## 5. Data Quality Behavior

The operational snapshot produced five Submission Data Quality findings.

Observed findings:

```text
SUB-002 → DQ-004 Missing Evidence
SUB-006 → DQ-003 Invalid Status
SUB-008 → DQ-005 Duplicate Submission
SUB-009 → DQ-005 Duplicate Submission
SUB-015 → DQ-002 Unknown Control ID
```

Critical acceptance result:

```text
DQ findings
!=
pipeline failure
```

The process completed successfully, wrote the contractual outputs, retained invalid source rows in curated reporting, and classified:

```text
Valid submissions:   12
Invalid submissions:  5
```

No new DQ rule IDs or operational-data repair logic were introduced.

## 6. Submission Grain Preservation

The operational source contained:

```text
17 Submission rows
```

The curated output contained:

```text
17 Submission rows
17 unique submission_id values
```

The two Action records therefore did not multiply Submission grain.

This proves the existing Action aggregation boundary remained intact for the real operational source set.

## 7. Phase 6 Reminder-State Propagation

The accepted snapshot contained real operational reminder history produced during Phase 6 acceptance.

Observed curated state:

### `SUB-016`

```text
active_action_status   = Open
active_action_due_date = 2026-08-29
reminder_count         = 1
last_reminder_at       = 2026-08-22
overdue_flag           = True
days_overdue           = 74
```

### `SUB-017`

```text
active_action_status   = Open
active_action_due_date = 2026-08-29
reminder_count         = 2
last_reminder_at       = 2026-08-22
overdue_flag           = True
days_overdue           = 105
```

This establishes the complete reporting path for reminder facts:

```text
ActionRegister
     ↓
Power Automate Action snapshot
     ↓
Python Action aggregation
     ↓
curated Submission reporting state
```

Phase 7 did not create, increment, infer, or repair these reminder values. It carried the operational facts across the reporting boundary.

## 8. AI Review Queue Acceptance

The operational `ai_review_queue.json` used:

```text
as_of_date = 2026-08-23
```

and contained exactly:

```text
SUB-005 → Non-Compliant
SUB-016 → Overdue
SUB-017 → Overdue
```

This is consistent with the existing queue policy:

```text
data_quality_status = Valid
AND
(
    submission_status = Non-Compliant
    OR
    overdue_flag = True
)
```

No DQ-invalid Submission entered the queue.

The queue remained minimized and did not add Action owner addresses, submitter identity, evidence references, or Action descriptions.

## 9. Canonical Regression After Operational Processing

After the real operational snapshot run, the canonical repository pipeline was executed again with:

```bash
python src/main.py --as-of-date 2026-08-15
```

Observed result:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

The canonical acceptance baseline therefore remained exactly unchanged.

## 10. Automated Regression Suite

The complete repository test suite was run after the operational acceptance:

```text
53 passed in 11.08s
```

Git status after the acceptance run showed:

```text
branch: main
up to date with origin/main
nothing to commit
working tree clean
```

This provides additional evidence that private operational processing did not mutate version-controlled canonical source data.

## 11. Canonical Fixture Preservation

The following canonical files remain the deterministic acceptance fixtures:

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

Operational acceptance did not replace, rewrite, or synchronize these files.

This preserves the established data-plane rule:

```text
Operational Microsoft 365 state
!=
Canonical repository fixtures
```

## 12. Privacy and Repository Evidence Boundary

The repository does not contain the accepted private operational source package or its private processed output files.

Public evidence is limited to:

- sanitized Power Automate screenshots,
- sanitized workflow source with deployment placeholders,
- non-sensitive snapshot metadata and row counts,
- deterministic acceptance observations,
- canonical synthetic repository data.

Private values intentionally excluded from public version control include:

- authenticated responder identity,
- reachable operational owner addresses,
- tenant/environment identifiers,
- OneDrive/workbook/table identifiers,
- Connection bindings,
- private Solution deployment ZIPs.

## 13. Known Limitations Preserved

Phase 7 closes the reporting bridge but does not claim production synchronization.

Known limitations remain:

- the three Excel tables are read sequentially and do not form an ACID/transactional point-in-time snapshot,
- Python processing is explicitly invoked; there is no automatic snapshot discovery or scheduled Python execution,
- the manifest is a completion/provenance contract but is not automatically ingested by the CLI,
- the current PoC does not automatically complete an existing missing-submission Action when later evidence moves the Submission to `In Review`,
- Phase 7 does not add Action-specific DQ rule IDs,
- Excel/OneDrive remains a PoC datastore boundary,
- Power BI is not implemented by Phase 7.

## 14. Phase 7 Definition of Done

Phase 7 is accepted because:

- [x] the operational Control, Submission, and Action tables are exported,
- [x] all snapshot source artifacts share one snapshot identity,
- [x] a completion manifest is created only after source artifacts succeed,
- [x] the Power Automate failure path prevents a failed partial package from being presented as complete,
- [x] empty Action source data produces a contract-valid header-only CSV,
- [x] the final Power Automate runtime was restored and smoke-tested after acceptance fixtures,
- [x] the public Power Automate source is sanitized,
- [x] Python accepts one explicit coherent Control/Submission/Action source set,
- [x] partial source overrides are rejected,
- [x] no explicit external input silently falls back to canonical data,
- [x] the private operational package was processed end to end,
- [x] manifest source counts matched Python load counts,
- [x] DQ findings remained non-fatal business outputs,
- [x] Submission grain remained preserved,
- [x] Phase 6 reminder state reached curated reporting,
- [x] the operational AI queue followed the existing eligibility policy,
- [x] the canonical acceptance run remained unchanged,
- [x] all 53 automated tests passed,
- [x] canonical fixtures remained unchanged,
- [x] private operational data remained outside the repository.

**Final Phase 7 status: COMPLETE**

## 15. Next Phase Boundary

The next planned project phase is:

```text
Phase 8 — Power BI Dashboard
```

Phase 8 may consume the curated reporting outputs and the reminder-state fields now proven across the Phase 7 bridge. Phase 7 itself does not implement any Power BI artifact or DAX measure.

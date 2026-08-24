# Phase 8.10 — Operational Phase 7 Output Acceptance

**Status:** PHASE 8.10 COMPLETE — OPERATIONAL PHASE 7 OUTPUT ACCEPTED IN POWER BI

## Purpose and boundary

Phase 8.10 proves that the source-controlled Phase 8 Power BI model can consume
the already accepted private Phase 7 processed output without rebuilding or
changing reporting semantics. This is an acceptance step, not a build step.

The acceptance used:

- branch `feature/phase8-operational-acceptance`,
- snapshot ID `20260823_112030`,
- operational `as_of_date = 2026-08-23`,
- one private Phase 7 snapshot directory,
- one private temporary processed output directory, and
- one temporary copy of the source-controlled PBIP project.

No private source or processed data was moved into the repository.

## Snapshot and manifest acceptance

The exact accepted Phase 7 snapshot package was found outside the repository.
All four contractual files were present: Control, Submission, Action, and the
completion manifest.

Accepted non-sensitive manifest metadata:

```text
snapshot_id        = 20260823_112030
as_of_date         = 2026-08-23
generated_at_local = 2026-08-23T11:20:30
status             = complete
control_rows       = 5
submission_rows    = 17
action_rows        = 2
```

The complete status and the 5 / 17 / 2 counts matched the selected source set.
No fallback or substitution with another snapshot was used.

## Private operational processing

The existing Python CLI processed the three explicit private source paths into
a private temporary output directory. Observed result:

```text
Controls loaded: 5
Submissions loaded: 17
Actions loaded: 2
DQ issues: 5
Valid submissions: 12
Invalid submissions: 5
AI review queue items: 3
```

The processed directory contained exactly the three contractual outputs:

- `curated_control_status.csv`
- `data_quality_issues.csv`
- `ai_review_queue.json`

Power BI consumed only the first two outputs. The AI review queue remained
outside the reporting source boundary.

## Processed-output quality and grain

| Check | Observed | Expected | Result |
|---|---:|---:|---|
| ControlStatus rows | 17 | 17 | PASS |
| DataQualityIssues rows | 5 | 5 | PASS |
| Unique submission IDs | 17 | 17 | PASS |
| Unique ControlStatus source-row keys | 17 | 17 | PASS |
| DQ relationship-key orphans | 0 | 0 | PASS |

Submission grain remained one row per source Submission. The two Action rows
were aggregated by the existing Python semantics and did not multiply the 17
Submission rows.

## Temporary DataRoot and PBIP approach

The complete source-controlled Power BI project was copied to a temporary
directory outside the repository. Before opening Power BI, a file-by-file
comparison showed exactly one difference between the repository project and
the temporary copy: the `DataRoot` parameter value in the temporary
`expressions.tmdl`.

The temporary `DataRoot` pointed to the private temporary processed output
directory. The two table queries continued to append only the contractual
filenames:

```text
DataRoot\curated_control_status.csv
DataRoot\data_quality_issues.csv
```

No table, relationship, measure, DAX expression, PBIR visual, Power Query
business rule, source filename, or canonical repository fixture was changed.
The repository Power BI project was never reconfigured or saved.

This proves the intended acceptance equation:

```text
same PBIP / PBIR / TMDL model
+ different DataRoot
= operational Phase 7 processed output accepted
```

## Power BI refresh and runtime counts

Only the temporary PBIP copy was opened in Power BI Desktop. A full refresh
completed without source-loading, Power Query, typing, relationship, DAX, or
visual errors. All three existing pages loaded:

1. Management Overview
2. Control Monitoring
3. Process & Data Quality

Read-only DAX Query View confirmed:

| Runtime table | Observed rows | Expected rows | Result |
|---|---:|---:|---|
| ControlStatus | 17 | 17 | PASS |
| DataQualityIssues | 5 | 5 | PASS |

## All 21 operational measures

Every contracted measure executed successfully against the operational
dataset. A dash in the Expected column means the Phase 8.10 contract requires
the runtime observation but does not freeze an expected value for that measure.

| Measure | Observed | Expected | Result |
|---|---:|---:|---|
| Controls in Scope | 5 | 5 | PASS |
| Expected Submissions | 17 | 17 | PASS |
| Valid Submissions | 12 | 12 | PASS |
| Invalid Submissions | 5 | 5 | PASS |
| Assessed Submissions | 5 | — | OBSERVED |
| Compliant Submissions | 4 | — | OBSERVED |
| Non-Compliant Submissions | 1 | 1 | PASS |
| Assessed Compliance Rate | 80.0% | — | OBSERVED |
| Overdue Submissions | 2 | 2 | PASS |
| Late Submissions | 2 | — | OBSERVED |
| High/Critical Exceptions | 3 | — | OBSERVED |
| Overdue Submission Rate | 16.7% | 16.7% | PASS |
| Total Automated Reminders | 3 | 3 | PASS |
| Active Follow-up Submissions | 2 | 2 | PASS |
| Submissions with Reminder History | 2 | 2 | PASS |
| Average Reminders per Reminded Submission | 1.50 | 1.50 | PASS |
| Total DQ Issues | 5 | 5 | PASS |
| Submissions with DQ Issues | 5 | 5 | PASS |
| DQ Issue Rate | 29.4% | 29.4% | PASS |
| High-Severity DQ Issues | 5 | 5 | PASS |
| Missing Evidence Issues | 1 | 1 | PASS |

All 16 values directly derivable from the accepted Phase 7 contract matched
their expectations. The remaining five measures were documented only as
runtime observations and were not assigned invented targets.

## Reminder-state scenarios

Read-only DAX verified both accepted Phase 7 reminder-state rows.

### SUB-016

```text
active_action_status   = Open
active_action_due_date = 2026-08-29
reminder_count         = 1
last_reminder_at       = 2026-08-22
overdue_flag           = True
days_overdue           = 74
```

Result: PASS.

### SUB-017

```text
active_action_status   = Open
active_action_due_date = 2026-08-29
reminder_count         = 2
last_reminder_at       = 2026-08-22
overdue_flag           = True
days_overdue           = 105
```

Result: PASS.

## Data Quality acceptance

The operational runtime contained exactly five DQ rows, all with High
severity:

| Submission | Rule | Severity | Result |
|---|---|---|---|
| SUB-002 | DQ-004 Missing Evidence | High | PASS |
| SUB-006 | DQ-003 Invalid Status | High | PASS |
| SUB-008 | DQ-005 Duplicate Submission | High | PASS |
| SUB-009 | DQ-005 Duplicate Submission | High | PASS |
| SUB-015 | DQ-002 Unknown Control ID | High | PASS |

DQ findings remained visible business outputs rather than refresh failures.

## Report-page runtime acceptance

### Management Overview

The page loaded without errors and showed:

| KPI | Observed | Contract check |
|---|---:|---|
| Controls in Scope | 5 | PASS |
| Assessed Compliance Rate | 80.0% | Observation |
| Non-Compliant Submissions | 1 | PASS |
| Overdue Submissions | 2 | PASS |
| High/Critical Exceptions | 3 | Observation |
| Total DQ Issues | 5 | PASS |

The operational Submission Status Distribution contained 17 rows in total:
Compliant 7, Not Submitted 5, In Review 3, Non-Compliant 1, and Pending 1.
Existing Business Unit and Risk Level analytical visuals also rendered without
errors.

### Control Monitoring

The unfiltered page displayed all 17 operational Submission rows. Its existing
15-field contractual detail layout remained unchanged:

```text
Control ID
Control Name
Business Unit
Risk Level
Reporting Period
Submission Status
Due Date
Evidence Present
Overdue
Days Overdue
Data Quality Status
Active Action Status
Active Action Due Date
Reminder Count
Last Reminder At
```

The additional operational rows, including SUB-016 and SUB-017, were
reportable without adding a column, measure, relationship, or visual.

### Process & Data Quality

The page loaded without errors and showed:

| KPI | Observed | Expected or treatment | Result |
|---|---:|---:|---|
| Total Automated Reminders | 3 | 3 | PASS |
| Active Follow-up Submissions | 2 | 2 | PASS |
| Submissions with Reminder History | 2 | 2 | PASS |
| Late Submissions | 2 | Runtime observation | OBSERVED |
| Overdue Submission Rate | 16.7% | 16.7% | PASS |
| Total DQ Issues | 5 | 5 | PASS |
| DQ Issue Rate | 29.4% | 29.4% | PASS |
| High-Severity DQ Issues | 5 | 5 | PASS |

The rule chart, severity chart, and five-row DQ detail table rendered without
errors.

## Canonical regression after the operational test

Power BI was closed without saving. The temporary PBIP copy and private
temporary processed outputs were then deleted. The repository's canonical
pipeline was rerun with `as_of_date = 2026-08-15`.

Observed canonical result:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

The complete Python regression suite then passed:

```text
53 passed in 85.17s
```

This confirms:

```text
operational acceptance
!= canonical fixture mutation
```

## Privacy controls

The acceptance document contains no private local snapshot path, private
processed path, owner address, submitter identity, private comment, OneDrive
identifier, workbook identifier, tenant identifier, or connection identifier.
No operational source row, processed output, local Power BI cache, or private
screenshot was added to Git.

The public evidence is limited to the approved non-sensitive snapshot identity,
dates, aggregate counts, measure results, DQ rule outcomes, and the two
explicitly contracted reminder-state scenarios.

## Limitations

- The accepted private snapshot remains intentionally unavailable in public
  version control, so rerunning this acceptance requires authorized local access.
- The upstream Excel/OneDrive source package remains a sequential, non-ACID
  PoC snapshot boundary as documented by Phase 7.
- Snapshot processing and Power BI Desktop refresh remain explicitly invoked;
  this phase does not add scheduling, Power BI Service publication, gateways,
  or production monitoring.
- No screenshots containing private operational data are committed as public
  evidence.

## Definition of Done

Phase 8.10 is complete because:

- [x] the exact complete Phase 7 snapshot package was found privately,
- [x] manifest counts 5 / 17 / 2 matched the selected sources,
- [x] Python produced 5 DQ / 12 valid / 5 invalid / 3 queue items,
- [x] processed output retained 17 unique Submission rows and 5 DQ rows,
- [x] only a temporary PBIP copy received the temporary DataRoot value,
- [x] the source-controlled Power BI project remained unchanged,
- [x] full Power BI refresh completed without errors,
- [x] runtime table counts were 17 / 5,
- [x] all 21 measures executed and all contract-derived values matched,
- [x] SUB-016 and SUB-017 matched the accepted reminder evidence,
- [x] all five expected DQ findings remained present and High severity,
- [x] all three existing report pages accepted the operational dataset,
- [x] Submission grain and relationship-key integrity were preserved,
- [x] the temporary private outputs and PBIP copy were removed,
- [x] the canonical pipeline remained unchanged after operational acceptance,
- [x] all 53 automated tests passed, and
- [x] the repository/privacy boundary remained intact.

**Final Phase 8.10 status: PASS**

Phase 8.11 final documentation, screenshots, and regression closure remains.

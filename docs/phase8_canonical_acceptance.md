# Phase 8.9 — Canonical Power BI Acceptance

**Status:** PHASE 8.9 COMPLETE — CANONICAL POWER BI RUNTIME ACCEPTED

## Acceptance purpose and boundary

This phase formally accepts the existing Power BI runtime against the frozen
canonical Phase 8 baseline. It is an acceptance activity, not a build or repair
step. The acceptance used synthetic repository fixtures only; no private
operational data was introduced.

- Branch: `feature/phase8-canonical-acceptance`
- Acceptance date: 2026-08-24
- Canonical `as_of_date`: 2026-08-15
- Power BI project: `powerbi/CyberGovernanceDashboard/CyberGovernanceDashboard.pbip`
- DataRoot: `C:\dev\cyber-governance-automation-lab\data\curated`

## Canonical pipeline and regression evidence

The canonical pipeline was run from the repository root with:

```text
python src/main.py --as-of-date 2026-08-15
```

Observed output:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

All required runtime outputs existed after the run:

- `data/curated/curated_control_status.csv`
- `data/curated/data_quality_issues.csv`
- `data/curated/ai_review_queue.json`

Only the first two files are Power BI sources. The AI review queue is outside
the reporting source boundary. All three runtime outputs remain Git-ignored.

The Python regression suite completed with `53 passed`:

```text
python -m pytest -q
53 passed in 22.77s
```

## Static model and source-boundary checks

The implemented project remains aligned with the frozen semantic-model
contract:

- Reporting tables: 2 (`ControlStatus`, `DataQualityIssues`)
- Relationships: exactly 1
- Relationship: `ControlStatus[source_row_number]` (1) to
  `DataQualityIssues[source_row_number]` (*)
- Cross-filter direction: `ControlStatus` to `DataQualityIssues`
- Measures: exactly 21
- Calculated tables: 0
- Calculated columns: 0
- Power BI sources: exactly 2
  (`curated_control_status.csv`, `data_quality_issues.csv`)
- `days_overdue`, `days_late`, and `reminder_count` use `summarizeBy: none`

Power Query remains limited to source transport, blank-string-to-null handling,
and technical typing. No reporting business logic or derived Overall Status was
introduced.

## Power BI refresh and runtime counts

Power BI Desktop opened the project with exactly these three primary pages, in
this order:

1. Management Overview
2. Control Monitoring
3. Process & Data Quality

A full refresh against the canonical DataRoot completed without refresh,
query, relationship, or visual errors. Read-only DAX Query View checks did not
change the model.

| Runtime table | Observed rows | Expected rows | Result |
|---|---:|---:|---|
| ControlStatus | 15 | 15 | PASS |
| DataQualityIssues | 5 | 5 | PASS |

## Measure acceptance

All 21 measures were evaluated in the unfiltered canonical context.

| Measure | Observed | Expected | Result |
|---|---:|---:|---|
| Controls in Scope | 5 | 5 | PASS |
| Expected Submissions | 15 | 15 | PASS |
| Valid Submissions | 10 | 10 | PASS |
| Invalid Submissions | 5 | 5 | PASS |
| Assessed Submissions | 5 | 5 | PASS |
| Compliant Submissions | 4 | 4 | PASS |
| Non-Compliant Submissions | 1 | 1 | PASS |
| Assessed Compliance Rate | 80.0% | 80.0% | PASS |
| Overdue Submissions | 1 | 1 | PASS |
| Late Submissions | 1 | 1 | PASS |
| High/Critical Exceptions | 2 | 2 | PASS |
| Overdue Submission Rate | 10.0% | 10.0% | PASS |
| Total Automated Reminders | 4 | 4 | PASS |
| Active Follow-up Submissions | 4 | 4 | PASS |
| Submissions with Reminder History | 4 | 4 | PASS |
| Average Reminders per Reminded Submission | 1.00 | 1.00 | PASS |
| Total DQ Issues | 5 | 5 | PASS |
| Submissions with DQ Issues | 5 | 5 | PASS |
| DQ Issue Rate | 33.3% | 33.3% | PASS |
| High-Severity DQ Issues | 5 | 5 | PASS |
| Missing Evidence Issues | 1 | 1 | PASS |

## Zero-versus-blank semantics

The hardened semantic distinction remains intact:

- Finance in the DQ context returned `Total DQ Issues = 0` and
  `DQ Issue Rate = 0.0%`: a defined context with no matching findings is zero.
- The `Not Submitted` assessed context returned no assessed rows and
  `Assessed Compliance Rate = BLANK`: a ratio with a zero denominator remains
  undefined rather than being rendered as 0.0%.

Therefore, known zero and undefined remain distinct.

## Canonical submission scenarios

| Submission | Accepted runtime evidence | Result |
|---|---|---|
| SUB-004 | `data_quality_status = Valid`; `submission_status = In Review`; `submission_late = True`; `days_late = 2` | PASS |
| SUB-005 | `data_quality_status = Valid`; `submission_status = Non-Compliant`; `risk_level = High`; `overdue_flag = False` | PASS |
| SUB-014 | `data_quality_status = Valid`; `submission_status = Not Submitted`; `overdue_flag = True`; `days_overdue = 5`; `active_action_status = Open`; `reminder_count = 1`; `last_reminder_at = 2026-08-15` | PASS |
| SUB-015 | `control_id = CTRL-999`; `data_quality_status = Invalid`; `control_name = null`; row remains visible | PASS |

The unknown `CTRL-999` reference does not inflate the control dimension:
`Controls in Scope` remains 5.

## Data-quality scenarios

Exactly five high-severity findings were present:

| Submission | Control | Rule | Severity | Result |
|---|---|---|---|---|
| SUB-002 | CTRL-001 | DQ-004 Missing Evidence | High | PASS |
| SUB-006 | CTRL-002 | DQ-003 Invalid Status | High | PASS |
| SUB-008 | CTRL-003 | DQ-005 Duplicate Submission | High | PASS |
| SUB-009 | CTRL-003 | DQ-005 Duplicate Submission | High | PASS |
| SUB-015 | CTRL-999 | DQ-002 Unknown Control ID | High | PASS |

The accepted rule distribution is `DQ-005 = 2`, `DQ-002 = 1`, `DQ-003 = 1`,
and `DQ-004 = 1`.

## Report-page acceptance

### Management Overview

The unfiltered page showed:

- KPI cards: Controls in Scope 5; Assessed Compliance Rate 80.0%;
  Non-Compliant Submissions 1; Overdue Submissions 1; High/Critical
  Exceptions 2; Total DQ Issues 5.
- Submission status distribution: Compliant 7; Not Submitted 4; In Review 2;
  Non-Compliant 1; Pending 1; total 15.
- Assessed Compliance Rate by Business Unit: Finance 100.0%; IT Operations
  100.0%; Retail Banking 0.0%.
- High/Critical Exceptions by Risk Level: Critical 1; High 1.

The Business Unit, Risk Level, and Reporting Period slicers all changed the
page as expected and were fully reset to the canonical unfiltered state.

### Control Monitoring

The unfiltered detail table contained 15 submission rows and exactly the 15
contracted business fields: Control ID, Control Name, Business Unit, Risk
Level, Reporting Period, Submission Status, Due Date, Evidence Present,
Overdue, Days Overdue, Data Quality Status, Active Action Status, Active Action
Due Date, Reminder Count, and Last Reminder At.

The Business Unit, Risk Level, Submission Status, Data Quality Status, and
Overdue slicers were exercised and reset. Accepted filter evidence:

- Retail Banking: 3 rows
- Finance: 2 rows
- IT Operations: 9 rows
- Risk Level High: 7 rows
- Non-Compliant: exactly SUB-005 / CTRL-002
- Invalid: exactly SUB-002, SUB-006, SUB-008, SUB-009, and SUB-015
- Overdue True: exactly SUB-014 / CTRL-005, Days Overdue 5, Active Action
  Status Open, Reminder Count 1

`Pending` and `CTRL-999` remained visible in the unfiltered table.

### Process & Data Quality

The unfiltered page showed:

- Process KPIs: Total Automated Reminders 4; Active Follow-up Submissions 4;
  Submissions with Reminder History 4; Late Submissions 1; Overdue Submission
  Rate 10.0%.
- DQ KPIs: Total DQ Issues 5; DQ Issue Rate 33.3%; High-Severity DQ Issues 5.
- DQ Issues by Rule: DQ-005 2; DQ-002 1; DQ-003 1; DQ-004 1.
- DQ Issues by Severity: High 5, with no artificial Medium or Low category.
- DQ detail: 5 rows with exactly Submission ID, Control ID, Rule, Severity,
  Field, and Message.

## Cross-table filter propagation

A temporary page filter on `ControlStatus[business_unit]` verified propagation
from the submission-grain table to the DQ issue-grain table.

| Business Unit | Process KPIs (reminders / active / history / late / overdue rate) | DQ KPIs (issues / rate / high) | DQ detail | Result |
|---|---|---|---|---|
| Retail Banking | 2 / 2 / 2 / 1 / 0.0% | 1 / 33.3% / 1 | SUB-006 / DQ-003 | PASS |
| Finance | 0 / 0 / 0 / 0 / 0.0% | 0 / 0.0% / 0 | empty | PASS |
| IT Operations | 2 / 2 / 2 / 1 / 16.7% | 3 / 33.3% / 3 | SUB-002, SUB-008, SUB-009 | PASS |

The temporary page filter was then removed completely. The page returned to
the unfiltered canonical 4 / 4 / 4 / 1 / 10.0% process state and 5 / 33.3% / 5
DQ state.

## Null, unknown, grain, and multiplication checks

The canonical runtime contains no null values in `overdue_flag`,
`submission_late`, `days_overdue`, or `days_late`. Consequently, this fixture
cannot provide a direct runtime null example for those four columns. This is a
documented test limitation; no synthetic null case was invented.

The structural null contract was verified: Power Query converts blank strings
to null before technical typing, performs no false/zero coercion, and the DAX
count-zero behavior does not rewrite source nulls. The actual unknown-control
case remains represented by SUB-015 with a null control name.

The relationship does not materialize a join or multiply submission rows.
`ControlStatus` remains at its 15-row submission grain while
`DataQualityIssues` remains at its 5-row issue grain. `source_row_number` is
unique in `ControlStatus`; all five issue rows have a valid relationship key.

## Power BI side effects and repository review

Power BI was closed without saving after all temporary slicers and page filters
had been reset or removed. No tracked PBIR, TMDL, Power Query, source, test, or
fixture file changed. In particular, `de-DE.tmdl` had no diff, so no targeted
revert was required. Power BI's `.pbi/cache.abf` and `.pbi/localSettings.json`
and the freshly generated curated outputs remain ignored and unstaged.

The only regular repository change produced by this phase is this acceptance
document. No file was staged, committed, pushed, merged, or submitted as a pull
request.

## Limitations and definition of done

- The current fixture does not contain a null case for the four nullable timing columns
  listed above; only the structural null-preservation path can be
  accepted for them.
- The acceptance proves the canonical synthetic runtime and the implemented
  report behavior. It does not constitute acceptance of private operational
  data or publication evidence.

All mandatory Phase 8.9 checks passed: canonical generation, regression tests,
source boundary, refresh, model invariants, runtime counts, all measures,
zero-versus-blank behavior, submission and DQ scenarios, all three report
pages, slicers, cross-table propagation, null/unknown semantics, grain
preservation, and repository cleanliness.

Formal operational Phase 7 output acceptance remains Phase 8.10.

Public screenshots / final presentation evidence remain Phase 8.11.

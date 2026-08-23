# Phase 8.1 — Canonical Curated Reporting Baseline

## Status

**PHASE 8.1 COMPLETE — CANONICAL REPORTING BASELINE FIXED AND VERIFIED**

Phase 8.1 establishes the deterministic canonical reporting baseline that the later Power BI semantic model and dashboard must reproduce. It does not create a Power BI artifact, add DAX, change Python business rules, or modify canonical source fixtures.

The baseline is evaluated at:

```text
as_of_date = 2026-08-15
```

and is produced by the existing canonical Python execution path:

```bash
python src/main.py --as-of-date 2026-08-15
```

Generated runtime outputs remain under `data/curated/` and are intentionally not committed. The repository records the baseline contract and automated acceptance evidence instead.

## 1. Purpose

Phase 8.0 froze the Power BI reporting semantics before any report was built. Phase 8.1 now fixes the exact deterministic dataset state that Phase 8 will use as its first implementation and acceptance target.

The dependency chain remains:

```text
canonical Control / Submission / Action fixtures
        ↓
existing Python pipeline
        ↓
curated_control_status.csv
        +
data_quality_issues.csv
        ↓
Phase 8 Power BI
```

Power BI must later reproduce this baseline without redefining upstream semantics.

## 2. Canonical Inputs

The canonical source set remains unchanged:

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

Canonical source inventory:

```text
Controls:    5
Submissions: 15
Actions:     5
```

These files remain synthetic deterministic fixtures and are not replaced by operational Microsoft 365 data.

## 3. Canonical CLI Acceptance

The existing black-box test `test_canonical_cli_end_to_end_acceptance` executes the canonical CLI with:

```text
--as-of-date 2026-08-15
```

and requires the following successful run summary:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

The same test requires all three contractual runtime outputs to exist:

```text
curated_control_status.csv
data_quality_issues.csv
ai_review_queue.json
```

For Phase 8, only the first two are reporting sources. `ai_review_queue.json` remains downstream input for the later controlled AI phase.

## 4. Curated Reporting Grain Acceptance

`curated_control_status.csv` must contain:

```text
15 rows
```

for:

```text
15 raw Submission rows
```

Therefore:

```text
raw Submission rows = curated ControlStatus rows = 15
```

No Submission row may be removed because of invalid Data Quality, unresolved Control reference, duplicate business key, or Action enrichment.

Action aggregation must not multiply Submission grain.

## 5. Data Quality Baseline

The canonical output contains exactly five Data Quality Issue rows:

| Submission | Rule | Meaning |
| --- | --- | --- |
| `SUB-002` | `DQ-004 Missing Evidence` | reviewed/final state without required evidence reference |
| `SUB-006` | `DQ-003 Invalid Status` | synthetic invalid Submission status |
| `SUB-008` | `DQ-005 Duplicate Submission` | first row in duplicate business-key pair |
| `SUB-009` | `DQ-005 Duplicate Submission` | second row in duplicate business-key pair |
| `SUB-015` | `DQ-002 Unknown Control ID` | unresolved Control reference |

Canonical classification:

```text
Valid Submissions   = 10
Invalid Submissions = 5
Total DQ Issues     = 5
```

All five canonical DQ findings are High severity under the current fixture set.

## 6. Known Curated Scenario Acceptance

The canonical baseline preserves the following targeted scenarios.

### `SUB-004` — valid late Submission

```text
data_quality_status = Valid
submission_status   = In Review
submission_late     = True
days_late           = 2
```

This proves:

```text
late != invalid
```

and:

```text
timeliness != compliance != Data Quality
```

### `SUB-005` — valid Non-Compliant governance outcome

```text
data_quality_status = Valid
submission_status   = Non-Compliant
risk_level          = High
overdue_flag        = False
```

This proves:

```text
Non-Compliant != Data Quality error
```

### `SUB-014` — valid overdue missing Submission

```text
data_quality_status   = Valid
submission_status     = Not Submitted
overdue_flag          = True
days_overdue          = 5
active_action_status  = Open
reminder_count        = 1
last_reminder_at      = 2026-08-15
```

This proves that the canonical reporting baseline already contains process-follow-up state at Submission grain.

### `SUB-015` — unresolved Control reference remains visible

```text
submission_id        = SUB-015
control_id           = CTRL-999
data_quality_status  = Invalid
control_name         = empty
```

The row remains present in curated output even though Control enrichment cannot resolve.

This is the reason `Controls in Scope` must count only resolved Controls rather than blindly distinct-counting every `control_id` value.

## 7. Phase 8 KPI Baseline

Using the Phase 8.0 KPI definitions against the canonical accepted output yields the following expected values.

### Governance

| KPI | Canonical value |
| --- | ---: |
| Controls in Scope | 5 |
| Expected Submissions | 15 |
| Valid Submissions | 10 |
| Invalid Submissions | 5 |
| Assessed Submissions | 5 |
| Compliant Submissions | 4 |
| Non-Compliant Submissions | 1 |
| Assessed Compliance Rate | 80% |

`Assessed Compliance Rate` is:

```text
4 Compliant
/
5 Assessed
=
80%
```

It is not a distinct-Control compliance ratio.

### Timeliness and Exceptions

| KPI | Canonical value |
| --- | ---: |
| Overdue Submissions | 1 |
| Late Submissions | 1 |
| High/Critical Exceptions | 2 |
| Overdue Submission Rate | 10% |

The two High/Critical exceptions are the valid canonical rows:

```text
SUB-005 → High risk + Non-Compliant
SUB-014 → Critical risk + Overdue
```

The overdue rate is:

```text
1 overdue valid Submission
/
10 valid Submissions
=
10%
```

### Data Quality

| KPI | Canonical value |
| --- | ---: |
| Total DQ Issues | 5 |
| Submissions with DQ Issues | 5 |
| DQ Issue Rate | 33.33% |
| High-Severity DQ Issues | 5 |
| Missing Evidence Issues | 1 |

The DQ issue rate is:

```text
5 source rows with DQ issues
/
15 expected Submission rows
=
33.33%
```

### Follow-up and Process Impact

Canonical Action reminder counts are:

```text
ACT-001 = 1
ACT-002 = 1
ACT-003 = 1
ACT-004 = 1
ACT-005 = 0
```

After Python aggregation at Submission grain, the expected Phase 8 process measures are:

| KPI | Canonical value |
| --- | ---: |
| Total Automated Reminders | 4 |
| Active Follow-up Submissions | 4 |
| Submissions with Reminder History | 4 |
| Average Reminders per Reminded Submission | 1.00 |

`Active Follow-up Submissions` reflects stored active Action state only and must not be presented as a perfect inference of current business need because automatic Action completion after later evidence intake is not implemented in the PoC.

## 8. Power BI Source Baseline

Phase 8 must later load exactly:

```text
ControlStatus
← curated_control_status.csv

DataQualityIssues
← data_quality_issues.csv
```

Expected canonical model counts before any report filtering:

```text
ControlStatus rows     = 15
DataQualityIssues rows = 5
```

The required relationship remains:

```text
ControlStatus[source_row_number]
          1
          │
          *
DataQualityIssues[source_row_number]
```

Joining DQ Issues must not multiply `ControlStatus` rows.

## 9. Generated Output Version-Control Boundary

Phase 8.1 does not commit generated files from:

```text
data/curated/
```

because the repository already treats them as reproducible runtime artifacts.

The permanent public evidence for this work package is:

```text
docs/phase8_canonical_baseline.md
```

plus the existing automated tests that recreate and inspect the canonical outputs in temporary test directories.

This avoids turning generated snapshots into a second source of truth.

## 10. Regression Evidence

The canonical CLI end-to-end test protects:

- exact source counts,
- successful process exit,
- exact three-file output creation,
- exact curated schema,
- 15-row Submission-grain preservation,
- 10 Valid / 5 Invalid classification,
- `SUB-004` late timing result,
- `SUB-014` overdue timing result,
- unresolved `SUB-015` Control enrichment,
- exact five DQ findings,
- exact canonical AI queue membership.

Additional transformation tests independently protect:

- Action aggregation without Submission-row multiplication,
- overdue equality boundary,
- late equality boundary,
- non-evaluable timing remaining unknown rather than forced false/zero.

Phase 8.1 adds no new production code because the existing deterministic acceptance already covers the reporting baseline required by Power BI.

## 11. Scope Boundaries

Phase 8.1 does not implement:

```text
Power BI project files
Power Query
DAX measures
report visuals
Power BI Service publication
operational snapshot acceptance in Power BI
new Python business rules
new DQ rules
new Action fields
new canonical fixtures
committed curated runtime snapshots
Phase 9 AI runtime
Phase 10 API
```

Those remain later work packages.

## 12. Definition of Done

Phase 8.1 is complete because:

- [x] the canonical source set remains fixed at 5 Controls / 15 Submissions / 5 Actions,
- [x] the canonical evaluation date remains `2026-08-15`,
- [x] the canonical CLI acceptance result is fixed at `5 / 15 / 5 / 5 / 10 / 5 / 2`,
- [x] the two Phase 8 reporting outputs are identified,
- [x] `ControlStatus` row count is fixed at 15,
- [x] Data Quality Issue row count is fixed at 5,
- [x] 10 Valid / 5 Invalid Submission classification is fixed,
- [x] known late, Non-Compliant, overdue, duplicate, missing-evidence, and unknown-Control scenarios are fixed,
- [x] unresolved `CTRL-999` is excluded from the `Controls in Scope` semantic,
- [x] expected Phase 8 governance KPI values are derived,
- [x] expected timeliness/exception KPI values are derived,
- [x] expected DQ KPI values are derived,
- [x] expected reminder/process KPI values are derived,
- [x] generated `data/curated/` outputs remain runtime artifacts rather than committed source data,
- [x] existing automated tests provide executable regression protection for the canonical baseline,
- [x] no Phase 8.2+ Power BI implementation or later-phase functionality is pulled forward.

**Phase 8.1 status: COMPLETE**

## 13. Next Work Package

The next step is Phase 8.2:

```text
create the source-controlled Power BI project artifact
without changing the frozen Phase 8.0 semantics or Phase 8.1 canonical baseline
```

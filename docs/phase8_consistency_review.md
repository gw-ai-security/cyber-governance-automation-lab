# Phase 8 — Consistency Review Before Control Monitoring

## Status

**PHASE 8.0–8.6 REVIEWED — CORE ARCHITECTURE VALID; CONSISTENCY HARDENING APPLIED**

This review was performed after Phase 8.6 and before Phase 8.7. It cross-checks the frozen Phase 8 reporting contract, canonical baseline, PBIP/PBIR/TMDL project, Power Query ingestion, semantic relationship, DAX measures, Management Overview, Git/privacy boundary, and current-state documentation.

The review does **not** change the canonical source fixtures or any Python-owned business rule.

## 1. Reviewed Scope

The following Phase 8 work packages were reviewed as one dependency chain:

```text
8.0 reporting/KPI contract
  ↓
8.1 canonical reporting baseline
  ↓
8.2 PBIP/PBIR/TMDL scaffold
  ↓
8.3 curated loading and typing
  ↓
8.4 semantic relationship
  ↓
8.5 semantic measures
  ↓
8.6 Management Overview
```

## 2. Confirmed Correct

The following design decisions remain correct and unchanged:

- Power BI consumes exactly `curated_control_status.csv` and `data_quality_issues.csv`.
- Power BI does not directly consume operational Excel, raw Phase 7 snapshots, canonical raw inputs, or `ai_review_queue.json`.
- `ControlStatus` remains one row per raw Submission source row.
- `DataQualityIssues` remains one row per triggered DQ rule per source row.
- the model contains exactly two reporting tables,
- the single active relationship uses `source_row_number`, not `submission_id`,
- effective filter propagation remains `ControlStatus → DataQualityIssues`,
- both technical relationship keys remain hidden from report consumers,
- empty CSV strings are normalized to null before technical typing,
- non-evaluable timing state remains null rather than being rewritten to false/zero,
- automatic time intelligence remains disabled,
- no calculated table or calculated column has been introduced,
- the semantic layer still contains the same 21 contracted measures,
- canonical Phase 8.1 acceptance values remain unchanged,
- the Management Overview uses the required three slicers, six KPI cards, and three analytical views,
- no synthetic `Overall Status` has been introduced,
- generated curated data and machine-local Power BI cache/state remain outside Git.

## 3. Corrections Applied

### 3.1 Aggregate zero-result semantics

Power BI count/distinct-count/sum expressions can return blank for an empty result set. A blank is appropriate for an undefined rate denominator, but it is not the best representation for a known count of zero.

The aggregate measure layer is therefore standardized so count/sum measures return an explicit `0` when the current filter context contains no matching rows.

This applies to count/sum semantics such as:

```text
Controls in Scope
Expected Submissions
Valid Submissions
Invalid Submissions
Assessed Submissions
Compliant Submissions
Non-Compliant Submissions
Overdue Submissions
Late Submissions
High/Critical Exceptions
Total Automated Reminders
Active Follow-up Submissions
Submissions with Reminder History
Total DQ Issues
Submissions with DQ Issues
```

Ratio/average measures continue to preserve `BLANK()` when their denominator is zero:

```text
Assessed Compliance Rate
Overdue Submission Rate
DQ Issue Rate
Average Reminders per Reminded Submission
```

This preserves the distinction:

```text
known count = 0
undefined ratio = blank
```

No nullable source attribute is coerced to false or zero.

### 3.2 Data Quality rate zero behavior

`Submissions with DQ Issues` now returns `0` rather than blank when a valid filter context contains no DQ issue rows. Therefore:

```text
expected submissions > 0
and DQ affected submissions = 0
→ DQ Issue Rate = 0.0%
```

If there are no expected submissions at all, the denominator remains zero and `DQ Issue Rate` remains blank.

### 3.3 Row-detail numeric summarization

The following Submission-grain fields are attributes in the Phase 8.7 detail view, not additive report facts:

```text
days_overdue
days_late
reminder_count
```

Their semantic-model default summarization is therefore set to:

```text
summarizeBy: none
```

This prevents Power BI from offering misleading default labels such as `Sum of Days Overdue` in the Control Monitoring detail table. Aggregate reminder reporting continues to use the explicit `[Total Automated Reminders]` measure.

## 4. Management Overview Review

Phase 8.6 remains valid after the consistency hardening.

Canonical unfiltered smoke-test values remain:

```text
Controls in Scope              5
Assessed Compliance Rate       80.0%
Non-Compliant Submissions      1
Overdue Submissions            1
High/Critical Exceptions       2
Total DQ Issues                5
```

The three analytical views remain contract-aligned:

```text
Submission Status Distribution
Assessed Compliance Rate by Business Unit
High/Critical Exceptions by Risk Level
```

The Business Unit and Risk Level slicers may suppress unresolved blank enrichment values from their selectable management lists without deleting the underlying invalid source row from the model.

## 5. Canonical Baseline Unchanged

The consistency review does not change the frozen canonical acceptance baseline:

```text
as_of_date = 2026-08-15
Controls loaded = 5
Submissions loaded = 15
Actions loaded = 5
DQ issues = 5
Valid submissions = 10
Invalid submissions = 5
AI review queue items = 2
```

Nor does it change the expected reporting values:

```text
ControlStatus rows = 15
DataQualityIssues rows = 5
Controls in Scope = 5
Expected Submissions = 15
Assessed Compliance Rate = 80.0%
Overdue Submissions = 1
High/Critical Exceptions = 2
Total DQ Issues = 5
DQ Issue Rate = 33.3%
Total Automated Reminders = 4
```

## 6. Documentation Consistency

Current-state documentation is updated to reflect that Phase 8.6 is complete and Phase 8.7 is next.

Historical phase documents remain valid for the state they accepted. Where a later Phase 8 work package hardened an existing measure representation without changing its business definition, the later acceptance evidence and current TMDL define the current implementation.

## 7. Remaining Phase 8 Work

```text
Phase 8.7  Control Monitoring
Phase 8.8  Process & Data Quality
Phase 8.9  Canonical Power BI acceptance
Phase 8.10 Operational Phase 7 output acceptance
Phase 8.11 Documentation, screenshots, regression and final acceptance
```

Phase 8 remains in progress.

## 8. Definition of Done

This consistency review is complete when:

- [x] Phase 8.0–8.6 contracts and implementation are cross-checked,
- [x] source and grain boundaries remain unchanged,
- [x] relationship key/direction remain unchanged,
- [x] canonical fixture values remain unchanged,
- [x] count/sum measures use explicit zero-result semantics,
- [x] undefined rates/averages still preserve blank denominators,
- [x] DQ Issue Rate can represent a known 0%,
- [x] row-detail numeric fields default to `Do not summarize`,
- [x] no upstream Python business rule is duplicated in Power BI,
- [x] no new data source, table, relationship, calculated table, or calculated column is introduced,
- [x] current-state documentation reflects Phase 8.6 completion,
- [x] regression CI is green on the review pull request.

## 9. Next Work Package

After this review is merged and Power BI Desktop is reopened against the updated TMDL, Phase 8.7 builds the **Control Monitoring** page using the existing curated model and the frozen Submission-grain detail contract.

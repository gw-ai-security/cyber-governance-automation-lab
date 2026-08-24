# Phase 8.8 — Process & Data Quality

## Status

**PHASE 8.8 COMPLETE — THIRD PRIMARY POWER BI REPORT PAGE IMPLEMENTED**

Phase 8.8 implements the third contracted Power BI page, `Process & Data Quality`, on the existing source-controlled PBIP/PBIR/TMDL project.

The page remains a reporting consumer of the frozen Phase 8 semantic model. It introduces no new data source, Power Query business rule, relationship, calculated table, calculated column, DAX measure, or composite `Overall Status`.

Formal canonical runtime acceptance remains Phase 8.9. Operational Phase 7 output acceptance remains Phase 8.10.

## 1. Purpose

The page provides one analytical workspace while preserving the semantic distinction between:

```text
Data Quality
!=
operational follow-up
!=
timeliness
!=
compliance
```

Data Quality is shown from `DataQualityIssues` at DQ-Issue grain. Process/follow-up KPIs consume existing Submission-grain measures from `ControlStatus`.

## 2. Page Identity

```text
Display name: Process & Data Quality
PBIR page ID: c7d8e9f0a1b2c3d4e5f6
Display mode: FitToPage
Canvas: 1280 × 720
```

The report page order is:

```text
1. Management Overview
2. Control Monitoring
3. Process & Data Quality
```

## 3. Visual Contract

The page contains exactly 14 visual definitions:

```text
3 text boxes
8 KPI cards
2 analytical charts
1 DQ detail table
--------------------
14 visuals
```

No slicer is added because the frozen Phase 8.0 page contract does not require primary slicers for Page 3.

The three text boxes are presentation-only labels:

```text
Cyber Governance — Process & Data Quality
Process & Follow-up
Data Quality
```

## 4. Process & Follow-up Section

The section uses exactly five existing `ControlStatus` measures:

```text
Total Automated Reminders
Active Follow-up Submissions
Submissions with Reminder History
Late Submissions
Overdue Submission Rate
```

Canonical unfiltered values:

| Measure | Expected |
| --- | ---: |
| Total Automated Reminders | 4 |
| Active Follow-up Submissions | 4 |
| Submissions with Reminder History | 4 |
| Late Submissions | 1 |
| Overdue Submission Rate | 10.0% |

The page does not reinterpret these measures. In particular:

```text
Active Follow-up
!= Reminder History
!= Late
!= Overdue
!= Compliance
```

`Active Follow-up Submissions` remains a current stored active-Action projection, not a historical `ever had an Action` KPI.

## 5. Data Quality KPI Section

The section uses exactly three existing `DataQualityIssues` measures:

```text
Total DQ Issues
DQ Issue Rate
High-Severity DQ Issues
```

Canonical unfiltered values:

| Measure | Expected |
| --- | ---: |
| Total DQ Issues | 5 |
| DQ Issue Rate | 33.3% |
| High-Severity DQ Issues | 5 |

No new DQ rule or severity category is inferred in Power BI.

## 6. DQ Issues by Rule

Visual type:

```text
Clustered Bar Chart
```

Binding:

```text
Category: DataQualityIssues[rule]
Value:    [Total DQ Issues]
```

Data labels are enabled. Technical axis titles are disabled.

Canonical distribution:

```text
DQ-005 Duplicate Submission    2
DQ-002 Unknown Control ID      1
DQ-003 Invalid Status          1
DQ-004 Missing Evidence        1
```

No missing rule category is manufactured to make the chart look complete.

## 7. DQ Issues by Severity

Visual type:

```text
Clustered Column Chart
```

Binding:

```text
Category: DataQualityIssues[severity]
Value:    [Total DQ Issues]
```

Data labels are enabled. Technical axis titles are disabled.

Canonical distribution:

```text
High    5
```

The current canonical fixture contains no Medium or Low DQ issue. Those categories are therefore not synthesized with zero values.

## 8. DQ Detail Table

The detail table remains at DQ-Issue grain and contains exactly six physical `DataQualityIssues` fields:

```text
submission_id → Submission ID
control_id    → Control ID
rule          → Rule
severity      → Severity
field         → Field
message       → Message
```

Business-friendly names are PBIR visual `displayName` metadata only. The semantic-model and source field names remain unchanged.

Canonical unfiltered row count:

```text
5 DQ Issue rows
```

Canonical affected Submission rows visible in the table:

```text
SUB-002
SUB-006
SUB-008
SUB-009
SUB-015
```

## 9. Runtime Smoke Tests

The page was checked in Power BI Desktop against the canonical reporting dataset before commit.

### Unfiltered

```text
Total DQ Issues                    5
DQ Issue Rate                   33.3%
High-Severity DQ Issues            5

Total Automated Reminders          4
Active Follow-up Submissions       4
Submissions with Reminder History  4
Late Submissions                   1
Overdue Submission Rate         10.0%

DQ detail rows                      5
```

### Retail Banking temporary page-filter check

```text
Process:
Total Automated Reminders          2
Active Follow-up Submissions       2
Submissions with Reminder History  2
Late Submissions                   1
Overdue Submission Rate          0.0%

Data Quality:
Total DQ Issues                    1
DQ Issue Rate                   33.3%
High-Severity DQ Issues            1
DQ detail: SUB-006 / DQ-003
```

### Finance temporary page-filter check

```text
Process count KPIs                 0
Overdue Submission Rate          0.0%
Data Quality count KPIs            0
DQ Issue Rate                    0.0%
DQ detail rows                      0
```

### IT Operations temporary page-filter check

```text
Process:
Total Automated Reminders          2
Active Follow-up Submissions       2
Submissions with Reminder History  2
Late Submissions                   1
Overdue Submission Rate         16.7%

Data Quality:
Total DQ Issues                    3
DQ Issue Rate                   33.3%
High-Severity DQ Issues            3
DQ detail: SUB-002 / SUB-008 / SUB-009
```

These checks confirm the existing single-direction relationship propagates `ControlStatus` filter context to `DataQualityIssues` without introducing bidirectional filtering.

Temporary validation filters were removed before the report was saved for source control.

## 10. Visual QA

The initial authoring layout truncated several Process KPI labels. Before commit, card widths and layout were adjusted so all five Process labels are fully readable:

```text
Total Automated Reminders
Active Follow-up Submissions
Submissions with Reminder History
Late Submissions
Overdue Submission Rate
```

The Data Quality KPI labels, both analytical charts, and all six DQ detail columns remain readable on the 1280 × 720 page.

## 11. Semantic-Model Boundary

Phase 8.8 does not change the semantic model.

The following invariants remain:

```text
Reporting tables:       2
Active relationships:   1
Measures:              21
Calculated tables:      0
Calculated columns:     0
CSV reporting sources:  2
```

Relationship:

```text
ControlStatus[source_row_number]
          1
          │
          *
DataQualityIssues[source_row_number]

Filter direction: ControlStatus → DataQualityIssues
```

No TMDL change is part of the implementation commit.

The row-detail numeric attributes remain:

```text
days_overdue     summarizeBy: none
days_late        summarizeBy: none
reminder_count   summarizeBy: none
```

## 12. Power BI Desktop Side-Effect Handling

Power BI Desktop regenerated linguistic metadata in:

```text
CyberGovernanceDashboard.SemanticModel/definition/cultures/de-DE.tmdl
```

This was an unrelated authoring side effect and was explicitly reverted before commit.

No SemanticModel/TMDL file is included in the Phase 8.8 report implementation commit.

## 13. Validation

Local validation reported:

```text
python -m pytest -q
53 passed

git diff --check
PASS
```

The Python suite validates repository regression behavior; it does not replace PBIR inspection or Power BI Desktop runtime smoke testing.

## 14. Scope Exclusions

Phase 8.8 does not:

- add primary slicers to Page 3,
- add or redefine DAX measures,
- add a new relationship,
- enable bidirectional filtering,
- add calculated tables or calculated columns,
- add a new data source,
- add Power Query business logic,
- modify canonical fixtures,
- remove DQ-invalid records,
- invent Medium/Low DQ categories when no current issue rows exist,
- combine DQ/process/compliance into an `Overall Status`,
- claim historical Action coverage not exposed by the curated schema,
- claim ROI or time saved,
- perform formal Phase 8.9 canonical acceptance,
- perform Phase 8.10 operational Phase 7 output acceptance.

## 15. Definition of Done

Phase 8.8 is complete when:

- [x] `Process & Data Quality` is the third report page,
- [x] the page contains exactly 14 visual definitions,
- [x] 5 contracted Process KPI cards use existing measures,
- [x] 3 contracted DQ KPI cards use existing measures,
- [x] `DQ Issues by Rule` uses DQ rule + Total DQ Issues,
- [x] `DQ Issues by Severity` uses DQ severity + Total DQ Issues,
- [x] DQ detail table contains exactly 6 contracted fields at DQ-Issue grain,
- [x] no primary slicer is added,
- [x] canonical unfiltered values match the frozen baseline,
- [x] Business Unit runtime smoke tests confirm relationship propagation,
- [x] no TMDL or Power Query change is included,
- [x] all KPI labels are readable,
- [x] the model remains exactly 2 tables / 1 active relationship / 21 measures,
- [x] no `Overall Status` is introduced,
- [x] regression tests remain green.

## 16. Next Work Package

Phase 8.9 performs formal canonical Power BI acceptance across all three report pages and the frozen semantic contract.

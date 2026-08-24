# Phase 8.7 — Power BI Control Monitoring

## Status

**PHASE 8.7 IMPLEMENTED — CONTROL MONITORING PAGE BUILT AND SMOKE-TESTED**

Phase 8.7 implements the second report page of the source-controlled Power BI project. It uses the existing `ControlStatus` submission-grain reporting table and preserves the Phase 8 semantic-model boundary established in Phases 8.0–8.6.

The work package deliberately stops before the Process & Data Quality page, formal canonical Power BI acceptance, operational Phase 7 output acceptance, or Power BI Service publication.

## 1. Purpose

The Control Monitoring page provides an operational governance view that shows where review or follow-up is required at Submission grain.

It does not introduce a synthetic overall status or reimplement Python-owned business rules.

## 2. Source-Controlled Report Artifact

The page is stored in PBIR under:

```text
powerbi/CyberGovernanceDashboard/
└── CyberGovernanceDashboard.Report/
    └── definition/
        └── pages/
            └── 97e8a6263b77b0b46aec/
                ├── page.json
                └── visuals/
```

Page display name:

```text
Control Monitoring
```

Canvas:

```text
1280 × 720
FitToPage
```

The page contains exactly seven source-controlled visual definitions:

```text
1 page title
5 slicers
1 detail table
----------------
7 visuals
```

## 3. Page Header

Visible title:

```text
Cyber Governance — Control Monitoring
```

The title is presentation metadata only.

## 4. Primary Slicers

All slicers use `ControlStatus` fields and therefore operate at the existing Submission reporting grain.

| Slicer | Field | Style | Notes |
| --- | --- | --- | --- |
| Business Unit | `ControlStatus[business_unit]` | Dropdown | unresolved blank enrichment omitted from selectable list |
| Risk Level | `ControlStatus[risk_level]` | Dropdown | unresolved blank enrichment omitted from selectable list |
| Submission Status | `ControlStatus[submission_status]` | Dropdown | source values remain available, including canonical `Pending` |
| Data Quality Status | `ControlStatus[data_quality_status]` | Dropdown | no extra business classification |
| Overdue | `ControlStatus[overdue_flag]` | Dropdown | Boolean source semantics preserved |

The Business Unit and Risk Level slicer presentation does not delete unresolved/DQ-invalid source rows from the model or detail table.

## 5. Submission-Grain Detail Table

The page contains one large `tableEx` visual using exactly these fields, in this order:

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

Physical bindings remain the existing `ControlStatus` columns:

```text
control_id
control_name
business_unit
risk_level
reporting_period
submission_status
due_date
evidence_present
overdue_flag
days_overdue
data_quality_status
active_action_status
active_action_due_date
reminder_count
last_reminder_at
```

Business-friendly labels are implemented only through PBIR visual `displayName` metadata. Source and semantic-model field names are unchanged.

The table remains one row per Submission source row. It does not aggregate raw Actions or DQ issues.

## 6. Numeric Detail Semantics

The consistency review before Phase 8.7 established these detail attributes as non-additive by default:

```text
days_overdue
days_late
reminder_count
```

The current TMDL keeps:

```text
summarizeBy: none
```

for all three fields. The Phase 8.7 report commit introduces no semantic-model/TMDL change.

Aggregate reminder reporting remains owned by explicit DAX measures such as `[Total Automated Reminders]`, not by implicit table aggregation.

## 7. Runtime Smoke-Test Evidence

The page was exercised in Power BI Desktop before the report-only commit.

### Unfiltered

Observed:

```text
15 Submission rows
```

This matches the frozen canonical `ControlStatus` row count.

### Business Unit slices

Observed:

```text
Retail Banking  3 rows
Finance         2 rows
IT Operations   9 rows
```

The unresolved canonical `CTRL-999` row remains outside resolved Business Unit enrichment but remains present in the unfiltered detail population and DQ-invalid view.

### Submission Status = Non-Compliant

Observed one canonical row corresponding to:

```text
SUB-005 / CTRL-002
Data Quality Status = Valid
Overdue = False
Active Action Status = In Progress
Reminder Count = 1
```

### Data Quality Status = Invalid

Observed five canonical source rows:

```text
SUB-002
SUB-006
SUB-008
SUB-009
SUB-015
```

`SUB-006` retains source status `Pending`; unresolved `SUB-015 / CTRL-999` remains visible.

### Overdue = True

Observed one canonical row corresponding to:

```text
SUB-014 / CTRL-005
Reporting Period = 2026-07
Submission Status = Not Submitted
Days Overdue = 5
Active Action Status = Open
Reminder Count = 1
```

These checks are Phase 8.7 implementation smoke tests. Formal canonical Power BI acceptance remains Phase 8.9.

## 8. Null / Unknown Boundary

The current canonical fixture contains no null `overdue_flag` value, so a runtime slicer example for blank/unknown Overdue could not be demonstrated with this fixture.

The implementation does not add any `False` coercion. The existing ingestion contract still normalizes empty CSV strings to `null` before Boolean typing, so non-evaluable/unknown state remains governed by the existing Phase 8 type/null contract.

This is not treated as formal null-behavior acceptance; formal acceptance remains in the later acceptance work packages.

## 9. Preserved Semantic Boundaries

Phase 8.7 preserves:

```text
Evidence Present != Compliant
Not Submitted != Non-Compliant
Non-Compliant != Overdue
Compliance != Timeliness
Compliance != Data Quality
Submission Status != Action Status
Unknown != False
Not Evaluated != Failed
Action completion != Submission compliance
Control risk != DQ severity
```

No `Overall Status`, traffic-light composite, or new DAX status calculation is introduced.

## 10. Repository / Model Review

The Phase 8.7 report commit contains only:

```text
pages/pages.json
Control Monitoring page.json
7 Control Monitoring visual.json files
```

The branch comparison against `main` contains no TMDL, Power Query, Python, canonical data, or generated reporting-output change.

The existing model therefore remains:

```text
Reporting tables      2
Active relationships  1
DAX measures         21
Calculated tables     0
Calculated columns    0
```

Power BI Desktop temporarily generated linguistic culture/synonym metadata during authoring. That unrelated side effect was excluded from the Phase 8.7 report commit and is not part of the repository implementation.

## 11. Regression Evidence

Local regression reported before push:

```text
python -m pytest -q
53 passed
```

`git diff --check` and the staged diff check also completed without whitespace errors.

GitHub CI evidence is recorded on the Phase 8.7 pull request before merge.

## 12. Scope Exclusions

Phase 8.7 does not:

- add a data source,
- change Power Query ingestion,
- add a semantic-model table,
- add a calculated table or calculated column,
- add or change a relationship,
- introduce bidirectional filtering,
- add or redefine a DAX measure,
- remove DQ-invalid source rows,
- infer lifecycle repair,
- implement the Process & Data Quality page,
- perform formal Phase 8.9 canonical acceptance,
- perform operational Phase 8.10 acceptance,
- publish to Power BI Service.

## 13. Definition of Done

Phase 8.7 is complete when:

- [x] the `Control Monitoring` page exists,
- [x] the page title is present,
- [x] Business Unit, Risk Level, Submission Status, Data Quality Status, and Overdue slicers exist,
- [x] the detail table contains the 15 contracted fields,
- [x] detail fields remain at Submission grain,
- [x] `Pending` and DQ-invalid rows remain reportable,
- [x] `days_overdue` and `reminder_count` are not implicitly summed,
- [x] no `Overall Status` is introduced,
- [x] no new data source, table, relationship, calculated table/column, or Power Query business rule is introduced,
- [x] PBIR definitions are source-controlled,
- [x] local implementation smoke tests were performed,
- [ ] GitHub regression CI is green on the Phase 8.7 pull request,
- [ ] Phase 8 tracking is updated after merge.

## 14. Next Work Package

After Phase 8.7 merge and acceptance tracking, Phase 8.8 builds the **Process & Data Quality** page using the existing two-table model and contracted measures.

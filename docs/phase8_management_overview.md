# Phase 8.6 — Power BI Management Overview

## Status

**PHASE 8.6 COMPLETE — MANAGEMENT OVERVIEW IMPLEMENTED AND SMOKE-TESTED**

Phase 8.6 implements the first report page of the source-controlled Power BI project. It uses only the curated reporting tables and contracted DAX measures established in Phases 8.3–8.5.

The work package deliberately stops before the Control Monitoring page, Process & Data Quality page, formal canonical Power BI acceptance, operational Phase 7 output acceptance, or Power BI Service publication.

## 1. Purpose

The Management Overview provides a compact governance summary for management-level review without collapsing distinct governance concepts into a synthetic overall status.

Dependency sequence:

```text
Phase 8.0 — reporting/KPI contract
        ↓
Phase 8.1 — canonical reporting baseline
        ↓
Phase 8.2 — PBIP/PBIR/TMDL scaffold
        ↓
Phase 8.3 — curated source loading and typing
        ↓
Phase 8.4 — semantic relationship
        ↓
Phase 8.5 — contracted DAX measures
        ↓
Phase 8.6 — Management Overview
```

## 2. Source-Controlled Report Artifact

The page is stored in PBIR under:

```text
powerbi/CyberGovernanceDashboard/
└── CyberGovernanceDashboard.Report/
    └── definition/
        └── pages/
            └── a9b0aa28ceebaf765cce/
                ├── page.json
                └── visuals/
```

The original page display name `Seite 1` is renamed to:

```text
Management Overview
```

Canvas size remains:

```text
1280 × 720
```

The page contains exactly 13 source-controlled visual definitions:

```text
1 page title
3 slicers
6 KPI cards
3 analytical charts
-------------------
13 visuals
```

## 3. Page Header

Visible title:

```text
Cyber Governance — Management Overview
```

The title is presentation metadata only. It does not introduce business logic.

## 4. Management Slicers

All primary slicers use fields from `ControlStatus`, preserving the existing single-direction relationship from `ControlStatus` to `DataQualityIssues`.

| Slicer | Field | Style | Visible values |
| --- | --- | --- | --- |
| Business Unit | `ControlStatus[business_unit]` | Dropdown | Finance, IT Operations, Retail Banking |
| Risk Level | `ControlStatus[risk_level]` | Dropdown | Critical, High, Medium |
| Reporting Period | `ControlStatus[reporting_period]` | Dropdown | all non-null canonical reporting-period values |

The Business Unit and Risk Level slicers exclude unresolved blank enrichment values from the selectable management list. This does **not** delete the underlying DQ-invalid Submission row from the model or from `Expected Submissions`.

Reporting periods intentionally remain heterogeneous because Controls have different frequencies:

```text
Annual:     2025, 2026
Quarterly:  2026-Q1, 2026-Q2, 2026-Q3
Monthly:    2026-06, 2026-07
```

No artificial normalization is added in Power BI.

## 5. KPI Cards

The page contains the six Management Overview KPIs frozen in the Phase 8 reporting contract:

| Card | Measure | Canonical unfiltered value |
| --- | --- | ---: |
| Controls in Scope | `[Controls in Scope]` | 5 |
| Assessed Compliance Rate | `[Assessed Compliance Rate]` | 80.0% |
| Non-Compliant Submissions | `[Non-Compliant Submissions]` | 1 |
| Overdue Submissions | `[Overdue Submissions]` | 1 |
| High/Critical Exceptions | `[High/Critical Exceptions]` | 2 |
| Total DQ Issues | `[Total DQ Issues]` | 5 |

The cards are aligned in one horizontal management KPI row.

No `Overall Status`, traffic-light composite, ROI claim, time-saved claim, or additional business classification is introduced.

## 6. Analytical Views

### Submission Status Distribution

Visual type:

```text
clustered column chart
```

Binding:

```text
Category: ControlStatus[submission_status]
Value:    [Expected Submissions]
```

Canonical unfiltered values:

```text
Compliant       7
Not Submitted   4
In Review       2
Non-Compliant   1
Pending         1
-----------------
Total          15
```

`Pending` remains visible because it is an intentionally DQ-invalid canonical source value and `Expected Submissions` deliberately keeps DQ-invalid source rows in expected volume.

### Assessed Compliance Rate by Business Unit

Visual type:

```text
clustered bar chart
```

Binding:

```text
Category: ControlStatus[business_unit]
Value:    [Assessed Compliance Rate]
```

Canonical business-unit results observed in Power BI Desktop:

```text
Finance          100.0%
IT Operations    100.0%
Retail Banking     0.0%
```

The zero percent for Retail Banking is an assessed result: one DQ-valid Non-Compliant Submission and zero DQ-valid Compliant Submissions.

### High/Critical Exceptions by Risk Level

Visual type:

```text
clustered column chart
```

Binding:

```text
Category: ControlStatus[risk_level]
Value:    [High/Critical Exceptions]
```

The visual is explicitly limited to the risk levels represented by the KPI definition:

```text
Critical
High
```

Canonical unfiltered values:

```text
Critical  1
High      1
```

Medium and unresolved blank risk are not shown in this exception-focused visual. The underlying records remain in the model.

## 7. Runtime Measure Hardening Discovered During Phase 8.6

Power BI Desktop smoke testing exposed a representation edge case: several count measures returned `BLANK()` for an empty result set in a valid filter context, causing KPI cards to render `--` even though the mathematically known count was zero.

Phase 8.6 therefore hardens five existing measures without changing their business definitions.

### Assessed Compliance Rate

Current expression:

```DAX
Assessed Compliance Rate =
DIVIDE(
    COALESCE([Compliant Submissions], 0),
    [Assessed Submissions]
)
```

Semantics:

- assessed rows exist and compliant count is zero → `0.0%`,
- no assessed denominator exists → `BLANK()` remains preserved through `DIVIDE`.

This distinguishes a known zero compliance result from a not-evaluable compliance rate.

### Count measures with explicit zero-result behavior

The following measures wrap their existing count logic in `COALESCE(..., 0)`:

```text
Non-Compliant Submissions
Overdue Submissions
High/Critical Exceptions
Total DQ Issues
```

This means:

```text
valid filter context + no matching rows → 0
```

It does not coerce nullable source attributes such as `overdue_flag`, `days_overdue`, or `days_late` to false or zero. Source null semantics remain unchanged.

## 8. Canonical Smoke-Test Evidence

### Unfiltered baseline

Observed in Power BI Desktop after the page was completed:

```text
Controls in Scope              5
Assessed Compliance Rate       80.0%
Non-Compliant Submissions      1
Overdue Submissions            1
High/Critical Exceptions       2
Total DQ Issues                5
```

### Retail Banking filter check

Observed with:

```text
Business Unit = Retail Banking
```

Results:

```text
Controls in Scope              1
Assessed Compliance Rate        0.0%
Non-Compliant Submissions      1
Overdue Submissions            0
High/Critical Exceptions       1
Total DQ Issues                1
```

This check confirmed the difference between a valid assessed 0% compliance result and a blank/not-evaluable rate.

### Finance filter check

Observed with:

```text
Business Unit = Finance
```

Results:

```text
Controls in Scope              1
Assessed Compliance Rate      100.0%
Non-Compliant Submissions      0
Overdue Submissions            0
High/Critical Exceptions       0
Total DQ Issues                0
```

This check confirmed that known empty counts render as zero rather than `--`.

These checks are Phase 8.6 smoke-test evidence. Formal canonical runtime acceptance of the complete Power BI measure set remains Phase 8.9.

## 9. Preserved Reporting Semantics

The Management Overview keeps the existing semantic separations explicit:

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

The page does not infer one synthetic overall status from these dimensions.

## 10. Scope Exclusions

Phase 8.6 does not:

- add a new data source,
- change Power Query ingestion,
- add a table or calculated table,
- add a calculated column,
- add or change a relationship,
- change the `ControlStatus → DataQualityIssues` filter direction,
- load raw Phase 7 snapshots or the operational workbook,
- load `ai_review_queue.json`,
- implement the Control Monitoring page,
- implement the Process & Data Quality page,
- perform formal Phase 8.9 acceptance,
- publish to Power BI Service.

## 11. Definition of Done

Phase 8.6 is complete when:

- [x] the report page is named `Management Overview`,
- [x] the management title is present,
- [x] Business Unit, Risk Level, and Reporting Period slicers are implemented,
- [x] all six contracted management KPI cards are implemented,
- [x] Submission Status Distribution uses `submission_status` and `[Expected Submissions]`,
- [x] Business Unit governance uses `[Assessed Compliance Rate]`,
- [x] risk-level exceptions use `[High/Critical Exceptions]`,
- [x] DQ-invalid expected Submission rows remain visible in expected volume,
- [x] Retail Banking 0% compliance behavior is runtime-verified,
- [x] zero-count KPI behavior is runtime-verified,
- [x] no Overall Status is introduced,
- [x] no new reporting source or relationship is introduced,
- [x] report metadata is source-controlled as PBIR,
- [x] Python regression tests remain green,
- [x] Phase 8 tracking is updated.

## 12. Next Work Package

Phase 8.7 builds the **Control Monitoring** page. It will add the detailed control/submission monitoring view using the existing semantic model and will not redefine the Phase 8.6 management KPI semantics.

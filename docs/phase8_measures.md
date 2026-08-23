# Phase 8.5 — Power BI Governance, Data Quality, Timeliness, and Process Measures

## Status

**PHASE 8.5 COMPLETE — 21 CONTRACTED DAX MEASURES IMPLEMENTED**

Phase 8.5 implements the semantic measures defined by the frozen Phase 8 reporting contract. It deliberately stops before report-page construction, final visual design, canonical runtime acceptance, operational Phase 7 acceptance, or Power BI Service publication.

## 1. Purpose

The Power BI model already contains:

- the source-controlled PBIP/PBIR/TMDL project,
- the configurable `DataRoot` reporting path,
- the curated `ControlStatus` and `DataQualityIssues` tables,
- technical typing and null preservation,
- one active one-to-many lineage relationship from `ControlStatus[source_row_number]` to `DataQualityIssues[source_row_number]`.

Phase 8.5 adds only reusable DAX measures. Power BI remains a reporting consumer of Python-owned semantics rather than a second business-rule engine.

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
Phase 8.5 — DAX measures
        ↓
Phase 8.6–8.8 — report pages
```

## 2. Model Boundary

The Phase 8.5 semantic-model boundary remains:

```text
Model tables:     2
Relationships:    1
Measures:        21
Calculated tables: 0
Calculated columns: 0
```

No additional data source, relationship, calculated table, calculated column, Power Query business rule, AI calculation, or report visual is introduced.

## 3. Measure Allocation

The 21 measures are stored with their logical reporting tables:

```text
ControlStatus       16 measures
DataQualityIssues    5 measures
-------------------------------
Total               21 measures
```

### ControlStatus measures

1. `Controls in Scope`
2. `Expected Submissions`
3. `Valid Submissions`
4. `Invalid Submissions`
5. `Assessed Submissions`
6. `Compliant Submissions`
7. `Non-Compliant Submissions`
8. `Assessed Compliance Rate`
9. `Overdue Submissions`
10. `Late Submissions`
11. `High/Critical Exceptions`
12. `Overdue Submission Rate`
13. `Total Automated Reminders`
14. `Active Follow-up Submissions`
15. `Submissions with Reminder History`
16. `Average Reminders per Reminded Submission`

### DataQualityIssues measures

17. `Total DQ Issues`
18. `Submissions with DQ Issues`
19. `DQ Issue Rate`
20. `High-Severity DQ Issues`
21. `Missing Evidence Issues`

## 4. Governance Measures

### Controls in Scope

```DAX
Controls in Scope =
CALCULATE(
    DISTINCTCOUNT(ControlStatus[control_id]),
    FILTER(
        ControlStatus,
        NOT ISBLANK(ControlStatus[control_name])
    )
)
```

The measure counts only rows whose Control enrichment resolved successfully. This prevents the intentionally invalid canonical `CTRL-999` source row from becoming a sixth Control in scope.

Canonical expected value: **5**.

### Expected Submissions

```DAX
Expected Submissions =
COUNTROWS(ControlStatus)
```

Submission is the reporting grain. DQ-invalid rows remain part of expected volume rather than disappearing from the denominator.

Canonical expected value: **15**.

### Valid Submissions

```DAX
Valid Submissions =
CALCULATE(
    COUNTROWS(ControlStatus),
    ControlStatus[data_quality_status] = "Valid"
)
```

Canonical expected value: **10**.

### Invalid Submissions

```DAX
Invalid Submissions =
CALCULATE(
    COUNTROWS(ControlStatus),
    ControlStatus[data_quality_status] = "Invalid"
)
```

Canonical expected value: **5**.

### Assessed Submissions

```DAX
Assessed Submissions =
CALCULATE(
    COUNTROWS(ControlStatus),
    FILTER(
        ControlStatus,
        ControlStatus[data_quality_status] = "Valid"
            &&
        (
            ControlStatus[submission_status] = "Compliant"
            ||
            ControlStatus[submission_status] = "Non-Compliant"
        )
    )
)
```

Only DQ-valid rows with an explicit compliance outcome are assessed. `In Review` and `Not Submitted` are not converted into compliance results.

Canonical expected value: **5**.

### Compliant Submissions

```DAX
Compliant Submissions =
CALCULATE(
    COUNTROWS(ControlStatus),
    ControlStatus[data_quality_status] = "Valid",
    ControlStatus[submission_status] = "Compliant"
)
```

Canonical expected value: **4**.

### Non-Compliant Submissions

```DAX
Non-Compliant Submissions =
CALCULATE(
    COUNTROWS(ControlStatus),
    ControlStatus[data_quality_status] = "Valid",
    ControlStatus[submission_status] = "Non-Compliant"
)
```

Canonical expected value: **1**.

### Assessed Compliance Rate

```DAX
Assessed Compliance Rate =
DIVIDE(
    [Compliant Submissions],
    [Assessed Submissions]
)
```

The denominator is assessed submissions, not all expected submissions and not Controls in Scope. `DIVIDE` preserves blank behavior if no assessed submissions exist.

Format: percentage, one decimal place.

Canonical expected value: **80.0%**.

## 5. Timeliness and Exception Measures

### Overdue Submissions

```DAX
Overdue Submissions =
CALCULATE(
    COUNTROWS(ControlStatus),
    ControlStatus[data_quality_status] = "Valid",
    ControlStatus[overdue_flag] = TRUE()
)
```

Canonical expected value: **1**.

### Late Submissions

```DAX
Late Submissions =
CALCULATE(
    COUNTROWS(ControlStatus),
    ControlStatus[data_quality_status] = "Valid",
    ControlStatus[submission_late] = TRUE()
)
```

Canonical expected value: **1**.

### High/Critical Exceptions

```DAX
High/Critical Exceptions =
CALCULATE(
    COUNTROWS(ControlStatus),
    FILTER(
        ControlStatus,
        ControlStatus[data_quality_status] = "Valid"
            &&
        (
            ControlStatus[risk_level] = "High"
            ||
            ControlStatus[risk_level] = "Critical"
        )
            &&
        (
            ControlStatus[submission_status] = "Non-Compliant"
            ||
            ControlStatus[overdue_flag] = TRUE()
        )
    )
)
```

This is an exception count, not a composite overall status. Compliance outcome, timeliness, and Control risk remain separate dimensions.

Canonical expected value: **2**.

### Overdue Submission Rate

```DAX
Overdue Submission Rate =
DIVIDE(
    [Overdue Submissions],
    [Valid Submissions]
)
```

Format: percentage, one decimal place.

Canonical expected value: **10.0%**.

## 6. Process and Reminder Measures

### Total Automated Reminders

```DAX
Total Automated Reminders =
SUM(ControlStatus[reminder_count])
```

The measure consumes the reminder aggregation already produced upstream. It does not reconstruct reminder history in Power BI.

Canonical expected value: **4**.

### Active Follow-up Submissions

```DAX
Active Follow-up Submissions =
CALCULATE(
    COUNTROWS(ControlStatus),
    FILTER(
        ControlStatus,
        NOT ISBLANK(ControlStatus[active_action_id])
    )
)
```

This reports the current active Action projection represented by the curated schema. It is not a claim about every historical Action that ever existed.

Canonical expected value: **4**.

### Submissions with Reminder History

```DAX
Submissions with Reminder History =
CALCULATE(
    COUNTROWS(ControlStatus),
    FILTER(
        ControlStatus,
        ControlStatus[reminder_count] > 0
    )
)
```

Canonical expected value: **4**.

### Average Reminders per Reminded Submission

```DAX
Average Reminders per Reminded Submission =
DIVIDE(
    [Total Automated Reminders],
    [Submissions with Reminder History]
)
```

Format: decimal number, two decimal places.

Canonical expected value: **1.00**.

## 7. Data Quality Measures

### Total DQ Issues

```DAX
Total DQ Issues =
COUNTROWS(DataQualityIssues)
```

Canonical expected value: **5**.

### Submissions with DQ Issues

```DAX
Submissions with DQ Issues =
DISTINCTCOUNT(DataQualityIssues[source_row_number])
```

The technical lineage key is deliberately used instead of `submission_id`, because missing or duplicate business identifiers are valid DQ scenarios.

Canonical expected value: **5**.

### DQ Issue Rate

```DAX
DQ Issue Rate =
DIVIDE(
    [Submissions with DQ Issues],
    [Expected Submissions]
)
```

The denominator remains all expected Submission rows, including DQ-invalid records.

Format: percentage, one decimal place.

Canonical expected value: **33.3%**.

### High-Severity DQ Issues

```DAX
High-Severity DQ Issues =
CALCULATE(
    [Total DQ Issues],
    DataQualityIssues[severity] = "High"
)
```

DQ severity is not Control risk. These dimensions remain semantically separate.

Canonical expected value: **5**.

### Missing Evidence Issues

```DAX
Missing Evidence Issues =
CALCULATE(
    [Total DQ Issues],
    DataQualityIssues[rule] = "DQ-004 Missing Evidence"
)
```

Canonical expected value: **1**.

## 8. Formatting Contract

```text
Assessed Compliance Rate                    percentage / 1 decimal
Overdue Submission Rate                    percentage / 1 decimal
DQ Issue Rate                              percentage / 1 decimal
Average Reminders per Reminded Submission decimal / 2 decimals
All remaining measures                    whole number
```

The source-controlled TMDL stores the corresponding measure format strings.

## 9. Canonical Acceptance Baseline

The deterministic Phase 8.1 fixture produces the following expected measure values:

| Measure | Expected |
|---|---:|
| Controls in Scope | 5 |
| Expected Submissions | 15 |
| Valid Submissions | 10 |
| Invalid Submissions | 5 |
| Assessed Submissions | 5 |
| Compliant Submissions | 4 |
| Non-Compliant Submissions | 1 |
| Assessed Compliance Rate | 80.0% |
| Overdue Submissions | 1 |
| Late Submissions | 1 |
| High/Critical Exceptions | 2 |
| Overdue Submission Rate | 10.0% |
| Total Automated Reminders | 4 |
| Active Follow-up Submissions | 4 |
| Submissions with Reminder History | 4 |
| Average Reminders per Reminded Submission | 1.00 |
| Total DQ Issues | 5 |
| Submissions with DQ Issues | 5 |
| DQ Issue Rate | 33.3% |
| High-Severity DQ Issues | 5 |
| Missing Evidence Issues | 1 |

These are semantic acceptance targets. Formal Power BI runtime acceptance remains Phase 8.9.

## 10. Preserved Semantic Separations

Phase 8.5 keeps the reporting model intentionally non-collapsing:

- Evidence Present != Compliant
- Not Submitted != Non-Compliant
- Non-Compliant != Overdue
- Compliance != Timeliness
- Compliance != Data Quality
- Submission Status != Action Status
- Unknown != False
- Not Evaluated != Failed
- Action completion != Submission compliance
- Control risk != DQ severity

No `Overall Status` is introduced.

## 11. Power BI Desktop Side-Effect Review

Power BI Desktop changed default summarization metadata for three numeric source columns while measures were created:

```text
days_overdue
days_late
reminder_count
```

Those unrelated changes were reverted so their pre-Phase-8.5 summarization settings remain intact. The Phase 8.5 semantic diff therefore contains the 21 measures plus model-diagram layout metadata, without unrelated source-column behavior changes.

`diagramLayout.json` is versioned because it contains only reproducible semantic-model diagram layout information such as node position, size, zoom, and selected diagram. It contains no reporting rows, credentials, private operational values, or tenant binding.

## 12. Scope Exclusions

Phase 8.5 does not:

- add report cards, charts, slicers, or pages,
- add a dedicated calculated Measures table,
- add calculated columns,
- add calculated tables,
- add relationships,
- change relationship direction,
- change Power Query ingestion,
- load raw operational or private sources,
- calculate AI eligibility,
- invent ROI or time-saved metrics,
- publish to Power BI Service.

## 13. Definition of Done

Phase 8.5 is complete when:

- [x] exactly 21 contracted measures exist,
- [x] 16 measures are stored with `ControlStatus`,
- [x] 5 measures are stored with `DataQualityIssues`,
- [x] Governance measures preserve DQ-valid assessment semantics,
- [x] timeliness measures use DQ-valid records,
- [x] DQ measures use raw-row lineage where required,
- [x] all percentage and decimal formats match the contract,
- [x] no calculated table or calculated column is added,
- [x] the model still contains exactly two reporting tables,
- [x] the model still contains exactly one active lineage relationship,
- [x] no Power Query business logic is added,
- [x] unrelated numeric-column summarization changes are reverted,
- [x] no generated curated or private operational data is committed,
- [x] Python regression tests remain green,
- [x] Phase 8 tracking is updated.

## 14. Next Work Package

Phase 8.6 builds the Management Overview page using the measures defined here. No measure semantics should be reimplemented inside visuals.

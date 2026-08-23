# Phase 8.4 — Power BI Semantic Model Relationship

## Status

**PHASE 8.4 COMPLETE — EXPLICIT SUBMISSION-LINEAGE RELATIONSHIP IMPLEMENTED**

Phase 8.4 adds the single semantic-model relationship required by the frozen Phase 8 reporting contract. It deliberately stops before DAX measures, calculated columns, final report visuals, or KPI implementation.

## 1. Purpose

Phase 8.3 loaded and technically typed the two curated Python reporting outputs:

```text
ControlStatus
DataQualityIssues
```

Phase 8.4 now connects them through the technical raw-row lineage key so Data Quality Issue rows can be filtered from their parent Submission row without relying on potentially missing or duplicate business identifiers.

The dependency sequence is:

```text
Phase 8.0 — reporting/KPI contract
        ↓
Phase 8.1 — canonical reporting baseline
        ↓
Phase 8.2 — PBIP/PBIR/TMDL scaffold
        ↓
Phase 8.3 — curated loading and technical typing
        ↓
Phase 8.4 — semantic relationship
        ↓
Phase 8.5 — DAX measures
```

## 2. Relationship Contract

The implemented relationship is:

```text
ControlStatus[source_row_number]
          1
          │
          │
          *
DataQualityIssues[source_row_number]
```

Required semantics:

```text
one side        = ControlStatus[source_row_number]
many side       = DataQualityIssues[source_row_number]
cardinality     = one-to-many
cross-filter    = single direction
filter flow     = ControlStatus → DataQualityIssues
relationship    = active
```

Power BI stores the generated TMDL relationship as:

```text
fromColumn: DataQualityIssues.source_row_number
toColumn:   ControlStatus.source_row_number
```

For a single-direction many-to-one relationship, the `to`/one side filters the `from`/many side. Therefore the effective filter propagation is `ControlStatus → DataQualityIssues`.

## 3. Why `source_row_number` Is the Relationship Key

The relationship is intentionally **not** built on `submission_id`.

The deterministic Data Quality contract explicitly permits source rows where `submission_id` is missing or duplicated. In particular, DQ-005 validates duplicate Submission identifiers/business instances rather than silently repairing them.

`source_row_number` is the technical raw-row lineage identifier. It remains available even when a business identifier is invalid, which makes it the correct bridge between the curated Submission-grain table and the issue-grain DQ table.

This preserves an important reporting property:

```text
DQ-invalid Submission rows remain visible
and can still be related to their DQ findings.
```

## 4. Grain Preservation

`ControlStatus` remains:

```text
one row per raw Submission source row
```

`DataQualityIssues` remains:

```text
one row per triggered DQ rule per raw Submission source row
```

A single Submission source row can therefore have:

```text
0 DQ issues
1 DQ issue
multiple DQ issues
```

The current canonical dataset happens to contain five affected source rows with one issue each, but the semantic model must not encode that fixture accident as a one-to-one relationship.

## 5. Relationship Acceptance

Power BI Desktop acceptance confirmed:

```text
Model tables:          2
Relationships:         1
ControlStatus side:    1
DataQualityIssues side: *
Cross-filter:          single
Status:                active
```

The generated TMDL relationship file is:

```text
powerbi/CyberGovernanceDashboard/
└── CyberGovernanceDashboard.SemanticModel/
    └── definition/
        └── relationships.tmdl
```

No additional or automatic relationship is present.

## 6. Technical Lineage Fields Hidden from Report Consumers

`source_row_number` remains physically present in both semantic-model tables because the relationship depends on it.

It is hidden from report consumers in both tables:

```text
ControlStatus[source_row_number]       → isHidden
DataQualityIssues[source_row_number]   → isHidden
```

The fields are therefore retained for model lineage while not being exposed as normal end-user reporting attributes.

They are not deleted, transformed, or replaced by another key.

## 7. Boundary Preservation

Phase 8.4 does not change Phase 8.3 ingestion behavior.

Power BI still consumes exactly:

```text
curated_control_status.csv
data_quality_issues.csv
```

The `DataRoot` parameter remains unchanged.

Phase 8.4 does not add:

```text
raw operational sources
canonical raw inputs
ai_review_queue.json
Power Query business rules
DAX measures
calculated columns
calculated tables
additional relationships
bidirectional filtering
report visuals
final report pages
```

Python remains responsible for Data Quality, Control enrichment, Action aggregation, overdue/lateness derivation, and AI-review eligibility.

## 8. Semantic Separations Preserved

The relationship does not collapse any governance concepts. The model continues to preserve:

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

No `Overall Status` field is introduced.

## 9. Definition of Done

Phase 8.4 is complete when:

- [x] exactly one semantic-model relationship exists,
- [x] `ControlStatus[source_row_number]` is the one side,
- [x] `DataQualityIssues[source_row_number]` is the many side,
- [x] the relationship is active,
- [x] cross-filtering is single-direction,
- [x] effective filter propagation is `ControlStatus → DataQualityIssues`,
- [x] no relationship exists on `submission_id`,
- [x] both technical `source_row_number` columns remain in the model,
- [x] both technical key columns are hidden from report consumers,
- [x] no second relationship is present,
- [x] no DAX measure or calculated column is introduced,
- [x] no Power Query business logic changes are introduced,
- [x] the Phase 8.3 source boundary remains unchanged.

**Phase 8.4 status: COMPLETE**

## 10. Next Work Package

Phase 8.5 implements the frozen governance, timeliness, Data Quality, and process-impact measures.

The measure implementation must follow `docs/phase8_power_bi_contract.md` and the canonical values fixed in `docs/phase8_canonical_baseline.md`. Phase 8.5 must not redefine KPI semantics for visual convenience.
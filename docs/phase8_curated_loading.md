# Phase 8.3 — Curated Power BI Source Loading

## Status

**PHASE 8.3 COMPLETE — CURATED REPORTING SOURCES LOADED AND TYPED**

Phase 8.3 implements the first functional Power BI data-ingestion layer on top of the Phase 8.2 PBIP/PBIR/TMDL project scaffold.

It loads exactly the two curated Python reporting outputs defined by the Phase 8.0 contract:

```text
curated_control_status.csv
data_quality_issues.csv
```

and exposes them as the Power BI model tables:

```text
ControlStatus
DataQualityIssues
```

Phase 8.3 deliberately stops before semantic-model relationships, DAX measures, final report pages, or Power BI Service deployment.

## 1. Dependency Chain

```text
Phase 8.0
Reporting/KPI contract
        ↓
Phase 8.1
Canonical reporting baseline
        ↓
Phase 8.2
PBIP/PBIR/TMDL project scaffold
        ↓
Phase 8.3
Curated CSV loading + technical typing
        ↓
Phase 8.4
Semantic model relationship
```

Phase 8.3 does not redefine any business semantics established upstream.

## 2. Source Boundary

Power BI consumes only:

```text
curated_control_status.csv
data_quality_issues.csv
```

The implementation does not load any of the following directly:

```text
Cyber_Governance_Control_Register.xlsx
ControlCatalog
SubmissionRegister
ActionRegister
security_control_snapshot_*.json
security_submission_snapshot_*.csv
security_action_snapshot_*.csv
security_snapshot_manifest_*.json
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
ai_review_queue.json
```

This preserves the responsibility boundary:

```text
Power Automate exports source facts.
Python owns DQ, Control enrichment, Action aggregation,
and derived reporting metrics.
Power BI consumes the curated result.
```

## 3. Configurable Data Root

The semantic model now contains a Power Query parameter:

```text
DataRoot
```

Description:

```text
Root directory containing Python curated reporting outputs.
```

The parameter is defined as required text and is referenced by both table partitions.

The authoring value committed by the current project is:

```text
C:\dev\cyber-governance-automation-lab\data\curated
```

This is an authoring/default value, not a deployment contract. A different local clone or later operational acceptance can change `DataRoot` without rewriting the two table queries.

No trailing path separator is stored in the parameter. Each table appends its own contractual file name.

## 4. `ControlStatus` Query

Physical source:

```text
DataRoot & "\curated_control_status.csv"
```

Power Query steps are limited to technical ingestion:

```text
Source
→ PromotedHeaders
→ BlankToNull
→ Typed
```

The query:

- reads UTF-8 CSV,
- uses comma delimiter,
- promotes the first row to headers,
- converts empty strings to null,
- applies the frozen technical type contract,
- does not filter, deduplicate, repair, aggregate, or derive business state.

Canonical load acceptance in Power BI Desktop:

```text
15 rows
25 columns
```

The unresolved canonical DQ row remains visible:

```text
SUB-015
control_id = CTRL-999
resolved Control enrichment = null
```

This confirms that Phase 8.3 does not remove DQ-invalid source rows.

### Type contract

```text
source_row_number       Whole number
submission_id           Text
control_id              Text
control_name            Text / null
business_unit           Text / null
owner_role              Text / null
owner_email             Text / null
frequency               Text / null
risk_level              Text / null
reporting_period         Text
due_date                 Date
submission_status        Text
evidence_present         Boolean
submitted_at             Date / null
comment                  Text / null
overdue_flag             Boolean / null
submission_late          Boolean / null
days_overdue             Whole number / null
days_late                Whole number / null
data_quality_status      Text
active_action_id         Text / null
active_action_status     Text / null
active_action_due_date   Date / null
reminder_count           Whole number
last_reminder_at         Date / null
```

The generated TMDL represents Power Query `type date` columns as semantic-model `dateTime` columns with `UnderlyingDateTimeDataType = Date`. This is normal Power BI serialization and preserves the requested Date semantic type.

## 5. `DataQualityIssues` Query

Physical source:

```text
DataRoot & "\data_quality_issues.csv"
```

Power Query steps are the same technical-only pattern:

```text
Source
→ PromotedHeaders
→ BlankToNull
→ Typed
```

Canonical load acceptance in Power BI Desktop:

```text
5 rows
8 columns
```

The five expected canonical findings remain present:

```text
SUB-002 → DQ-004 Missing Evidence
SUB-006 → DQ-003 Invalid Status
SUB-008 → DQ-005 Duplicate Submission
SUB-009 → DQ-005 Duplicate Submission
SUB-015 → DQ-002 Unknown Control ID
```

### Type contract

```text
issue_id            Text
submission_id       Text
control_id          Text
source_row_number   Whole number
rule                Text
severity            Text
field               Text
message             Text
```

## 6. Null Semantics

Phase 8.3 preserves the Phase 8.0 null contract.

The Power Query ingestion explicitly converts empty CSV strings to null before type assignment:

```text
"" → null
```

This is especially important for timing fields such as:

```text
overdue_flag
submission_late
days_overdue
days_late
submitted_at
active_action_due_date
last_reminder_at
```

Unknown or non-evaluable state is not coerced to:

```text
False
0
```

No business interpretation is added in Power Query.

## 7. Semantic Model State

At the end of Phase 8.3 the semantic model contains exactly two business/reporting tables:

```text
ControlStatus
DataQualityIssues
```

`model.tmdl` records query order:

```text
DataRoot
ControlStatus
DataQualityIssues
```

Automatic time intelligence is disabled:

```text
__PBI_TimeIntelligenceEnabled = 0
```

The Power BI Desktop model view was manually verified to contain both tables and no relationship line between them.

The TMDL definition directory contains no relationship definition artifact.

Therefore Phase 8.4 remains the owner of the explicit relationship:

```text
ControlStatus[source_row_number]
          1
          │
          *
DataQualityIssues[source_row_number]
```

## 8. No Premature Business Logic

Phase 8.3 does not implement:

```text
compliance calculations
overdue calculations
lateness calculations
DQ rules
DQ repair
deduplication
Action aggregation
AI eligibility
semantic-model relationship
DAX measures
calculated columns
final report visuals
Power BI Service deployment
```

No `Overall Status` field or measure is introduced.

## 9. Source-Control Representation

Phase 8.3 adds or changes the following TMDL/model files:

```text
CyberGovernanceDashboard.SemanticModel/
├── .pbi/
│   └── editorSettings.json
└── definition/
    ├── expressions.tmdl
    ├── model.tmdl
    └── tables/
        ├── ControlStatus.tmdl
        └── DataQualityIssues.tmdl
```

Generated curated CSV/JSON runtime outputs remain ignored under `data/curated/` and are not committed.

Local Power BI cache/state remains excluded through the existing `.gitignore` boundary.

## 10. Acceptance Evidence

Repository inspection confirms:

- `DataRoot` exists as a required text parameter,
- `ControlStatus` reads only `curated_control_status.csv`,
- `DataQualityIssues` reads only `data_quality_issues.csv`,
- both queries use UTF-8 CSV ingestion,
- both queries promote headers,
- empty strings are normalized to null,
- `ControlStatus` implements all 25 frozen fields,
- `DataQualityIssues` implements all 8 frozen fields,
- the required Whole number / Date / Boolean / Text types are represented,
- no relationship artifact exists,
- no DAX measure is present,
- no calculated column is present,
- no additional reporting source is present,
- no generated curated data is committed,
- no private Phase 7 operational data is committed.

Power BI Desktop acceptance additionally confirmed:

```text
ControlStatus       = 15 rows / 25 columns
DataQualityIssues   = 5 rows / 8 columns
Model tables        = exactly 2
Relationships       = 0
```

## 11. Definition of Done

Phase 8.3 is complete when:

- [x] canonical curated outputs are generated locally from the frozen `2026-08-15` baseline,
- [x] `DataRoot` parameter exists,
- [x] `ControlStatus` query exists,
- [x] `DataQualityIssues` query exists,
- [x] `ControlStatus` has 15 canonical rows and 25 columns,
- [x] `DataQualityIssues` has 5 canonical rows and 8 columns,
- [x] empty strings are preserved as null rather than semantic false/zero,
- [x] technical field types match the Phase 8.0 contract,
- [x] DQ-invalid rows remain visible,
- [x] exactly two reporting tables are loaded,
- [x] automatic time intelligence is disabled,
- [x] no model relationship is created,
- [x] no DAX measures or calculated columns are created,
- [x] no final visuals are created,
- [x] no raw/operational source is loaded,
- [x] generated curated outputs remain outside Git,
- [x] TMDL source representation is committed.

**Phase 8.3 status: COMPLETE**

## 12. Next Work Package

Phase 8.4 will establish the explicit semantic-model relationship:

```text
ControlStatus[source_row_number]
          1
          │
          *
DataQualityIssues[source_row_number]
```

Required behavior:

```text
Cardinality      = one-to-many
Filter direction = ControlStatus → DataQualityIssues
```

`submission_id` must not be used as the relationship key because duplicate and missing Submission identifiers are valid Data Quality scenarios.
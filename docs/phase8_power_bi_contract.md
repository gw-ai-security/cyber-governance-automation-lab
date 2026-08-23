# Phase 8.0 — Power BI Reporting and KPI Contract

## Status

**PHASE 8.0 COMPLETE — REPORTING CONTRACT FROZEN**

Phase 8.0 fixes the semantic and implementation boundary for the Phase 8 Power BI dashboard before any report artifact, Power Query model, DAX measure, or visual is built.

Current state after this work package:

```text
Phase 7 reporting snapshot bridge = COMPLETE
Phase 8.0 reporting/KPI contract   = COMPLETE
Phase 8 Power BI runtime           = NOT YET IMPLEMENTED
Phase 9 controlled AI runtime      = NOT IMPLEMENTED
Phase 10 REST API                  = NOT IMPLEMENTED
```

This document is the authoritative Phase 8 planning contract for the dashboard implementation. If later visual convenience conflicts with the established Python/reporting semantics, the report implementation must change rather than redefining the business model in Power BI.

## 1. Purpose

Phase 8 turns the curated reporting outputs produced by the existing deterministic Python pipeline into a small governance dashboard.

The intended path is:

```text
Operational Microsoft 365 state
        ↓
Phase 7 private snapshot package
        ↓
explicit Python source paths
        ↓
EXTRACT → NORMALIZE → VALIDATE → TRANSFORM / ENRICH → DERIVE → LOAD
        ↓
curated_control_status.csv
        +
data_quality_issues.csv
        ↓
Power BI semantic model
        ↓
Governance / timeliness / DQ / follow-up reporting
```

The Power BI layer is a reporting consumer. It is not another business-rule engine.

## 2. Source-of-Truth and Dependency Order

Phase 8 inherits the repository source-of-truth priority:

```text
implemented code + canonical data + automated tests
        ↓
current-state foundation documentation
        ↓
latest phase contract / acceptance evidence
        ↓
historical plans
```

The main upstream dependencies are:

- `src/transform.py` — curated grain, Control enrichment, Action aggregation, timing derivation,
- `src/validate.py` — DQ-001 through DQ-010,
- `src/load.py` — physical reporting output files,
- `docs/data_model.md` — entity/status semantics,
- `docs/data_contract.md` — physical data-plane contract,
- `docs/data_quality.md` — DQ semantics,
- `docs/phase3_pipeline_contract.md` — exact curated/DQ output contracts,
- `docs/phase7_reporting_export.md` — operational reporting bridge,
- `docs/phase7_end_to_end_acceptance.md` — accepted operational end-to-end evidence.

Phase 8 must not silently override these dependencies.

## 3. Phase 8 Data-Source Boundary

Power BI must load exactly these two Python reporting outputs:

```text
curated_control_status.csv
data_quality_issues.csv
```

Recommended Power BI query names:

```text
ControlStatus
DataQualityIssues
```

Phase 8 must **not** directly load any of the following as additional business sources:

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

Rationale:

```text
Power Automate exports source facts.
Python owns DQ, Control enrichment, Action aggregation,
and derived reporting metrics.
Power BI consumes the curated result.
```

Directly re-reading raw/operational sources in Power BI would create a second implementation of semantics already owned by Python and would weaken the tested reporting boundary established in Phase 7.

`ai_review_queue.json` remains outside Phase 8 because it is an input to the later controlled AI workflow, not a required Power BI reporting source.

## 4. Reporting Grain

### 4.1 `ControlStatus`

Physical source:

```text
curated_control_status.csv
```

Grain:

```text
one row per raw Submission source row
```

Submission is the primary reporting grain.

The current exact fields are:

```text
source_row_number
submission_id
control_id
control_name
business_unit
owner_role
owner_email
frequency
risk_level
reporting_period
due_date
submission_status
evidence_present
submitted_at
comment
overdue_flag
submission_late
days_overdue
days_late
data_quality_status
active_action_id
active_action_status
active_action_due_date
reminder_count
last_reminder_at
```

Action rows are already aggregated in Python before reaching this dataset. Power BI must not treat this table as raw Action grain.

### 4.2 `DataQualityIssues`

Physical source:

```text
data_quality_issues.csv
```

Grain:

```text
one row per triggered DQ rule per raw Submission source row
```

Exact fields:

```text
issue_id
submission_id
control_id
source_row_number
rule
severity
field
message
```

One Submission source row may therefore have zero, one, or multiple Data Quality Issue rows.

## 5. Semantic Model Relationship

The Phase 8 relationship is fixed as:

```text
ControlStatus[source_row_number]
          1
          │
          │
          *
DataQualityIssues[source_row_number]
```

Required behavior:

```text
Cardinality     = one-to-many
Filter direction = ControlStatus → DataQualityIssues
```

`source_row_number` is used because it is the stable raw-row lineage key. It remains valid even when a Submission identifier is missing or duplicated.

The relationship must **not** be built on `submission_id`, because duplicate or missing Submission identifiers are valid DQ test scenarios and DQ-005 explicitly validates identifier uniqueness.

`source_row_number` is technical lineage metadata and should normally be hidden from end-user report views after the relationship is established.

## 6. Semantic Separations that Power BI Must Preserve

The dashboard must preserve the repository-wide invariants:

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
```

Additional Power BI consequences:

```text
Control risk != DQ severity
Submission status != Action status
Current stored active Action != inferred business need
```

The report must not create an `Overall Status` calculation that collapses these separate dimensions into one opaque state.

## 7. Power Query Responsibility Boundary

Power Query may perform technical ingestion tasks only:

- resolve a configurable curated-data root path,
- load the two CSV outputs,
- assign technical data types,
- rename the two queries to their reporting names,
- hide or disable helper queries if required by the implementation.

Power Query must not:

- calculate compliance,
- calculate overdue or lateness,
- apply DQ-001 through DQ-010,
- repair malformed records,
- remove DQ-invalid rows to make KPIs look cleaner,
- deduplicate Submission rows,
- aggregate raw Actions,
- infer Action completion,
- derive AI-review eligibility.

Those responsibilities already belong to upstream deterministic code.

## 8. Type and Null Contract

### `ControlStatus`

Expected Power BI types:

| Field | Type |
| --- | --- |
| `source_row_number` | Whole number |
| `due_date` | Date |
| `submitted_at` | Date / null |
| `active_action_due_date` | Date / null |
| `last_reminder_at` | Date / null |
| `evidence_present` | Boolean |
| `overdue_flag` | Boolean / null |
| `submission_late` | Boolean / null |
| `days_overdue` | Whole number / null |
| `days_late` | Whole number / null |
| `reminder_count` | Whole number |
| all remaining fields | Text / null as applicable |

### `DataQualityIssues`

| Field | Type |
| --- | --- |
| `source_row_number` | Whole number |
| all remaining fields | Text / null as applicable |

Critical rule:

```text
unknown / non-evaluable
must remain blank/null
```

Power Query or DAX must not coerce non-evaluable timing values into known negatives such as:

```text
False
0
```

The Python contract explicitly preserves unknown timing state when prerequisites cannot be evaluated.

## 9. Control Scope Semantics

A Control can occur in many Submission rows across reporting periods. Therefore Control-level counts and Submission-level assessment counts serve different purposes.

`Controls in Scope` is a context KPI, not the compliance denominator.

The canonical curated dataset intentionally contains an unresolved test row:

```text
SUB-015 → CTRL-999 → DQ-002 Unknown Control ID
```

Therefore a blind:

```text
DISTINCTCOUNT(control_id)
```

would incorrectly count the unresolved `CTRL-999` as a sixth in-scope Control.

The required semantic definition is:

```text
Controls in Scope
=
distinct control_id values for rows with a resolved Control
```

A resolved Control is represented by populated Control enrichment such as `control_name`.

This preserves the canonical Control inventory of five while keeping unresolved rows visible for DQ reporting.

## 10. KPI Contract — Governance

DAX implementation is deferred to the measure work package. The business definitions are frozen here.

### 10.1 Expected Submissions

```text
COUNT of ControlStatus rows
```

Includes both DQ-valid and DQ-invalid source rows because the curated contract deliberately preserves every Submission source row.

### 10.2 Valid Submissions

```text
COUNT of ControlStatus rows
WHERE data_quality_status = Valid
```

### 10.3 Invalid Submissions

```text
COUNT of ControlStatus rows
WHERE data_quality_status = Invalid
```

### 10.4 Assessed Submissions

```text
COUNT of ControlStatus rows
WHERE data_quality_status = Valid
AND submission_status IN (Compliant, Non-Compliant)
```

`In Review` and `Not Submitted` are not final governance assessments.

### 10.5 Compliant Submissions

```text
COUNT of ControlStatus rows
WHERE data_quality_status = Valid
AND submission_status = Compliant
```

### 10.6 Non-Compliant Submissions

```text
COUNT of ControlStatus rows
WHERE data_quality_status = Valid
AND submission_status = Non-Compliant
```

A Non-Compliant Submission is a security/control outcome, not a Data Quality error.

### 10.7 Assessed Compliance Rate

```text
Compliant Submissions
/
Assessed Submissions
```

If there are no assessed Submissions in the current filter context, the measure returns blank rather than inventing a percentage.

This measure is intentionally named **Assessed Compliance Rate**. It must not be implemented as:

```text
Compliant distinct Controls / all distinct Controls
```

because one Control may have different Submission states across different reporting periods.

## 11. KPI Contract — Timeliness and Exceptions

Management-level timeliness/exception KPIs use DQ-valid records so the aggregated result is based on evaluable/trusted Submission state. DQ-invalid rows remain visible in the detailed monitoring and DQ pages.

### 11.1 Overdue Submissions

```text
COUNT of ControlStatus rows
WHERE data_quality_status = Valid
AND overdue_flag = True
```

Overdue means missing after the due date. It does not mean Non-Compliant.

### 11.2 Late Submissions

```text
COUNT of ControlStatus rows
WHERE data_quality_status = Valid
AND submission_late = True
```

Late means evidence was submitted after the due date. A late Submission may still be Compliant.

### 11.3 High/Critical Exceptions

```text
COUNT of ControlStatus rows
WHERE data_quality_status = Valid
AND risk_level IN (High, Critical)
AND (
    submission_status = Non-Compliant
    OR overdue_flag = True
)
```

This combines Control risk with an explicit governance/process exception without treating risk level as another status.

### 11.4 Overdue Submission Rate

```text
Overdue Submissions
/
Valid Submissions
```

The denominator remains DQ-valid Submission grain.

## 12. KPI Contract — Data Quality

### 12.1 Total DQ Issues

```text
COUNT of DataQualityIssues rows
```

### 12.2 Submissions with DQ Issues

```text
DISTINCTCOUNT(DataQualityIssues[source_row_number])
```

### 12.3 DQ Issue Rate

```text
Submissions with DQ Issues
/
Expected Submissions
```

### 12.4 High-Severity DQ Issues

```text
COUNT of DataQualityIssues rows
WHERE severity = High
```

### 12.5 Missing Evidence Issues

```text
COUNT of DataQualityIssues rows
WHERE rule = DQ-004 Missing Evidence
```

DQ severity values are:

```text
High
Medium
Low
```

They must not be confused with Control risk values:

```text
Low
Medium
High
Critical
```

## 13. KPI Contract — Follow-up and Process Impact

Phase 6 operationalizes reminder history on Action. Phase 7 proves that the relevant aggregated facts reach `ControlStatus`.

### 13.1 Total Automated Reminders

```text
SUM(ControlStatus[reminder_count])
```

`reminder_count` is already aggregated across all related Actions for the Submission by Python.

The measure reports observed confirmed reminder history. It does not estimate time saved or labour avoided.

### 13.2 Active Follow-up Submissions

```text
COUNT of ControlStatus rows
WHERE active_action_id is populated
```

This represents the currently stored active Action state (`Open` or `In Progress`) projected onto the Submission.

It must not be described as a perfect inference of whether follow-up is still business-required because the current PoC does not automatically complete a missing-submission Action after later evidence intake.

### 13.3 Submissions with Reminder History

```text
COUNT of ControlStatus rows
WHERE reminder_count > 0
```

This is a historical process-activity measure and is distinct from current active follow-up state.

### 13.4 Average Reminders per Reminded Submission

```text
Total Automated Reminders
/
Submissions with Reminder History
```

If no Submission has reminder history in the filter context, the result is blank.

### Explicitly unsupported process KPI

Phase 8 must not claim an exact historical:

```text
Submissions that ever had an Action
```

because the curated contract does not expose an `action_count` or `has_ever_had_action` field. Completed Actions with zero reminder history are not guaranteed to be identifiable from the current curated schema.

Phase 8 will not change the upstream contract solely to manufacture this KPI.

## 14. Report Page Contract

Phase 8 will implement exactly three primary report pages.

### 14.1 Page 1 — Management Overview

Purpose:

```text
Provide a concise current governance view and surface material exceptions.
```

Required KPI cards:

```text
Controls in Scope
Assessed Compliance Rate
Non-Compliant Submissions
Overdue Submissions
High/Critical Exceptions
Total DQ Issues
```

Required analytical views should cover:

```text
Submission status distribution
Business Unit governance view
Risk-level exception view
```

Primary slicers:

```text
Business Unit
Risk Level
Reporting Period
```

This page must remain concise; it is not a dense operational table.

### 14.2 Page 2 — Control Monitoring

Purpose:

```text
Show where governance review or follow-up is required at Submission grain.
```

Required detail fields:

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

Primary slicers:

```text
Business Unit
Risk Level
Submission Status
Data Quality Status
Overdue
```

Conditional formatting may highlight risk and explicit exception dimensions, but it must not derive an unsupported combined `Overall Status`.

### 14.3 Page 3 — Process & Data Quality

Purpose:

```text
Separate data reliability from operational follow-up behavior while showing both in one analytical workspace.
```

Data Quality section:

```text
Total DQ Issues
DQ Issue Rate
High-Severity DQ Issues
DQ Issues by Rule
DQ Issues by Severity
DQ detail table
```

DQ detail fields:

```text
Submission ID
Control ID
Rule
Severity
Field
Message
```

Process section:

```text
Total Automated Reminders
Active Follow-up Submissions
Submissions with Reminder History
Late Submissions
Overdue Submission Rate
```

## 15. Canonical Acceptance Baseline

Before Phase 8 can be accepted, the canonical reporting output must remain reproducible from:

```bash
python src/main.py --as-of-date 2026-08-15
```

Canonical source/result baseline:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

Power BI acceptance must verify at minimum:

```text
ControlStatus rows           = 15
Valid Submissions            = 10
Invalid Submissions          = 5
Total DQ Issues              = 5
Controls in Scope            = 5
```

Known scenario checks:

```text
SUB-004
→ data_quality_status = Valid
→ submission_status = In Review
→ submission_late = True
→ days_late = 2

SUB-005
→ data_quality_status = Valid
→ submission_status = Non-Compliant
→ risk_level = High

SUB-014
→ data_quality_status = Valid
→ overdue_flag = True
→ days_overdue = 5
→ active Action state present in canonical fixture

SUB-002
→ DQ-004 Missing Evidence

SUB-006
→ DQ-003 Invalid Status

SUB-008 + SUB-009
→ DQ-005 Duplicate Submission

SUB-015
→ DQ-002 Unknown Control ID
→ unresolved Control enrichment remains visible
→ must not increase Controls in Scope to 6
```

The relationship to `DataQualityIssues` must not multiply `ControlStatus` rows or hide invalid source rows.

## 16. Operational Phase 7 Acceptance Dependency

After canonical Power BI acceptance, the same report must be capable of consuming a private processed output directory generated from one complete Phase 7 operational snapshot.

The already accepted Phase 7 snapshot baseline is:

```text
snapshot_id = 20260823_112030
as_of_date  = 2026-08-23
Controls    = 5
Submissions = 17
Actions     = 2
```

Python result:

```text
DQ issues           = 5
Valid submissions   = 12
Invalid submissions = 5
AI queue items      = 3
```

Accepted reminder-state examples:

```text
SUB-016
reminder_count   = 1
last_reminder_at = 2026-08-22

SUB-017
reminder_count   = 2
last_reminder_at = 2026-08-22
```

Phase 8 operational acceptance should prove that these processed reminder facts can be represented by the same semantic model and measures without changing the canonical repository fixtures.

The private snapshot and its private processed outputs remain outside GitHub.

## 17. Data-Root Configuration Requirement

The Power BI implementation should use one configurable root location for the curated Python outputs so the same report can point to:

```text
canonical generated data/curated
```

or:

```text
private processed Phase 7 output directory
```

without rewriting business logic or rebuilding the semantic model.

The exact Power BI parameter implementation is deferred to the build work package, but multiple independently hard-coded file paths are not the target design.

## 18. Privacy and Public Evidence Boundary

The public Power BI artifact and screenshots must not publish private operational identities or tenant metadata.

Private operational outputs can contain:

```text
owner_email
operational comments
operational state derived from authenticated source data
```

Public portfolio evidence should use the canonical synthetic dataset or sanitized evidence.

The following remain prohibited from public version control:

- private Phase 7 snapshots,
- private processed operational outputs,
- tenant/environment identifiers,
- reachable private e-mail addresses,
- credentials, tokens, or connection secrets.

## 19. Phase 8.0 Scope Exclusions

Phase 8.0 does not implement or require:

```text
Power BI report visuals
DAX measures
Power Query runtime queries
Power BI Service publication
Fabric workspaces
Fabric Git integration
deployment pipelines
gateways
scheduled Power BI Service refresh
row-level security
incremental refresh
DirectQuery
custom visuals
new Python business rules
new DQ rule IDs
new Action fields
snapshot discovery
manifest parsing
AI review UI
AI model invocation
REST API
Dataverse or database migration
automatic Action lifecycle repair
ROI or labour-savings estimates
```

Later Phase 8 work must not pull Phase 9 or Phase 10 capabilities forward merely because Power BI can technically connect to them.

## 20. Phase 8.0 Definition of Done

Phase 8.0 is complete when:

- [x] the two Power BI source files are fixed,
- [x] raw/operational direct-source access is excluded,
- [x] Submission reporting grain is fixed,
- [x] DQ issue grain is fixed,
- [x] the `source_row_number` relationship is fixed,
- [x] `submission_id` is rejected as the DQ relationship key,
- [x] Power Query responsibilities are bounded to technical ingestion,
- [x] null/unknown semantics are preserved,
- [x] Control-scope semantics exclude unresolved test references,
- [x] Governance KPI business definitions are fixed,
- [x] timeliness/exception KPI business definitions are fixed,
- [x] DQ KPI business definitions are fixed,
- [x] reminder/process KPI business definitions are fixed,
- [x] unsupported historical Action claims are identified,
- [x] the three report-page purposes and required content are fixed,
- [x] canonical dashboard acceptance expectations are fixed,
- [x] operational Phase 7 acceptance expectations are fixed,
- [x] privacy/public-evidence boundaries are fixed,
- [x] Phase 9/10 and production-platform scope is explicitly excluded.

**Phase 8.0 status: COMPLETE**

## 21. Next Work Package

The next implementation step is Phase 8.1:

```text
produce and verify the canonical curated reporting baseline
before creating the Power BI report artifact
```

Phase 8 as a whole remains **IN PROGRESS** until the Power BI artifact, semantic model, measures, three report pages, canonical acceptance, operational acceptance, documentation, screenshots, and final regression have been completed.

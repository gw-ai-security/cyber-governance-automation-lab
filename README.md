# Cyber Governance Automation Lab

**Security Control Evidence, Follow-up & Reporting Automation**

[![Python tests](https://github.com/gw-ai-security/cyber-governance-automation-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/gw-ai-security/cyber-governance-automation-lab/actions/workflows/tests.yml)

A portfolio proof of concept for a recurring cybersecurity-governance process. The project models expected control-evidence submissions, automates authenticated evidence intake, validates Data Quality deterministically, derives governance and timeliness metrics, tracks follow-up work, and prepares selected valid exceptions for controlled AI-assisted review.

The project is intentionally small and explicit. It demonstrates business-process understanding, data modeling, workflow automation, Python data processing, testing, governance controls, and reproducible engineering practices without presenting a proof of concept as a production platform.

## What This Project Demonstrates

- **Cybersecurity governance modeling** — Controls, recurring Submissions, follow-up Actions, reporting periods, deadlines, and human compliance review are separate business concepts.
- **Controlled evidence intake** — Microsoft Forms and Power Automate resolve an expected Submission by business key and update the existing operational record from `Not Submitted` to `In Review`.
- **Fail-safe workflow design** — missing targets, duplicate business keys, and invalid Submission states stop automated processing explicitly instead of being silently repaired or overwritten.
- **Deterministic Python processing** — canonical repository CSV/JSON inputs are structurally checked, normalized without semantic repair, validated, enriched, transformed, and serialized into contractual outputs.
- **Explicit Data Quality controls** — ten documented DQ rules cover completeness, referential integrity, validity, consistency, and uniqueness.
- **Engineering discipline** — critical business invariants are regression-tested and GitHub Actions runs the complete test suite on pull requests and pushes to `main`.
- **Controlled AI design** — only Data-Quality-valid governance exceptions enter the AI review queue; payloads are minimized and final compliance authority remains human.

## Current Engineering Evidence

| Evidence | Current state |
| --- | ---: |
| Security Controls | 5 |
| Canonical synthetic Submissions | 15 |
| Follow-up Actions | 5 |
| Explicit Submission DQ rules | 10 |
| Automated tests | **42 passing** |
| Canonical DQ findings | 5 |
| Valid / invalid Submissions | 10 / 5 |
| Raw / curated Submission rows | 15 / 15 |
| AI review queue items | 2 |
| Contractual pipeline outputs | 3 |
| Power Automate evidence-intake workflow | Implemented and acceptance-tested |
| Evidence-intake failure codes | 3 |
| Continuous Integration | GitHub Actions |
| Required CI merge gate | **Not currently enforced** |

The deterministic Python acceptance run uses:

```text
as_of_date = 2026-08-15
```

and must produce:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

## Architecture

The project currently has two deliberately distinct data planes:

1. **Operational Phase 5 intake PoC** — Microsoft Forms → Power Automate → Excel Online / OneDrive.
2. **Deterministic repository pipeline** — canonical synthetic CSV/JSON files → Python ETL + Data Quality.

They are **not automatically synchronized** in Phase 5.

```mermaid
flowchart TD
    subgraph OP[Operational Evidence Intake — Phase 5]
        A[Microsoft Forms<br/>IMPLEMENTED] --> B[Power Automate Evidence Intake<br/>IMPLEMENTED]
        B --> C[Excel Online / OneDrive Submission Register<br/>IMPLEMENTED PoC]
    end

    subgraph REPO[Deterministic Repository Data Layer — Phases 2–4]
        D[Canonical Raw Submission CSV] --> F[Python ETL + Data Quality<br/>IMPLEMENTED]
        E[Control Catalog JSON] --> F
        G[Action CSV] --> F
        F --> H[Curated Control Status CSV]
        F --> I[Data Quality Issues CSV]
        F --> J[AI Review Queue JSON]
    end

    C -. Phase 7 reporting snapshot/export<br/>PLANNED; not automated in Phase 5 .-> S[security_control_snapshot.csv<br/>PLANNED]
    S -. future integration adapter .-> F

    H --> K[Power BI Governance Dashboard<br/>PLANNED]
    J --> L[Controlled AI Runtime<br/>PLANNED]
    L --> M[Human Governance Review<br/>PLANNED]
    N[Scheduled Reminder Flow<br/>PHASE 6 PLANNED] --> C
```

The live Excel register used for Phase 5 acceptance is an operational Microsoft 365 artifact. It does **not** overwrite `data/raw/evidence_submissions.csv`. The repository raw dataset intentionally remains the deterministic Phase 2–4 acceptance baseline.

See [docs/architecture.md](docs/architecture.md) and [docs/power_automate.md](docs/power_automate.md).

## Current Implementation Status

| Phase | Scope | Status |
| --- | --- | --- |
| Phase 0 | Repository & Project Foundation | ✅ Complete |
| Phase 1 | Business Process & Data Model | ✅ Complete |
| Phase 2 | Synthetic Dataset | ✅ Complete |
| Phase 3 | Python Data Quality Pipeline | ✅ Complete |
| Phase 4 | Test Hardening & Acceptance | ✅ Complete |
| Repository CI | GitHub Actions | ✅ Active |
| Repository merge gating | Required CI check before merge | ⚠ Not currently enforced |
| Phase 5 | Power Automate Evidence Flow | ✅ Core DoD complete; see roadmap delta below |
| Phase 6 | Reminder Automation | ▶ Next |
| Phase 7 | Reporting Export | ○ Planned |
| Phase 8 | Power BI Dashboard | ○ Planned |
| Phase 9 | Controlled AI Workflow | ○ Planned |
| Phase 10 | REST API | ○ Planned |
| Phase 11 | Documentation & Handover | ○ Planned |

### Phase 5 roadmap delta

The original project roadmap illustrated a separate **Confirmation Email** after a successful evidence submission. The implemented Phase 5 flow does not contain a custom confirmation-email action. The core Phase 5 Definition of Done — a Forms submission deterministically updating the expected Control Register record with validation and error handling — is implemented and acceptance-tested. The missing custom confirmation email is documented rather than falsely presented as implemented.

## Core Domain Model

The logical model contains exactly four core entities:

```text
CONTROL
   │ 1:n
   ▼
SUBMISSION
   ├──────────────► ACTION
   └──────────────► DATA QUALITY ISSUE
```

A Submission represents one expected assessment of a Control for one reporting period.

Technical identifier:

```text
submission_id
```

Business identity:

```text
control_id + reporting_period
```

Expected Submission records exist before evidence arrives so missing submissions can be detected explicitly.

Critical semantics are preserved throughout the project:

```text
Evidence Present != Compliant
Not Submitted != Non-Compliant
Non-Compliant != Overdue
Compliance != Timeliness
Compliance != Data Quality
Submission Status != Action Status
Unknown != False
Not Evaluated != Failed
```

## Phase 5: Controlled Evidence Intake

The implemented workflow is:

```text
Microsoft Forms
      ↓
Get Response Details
      ↓
Read Submission Register
      ↓
Filter by control_id
      ↓
Filter by reporting_period
      ↓
Require exactly one business-key match
      ↓
Require status = Not Submitted
      ↓
Update existing row by submission_id
      ↓
status = In Review
```

The workflow deliberately performs **UPDATE, not APPEND**.

The Control Owner supplies evidence but does not choose compliance status. The workflow only performs:

```text
Not Submitted → In Review
```

Final `Compliant` / `Non-Compliant` assessment remains a Governance Reviewer decision.

Three explicit failure paths are implemented and acceptance-tested:

| Code | Condition |
| --- | --- |
| `NO_MATCH` | No expected Submission exists for the submitted business key |
| `DUPLICATE_BUSINESS_KEY` | More than one Submission exists for the business key |
| `INVALID_SUBMISSION_STATE` | A unique Submission exists but is not `Not Submitted` |

See [docs/power_automate.md](docs/power_automate.md) for the complete workflow contract, expressions, screenshots, and acceptance evidence.

## Python Pipeline

Phase 3 implements:

```text
EXTRACT
   ↓
NORMALIZE
   ↓
VALIDATE
   ↓
TRANSFORM / ENRICH
   ↓
DERIVE
   ↓
LOAD
```

Normalization standardizes technical representation but does not silently repair business meaning. Submission rows are enriched with Control metadata using a `LEFT JOIN`; invalid rows remain visible, and Action aggregation preserves one row per raw Submission.

Derived fields include:

- `evidence_present`
- `overdue_flag`
- `submission_late`
- `days_overdue`
- `days_late`
- `data_quality_status`
- active Action context
- reminder metrics

See [docs/phase3_pipeline_contract.md](docs/phase3_pipeline_contract.md).

## Data Quality

The project applies exactly DQ-001 through DQ-010:

| Rule | Name | Category | Severity |
| --- | --- | --- | --- |
| DQ-001 | Missing Required Field | Completeness | High |
| DQ-002 | Unknown Control ID | Referential Integrity | High |
| DQ-003 | Invalid Status | Validity | High |
| DQ-004 | Missing Evidence | Consistency | High |
| DQ-005 | Duplicate Submission | Uniqueness | High |
| DQ-006 | Invalid Reporting Period | Validity | Medium |
| DQ-007 | Invalid Due Date | Validity | High |
| DQ-008 | Invalid Submission State | Consistency | High |
| DQ-009 | Invalid Evidence State | Consistency | Medium |
| DQ-010 | Invalid Submitter Email | Validity | Medium |

Invalid rows and duplicate business keys are preserved for traceability rather than silently deleted or repaired.

Canonical invariant:

```text
15 raw Submission rows → 15 curated Submission rows
```

See [docs/data_quality.md](docs/data_quality.md) and [docs/phase2_dataset_coverage.md](docs/phase2_dataset_coverage.md).

## Testing and Repository Governance

The Phase 4 acceptance baseline contains **42 passing automated tests** covering input contracts, DQ rules, validation dependencies, duplicates, lineage, deterministic issue IDs, enrichment behavior, timing boundaries, AI queue eligibility, serialization, CLI handling, and end-to-end acceptance counts.

GitHub Actions runs:

```bash
python -m pytest -q
```

for pull requests against `main` and pushes to `main`.

The Phase 5 pull request CI run also completed successfully with:

```text
42 passed
```

However, the current GitHub configuration does **not** enforce completion of that check as a merge gate. PR #8 was merged before its successful CI run finished. CI is therefore active and useful, but required-check enforcement must be restored in GitHub repository rules/settings if merge gating is intended.

Phase 5 was additionally acceptance-tested through Microsoft Forms submissions and Power Automate run history for:

- successful evidence intake,
- resubmission / invalid state,
- zero business-key matches,
- duplicate business-key matches.

## Controlled AI Review Queue

A Submission is eligible only when:

```text
data_quality_status = Valid
AND
(
    submission_status = Non-Compliant
    OR
    overdue_flag = True
)
```

DQ-invalid records remain in deterministic Data Quality / human-correction workflows. External model invocation is a later phase and final compliance authority remains human.

## Tech Stack

| Technology | Role |
| --- | --- |
| Microsoft Forms | Authenticated evidence intake |
| Power Automate | Evidence-intake orchestration and guardrails |
| Excel Online / OneDrive | Operational Submission Register for the PoC |
| Python 3.14.5 | Pipeline orchestration and business rules |
| pandas | Transformation and enrichment |
| pytest | Automated testing |
| CSV / JSON | Contractual repository inputs and outputs |
| GitHub Actions | Continuous Integration |
| Git / GitHub | Version control and repository workflow |

`requests`, `FastAPI`, and `uvicorn` are already present in `requirements.txt` for later integration/API phases; they are not evidence that Phase 10 is implemented.

## How to Run

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python src/main.py --as-of-date 2026-08-15
```

Successful pipeline execution writes runtime artifacts to `data/curated/`.

## Repository Guide

| Document | Purpose |
| --- | --- |
| [docs/architecture.md](docs/architecture.md) | Current architecture, data-plane boundaries, and component responsibilities |
| [docs/business_process.md](docs/business_process.md) | Governance process and role semantics |
| [docs/data_model.md](docs/data_model.md) | Logical domain model |
| [docs/data_contract.md](docs/data_contract.md) | Physical raw CSV contracts |
| [docs/data_quality.md](docs/data_quality.md) | DQ-001 through DQ-010 |
| [docs/phase2_dataset_coverage.md](docs/phase2_dataset_coverage.md) | Synthetic scenario coverage |
| [docs/phase3_pipeline_contract.md](docs/phase3_pipeline_contract.md) | Python pipeline contract |
| [docs/phase4_test_acceptance.md](docs/phase4_test_acceptance.md) | Regression hardening and acceptance |
| [docs/power_automate.md](docs/power_automate.md) | Phase 5 workflow, expressions, guardrails, screenshots, and acceptance tests |

## Security and Governance Considerations

- repository business records and identities are synthetic,
- the operational Microsoft 365 workbook is not a repository source artifact,
- actual evidence files are not stored in the repository,
- credentials, tokens, keys, and secrets must not be committed,
- evidence intake is authenticated in the Microsoft 365 PoC,
- evidence submission cannot assign compliance,
- ambiguous or invalid-state workflow targets fail safely,
- DQ-invalid records do not enter the AI review queue,
- AI payloads are minimized,
- final governance review remains human-controlled.

Screenshots committed as Phase 5 evidence are sanitized where necessary so authenticated test-account identifiers are not published.

## Limitations

This repository is a **portfolio proof of concept**, not a production cybersecurity-governance platform.

Current limitations include:

- Excel/OneDrive rather than a transactional production datastore,
- no automatic Phase 5 Excel → repository raw-CSV synchronization,
- no production IAM/RBAC or audit-trail service,
- no automated reporting-period generation,
- no custom Phase 5 confirmation email,
- no scheduled reminder workflow yet,
- no Power BI report artifact yet,
- no external AI model invocation,
- no REST API implementation,
- no enforced required CI status check before merge at the current repository configuration.

For production, Dataverse, SharePoint Lists, or a relational database would generally be preferable where stronger concurrency, governance, auditability, and scale are required.

## Source of Truth

Historical phase documents remain valid for the phase they describe. Current repository documentation, canonical datasets, implementation code, automated tests, and implemented workflow acceptance evidence define the current project state. Later implementation must not retroactively rewrite historical acceptance records merely to make them read like current-state documentation.

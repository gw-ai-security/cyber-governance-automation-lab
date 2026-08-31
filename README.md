# Cyber Governance Automation Lab

**Security Control Evidence · Workflow Automation · Deterministic Data Quality · Power BI · Controlled AI Review · Read-only REST Integration**

[![Python tests](https://github.com/gw-ai-security/cyber-governance-automation-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/gw-ai-security/cyber-governance-automation-lab/actions/workflows/tests.yml)

A completed **11-phase portfolio proof of concept** for recurring cybersecurity-control evidence, follow-up, reporting, controlled AI-assisted review and minimized read-only integration.

> **10-second summary:** Microsoft 365 workflows collect and follow up evidence, a deterministic Python pipeline validates and curates it, Power BI reports it, a minimized queue feeds controlled AI review, and a local FastAPI boundary exposes only selected read-only data. **84 automated tests pass in the final accepted baseline.**

> **Scope boundary:** this is a PoC, not a production compliance platform. Evidence presence, compliance, timeliness, workflow state, Data Quality, AI advice and API exposure remain separate concepts, and final governance authority remains human.

## Architecture

```text
Microsoft Forms
      ↓
Power Automate evidence intake
      ↓
SubmissionRegister

Scheduled reminder flow
      ↓
ControlCatalog + SubmissionRegister + ActionRegister
      ↓
Private snapshot package
      ↓
Deterministic Python pipeline
      ├────────────→ curated reporting → Power BI
      └────────────→ minimized AI queue → controlled AI review
                                      ↓
                              schema + correlation validation
                                      ↓
                              Human Governance Review

Canonical Control Catalog
      ↓
Local read-only FastAPI service
      ↓
Python client
```

The core authority model is explicit:

```text
Evidence intake != compliance decision
Data Quality     != compliance decision
AI output        != compliance decision
REST response    != governance authority
```

## Recruiter Snapshot

| Area | Implemented evidence |
|---|---|
| **Workflow / Connect** | Microsoft Forms + Power Automate evidence intake and scheduled reminders |
| **Operational state** | Control, Submission and Action registers with explicit business keys and state handling |
| **Processing** | deterministic Python extract → normalize → validate → transform/enrich → derive → load pipeline |
| **Data Quality** | exactly **10 Submission DQ rules** (`DQ-001`–`DQ-010`) |
| **Reporting** | source-controlled Power BI PBIP/PBIR/TMDL project with **21 DAX measures** and 3 primary pages |
| **AI review** | deterministic candidate selection, minimized queue, JSON Schema output contract, correlation validation, mandatory human review |
| **API** | local read-only FastAPI service with 2 business GET endpoints |
| **Testing / CI** | **84 automated tests**, locked Python environment, GitHub Actions |
| **Security / Governance** | explicit trust boundaries, minimized public fields, Security Considerations and PoC-to-production gap assessment |

## Final Accepted Baseline

Canonical acceptance uses:

```text
as_of_date = 2026-08-15
```

Expected deterministic result:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

Canonical AI candidates:

```text
SUB-005
SUB-014
```

Final functional baseline:

```text
84 passed
```

## Core Domain Model

Exactly four core business entities are modeled:

```text
CONTROL
   │ 1:n
   ▼
SUBMISSION
   ├──────────────► ACTION
   └──────────────► DATA QUALITY ISSUE
```

Primary reporting grain: **Submission**.

Critical semantic separations include:

```text
Evidence Present != Compliant
Not Submitted     != Non-Compliant
Non-Compliant     != Overdue
Compliance        != Timeliness
Compliance        != Data Quality
Submission Status != Action Status
Schema-valid      != factually correct
AI recommendation != governance authority
```

These distinctions are deliberate because collapsing them into a single status would make the system easier to demo but less trustworthy.

## Data Quality

Submission DQ remains exactly:

| Rule | Name | Severity |
|---|---|---|
| DQ-001 | Missing Required Field | High |
| DQ-002 | Unknown Control ID | High |
| DQ-003 | Invalid Status | High |
| DQ-004 | Missing Evidence | High |
| DQ-005 | Duplicate Submission | High |
| DQ-006 | Invalid Reporting Period | Medium |
| DQ-007 | Invalid Due Date | High |
| DQ-008 | Invalid Submission State | High |
| DQ-009 | Invalid Evidence State | Medium |
| DQ-010 | Invalid Submitter Email | Medium |

Workflow errors and API/client failures are not silently reclassified as Data Quality findings.

## Dashboard Evidence

All public dashboard images use canonical synthetic data.

### Management Overview

![Management Overview](docs/images/phase8/management-overview.webp)

### Control Monitoring

![Control Monitoring](docs/images/phase8/control-monitoring.webp)

### Process & Data Quality

![Process & Data Quality](docs/images/phase8/process-data-quality.webp)

Power BI consumes only Python-owned curated outputs:

```text
curated_control_status.csv
data_quality_issues.csv
```

## Controlled AI Review

Eligibility is deterministic:

```text
data_quality_status = Valid
AND
(
    submission_status = Non-Compliant
    OR
    overdue_flag = True
)
```

The queue excludes selected identity/evidence-reference fields including `owner_email`, `submitted_by` and `evidence_reference`.

AI output must pass:

1. JSON Schema validation,
2. Submission/Control correlation validation,
3. mandatory human Governance Review.

The project does **not** claim universal prompt-injection resistance, an external AI-provider runtime, autonomous governance decisions or automatic write-back.

## Local Read-only REST Boundary

Business endpoints:

```text
GET /api/v1/controls
GET /api/v1/controls/{control_id}
```

Public representation is intentionally minimized to:

```text
control_id
risk_level
```

Accepted failure contracts:

```text
unknown Control -> 404 CONTROL_NOT_FOUND
source failure   -> 500 CONTROL_SOURCE_ERROR
```

The runtime target is loopback only. Production authentication, authorization, gateway controls, rate limiting and telemetry are explicit production gaps rather than hidden omissions.

## Engineering Lessons and Trade-offs

This project was designed to expose failure modes rather than optimize for a clean demo.

- **Expected-state modeling matters.** Missing evidence must be observable; absence of a row is not enough.
- **Business keys and state transitions must be guarded.** Intake updates an expected Submission instead of blindly appending a new record.
- **Idempotency matters in reminders.** The workflow distinguishes create, reuse and duplicate-active-Action conditions.
- **Reporting grain must survive enrichment.** Control enrichment uses a `LEFT JOIN`, invalid submissions stay visible, and Action aggregation must not multiply Submission rows.
- **AI must remain downstream of deterministic checks.** Invalid data is excluded before AI review, and schema-valid output is still not treated as factually correct.
- **Auditability is not the same as compliance.** Logs, DQ results, workflow states and recommendations are evidence inputs, not legal determinations.
- **Production readiness requires more than a working PoC.** The repository explicitly records missing IAM/RBAC/DLP, transactional guarantees, production monitoring, deployment controls and external-provider integration.

The detailed implementation history, phase acceptance records and production-gap analysis remain in [`docs/`](docs/README.md).

## Run the Project

Accepted Python runtime:

```text
Python 3.14.5
```

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pytest -q
python src/main.py --as-of-date 2026-08-15
```

Local API:

```bash
python -m uvicorn api.mock_api:app --host 127.0.0.1 --port 8000
```

Detailed operating instructions: [`docs/handover.md`](docs/handover.md).

## Tech Stack

**Connect / Workflow:** Microsoft Forms · Power Automate · Office 365 Outlook  
**Operational storage:** Excel Online / OneDrive PoC state and private snapshots  
**Processing:** Python · pandas  
**Reporting:** Power BI · Power Query · DAX · PBIP/PBIR/TMDL  
**AI contract:** JSON Schema · deterministic queue selection · human review  
**API:** FastAPI · Uvicorn · requests  
**Quality / Delivery:** pytest · GitHub Actions · locked dependencies · Git/GitHub

## Production Boundaries

Key accepted limitations include:

- Excel/OneDrive rather than a transactional production datastore
- no transactional multi-table snapshot guarantee
- no production scheduling/orchestration of the Python pipeline
- no production IAM/RBAC/DLP/audit/retention/monitoring architecture
- no Power BI Service/Fabric enterprise deployment or RLS architecture
- no external AI-provider runtime or AI write-back
- no production API authentication/authorization/gateway/rate limiting/telemetry
- no enforced required CI status check before merge

Full assessment: [`docs/production_gap_assessment.md`](docs/production_gap_assessment.md).

## Suggested Review Path

1. [`docs/evidence.md`](docs/evidence.md) — curated engineering evidence
2. [`docs/architecture.md`](docs/architecture.md) — final implemented architecture
3. [`docs/data_quality.md`](docs/data_quality.md) — DQ rule contract
4. [`docs/security_considerations.md`](docs/security_considerations.md) — trust/security boundaries
5. [`docs/production_gap_assessment.md`](docs/production_gap_assessment.md) — explicit PoC-to-production gaps
6. [`docs/handover.md`](docs/handover.md) — reproducible technical runbook

## TL;DR

The strongest signal in this project is not "AI governance" as a label. It is the engineering discipline behind it: **explicit domain semantics, expected-state modeling, deterministic Data Quality, idempotent workflows, controlled analytical grain, bounded AI use, human authority, automated tests and documented production gaps**.

# Documentation Index

## Purpose

This index makes the Cyber Governance Automation Lab documentation easy to navigate by **document role**, **phase/work package**, and **current vs. historical status**.

The repository uses two documentation classes:

1. **Current-state foundation documents** — authoritative descriptions of the present implementation.
2. **Phase-specific records** — contracts, implementation plans, work-package evidence, and acceptance records retained for traceability.

Historical documents are not rewritten merely because later phases changed the current architecture. The current state is defined by implementation code, canonical data, tests, the foundation documents below, and the latest phase acceptance record.

## 1. Current-State Foundation Documents

| Document | Role | Current status |
| --- | --- | --- |
| [architecture.md](architecture.md) | System architecture, component responsibilities, integration/security boundaries | Current through Phase 10 |
| [business_process.md](business_process.md) | Governance process semantics and lifecycle boundaries | Current through Phase 10 |
| [data_model.md](data_model.md) | Four-entity logical data model and derived-state semantics | Current through Phase 10 |
| [data_contract.md](data_contract.md) | Canonical and operational physical data contracts | Current |
| [data_quality.md](data_quality.md) | DQ-001 through DQ-010 | Current |
| [repository_conventions.md](repository_conventions.md) | Repository/documentation naming, status, privacy, and source-of-truth conventions | Current through Phase 10 |

## 2. Phase-Specific Documentation

### Phase 2 — Canonical Synthetic Dataset

| Work package / role | Document | Status |
| --- | --- | --- |
| Phase 2 dataset coverage and acceptance matrix | [phase2_dataset_coverage.md](phase2_dataset_coverage.md) | Historical acceptance evidence; still canonical |

### Phase 3 — Deterministic Python Data Quality Pipeline

| Work package / role | Document | Status |
| --- | --- | --- |
| Phase 3 implementation contract | [phase3_pipeline_contract.md](phase3_pipeline_contract.md) | Historical contract; implementation remains active |

### Phase 4 — Test Hardening & Acceptance

| Work package / role | Document | Status |
| --- | --- | --- |
| Phase 4 regression/test acceptance | [phase4_test_acceptance.md](phase4_test_acceptance.md) | Historical acceptance record |

### Phase 5 — Power Automate Evidence Intake

| Work package / role | Document | Status |
| --- | --- | --- |
| Phase 5 implementation + acceptance | [phase5_evidence_intake.md](phase5_evidence_intake.md) | Implemented and acceptance-tested |

### Phase 6 — Scheduled Reminder Automation

| Work package / role | Document | Status |
| --- | --- | --- |
| Phase 6 implementation + acceptance | [phase6_reminder_automation.md](phase6_reminder_automation.md) | Implemented and acceptance-tested |

### Phase 7 — Reporting Snapshot Bridge

| Work package / role | Document | Status |
| --- | --- | --- |
| Phase 7.0 reporting export contract | [phase7_reporting_export.md](phase7_reporting_export.md) | Contract / implemented |
| Phase 7.1 implementation preparation | [phase7_implementation_plan.md](phase7_implementation_plan.md) | Historical implementation plan |
| Phase 7.2 Power Automate runtime acceptance | [phase7_power_automate_acceptance.md](phase7_power_automate_acceptance.md) | Acceptance record |
| Phase 7.3 Python external-input boundary | [phase7_python_external_input.md](phase7_python_external_input.md) | Implemented / acceptance evidence |
| Phase 7 final end-to-end acceptance | [phase7_end_to_end_acceptance.md](phase7_end_to_end_acceptance.md) | Final Phase 7 acceptance |

### Phase 8 — Power BI Dashboard

| Work package / role | Document | Status |
| --- | --- | --- |
| Phase 8.0 reporting/KPI contract | [phase8_power_bi_contract.md](phase8_power_bi_contract.md) | Contract / implemented |
| Phase 8.1 canonical reporting baseline | [phase8_canonical_baseline.md](phase8_canonical_baseline.md) | Baseline evidence |
| Phase 8.2 PBIP/PBIR/TMDL project scaffold | [phase8_power_bi_project.md](phase8_power_bi_project.md) | Implementation evidence |
| Phase 8.3 curated loading and typing | [phase8_curated_loading.md](phase8_curated_loading.md) | Implementation evidence |
| Phase 8.4 semantic relationship | [phase8_semantic_model.md](phase8_semantic_model.md) | Implementation evidence |
| Phase 8.5 DAX measures | [phase8_measures.md](phase8_measures.md) | Implementation evidence |
| Phase 8.6 Management Overview | [phase8_management_overview.md](phase8_management_overview.md) | Page acceptance evidence |
| Phase 8.7 Control Monitoring | [phase8_control_monitoring.md](phase8_control_monitoring.md) | Page acceptance evidence |
| Phase 8.8 Process & Data Quality | [phase8_process_data_quality.md](phase8_process_data_quality.md) | Page acceptance evidence |
| Phase 8.9 canonical runtime acceptance | [phase8_canonical_acceptance.md](phase8_canonical_acceptance.md) | Acceptance record |
| Phase 8.10 operational Phase 7 runtime acceptance | [phase8_operational_acceptance.md](phase8_operational_acceptance.md) | Acceptance record |
| Phase 8.11 consistency review | [phase8_consistency_review.md](phase8_consistency_review.md) | Closure review |
| Phase 8.11 final acceptance | [phase8_final_acceptance.md](phase8_final_acceptance.md) | Final Phase 8 acceptance |

### Phase 9 — Controlled AI Workflow

| Work package / role | Document | Status |
| --- | --- | --- |
| Phase 9.0 AI governance/trust/authority contract | [phase9_ai_workflow_contract.md](phase9_ai_workflow_contract.md) | Frozen/implemented contract |
| Phase 9.1 structured output contract | [phase9_ai_output_contract.md](phase9_ai_output_contract.md) | Frozen/implemented contract |
| Phase 9.7 human-review procedure | [phase9_human_review.md](phase9_human_review.md) | Current procedure for Phase 9 artifacts |
| Phase 9.7 human acceptance | [phase9_human_acceptance.md](phase9_human_acceptance.md) | Acceptance record |
| Phase 9.8–9.9 implementation/final acceptance | [phase9_ai_acceptance.md](phase9_ai_acceptance.md) | Final Phase 9 acceptance |

Phase 9.2–9.6 implementation evidence also lives directly in version-controlled artifacts under `ai/`, `src/ai_validation.py`, and the automated tests rather than one Markdown file per work package.

### Phase 10 — REST API

| Work package / role | Document | Status |
| --- | --- | --- |
| Phase 10.0 REST API contract freeze | [phase10_rest_api_contract.md](phase10_rest_api_contract.md) | Frozen historical design contract |
| Phase 10.1–10.10 implementation + acceptance | [phase10_rest_api_acceptance.md](phase10_rest_api_acceptance.md) | Final implementation/acceptance record |

The frozen Phase 10.0 contract deliberately retains its original pre-implementation language. The acceptance record is the authoritative description of what was actually implemented and tested.

## 3. Public Evidence Assets

### Curated portfolio images

```text
docs/images/phase8/
```

Contains the three canonical Power BI dashboard images embedded in the root README.

### Runtime / workflow screenshot evidence

```text
docs/screenshots/phase-5-evidence-intake/
docs/screenshots/phase-6-reminder-automation/
docs/screenshots/phase-7-reporting-export/
```

These directories contain sanitized public acceptance evidence only. Private operational screenshots and tenant-specific artifacts are not required in Git.

## 4. Naming Convention

Foundation documents use stable descriptive names:

```text
architecture.md
business_process.md
data_model.md
data_contract.md
data_quality.md
repository_conventions.md
```

Phase-specific documents use:

```text
phase<N>_<scope>.md
```

Role-oriented suffixes are preferred where useful:

```text
_contract       pre-implementation/frozen contract
_plan           implementation plan
_acceptance     acceptance evidence
_final_acceptance final phase closure record
```

Existing historical file names are retained when renaming would break traceability or links. This index provides the normalized phase/work-package mapping instead of rewriting repository history.

## 5. Source-of-Truth Order

For questions about the **current implementation**, use:

```text
implemented code + canonical data + automated tests
        ↓
current-state foundation documents
        ↓
latest phase implementation/acceptance record
        ↓
frozen contracts and historical plans
```

For questions about **what was planned or accepted at a specific phase**, use the relevant phase-specific record and preserve its historical context.

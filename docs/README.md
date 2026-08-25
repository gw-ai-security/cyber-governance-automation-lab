# Documentation Index

## Purpose

This index is the navigation layer for the completed Cyber Governance Automation Lab. It distinguishes current-state foundation documents, Phase 11 handover material, and historical phase-specific records.

The source-of-truth order for the present implementation is:

```text
implemented code + canonical data + automated tests
        ↓
current-state foundation documents
        ↓
Phase 11 handover/final acceptance
        ↓
historical phase contracts, plans, and acceptance records
```

Historical files are retained for traceability and are not rewritten merely because later phases changed the project.

## 1. Current-State Foundation Documents

| Document | Role | Status |
| --- | --- | --- |
| [architecture.md](architecture.md) | System architecture, component responsibilities, trust/integration boundaries | Current semantic/runtime architecture through Phase 10; unchanged by documentation-only Phase 11 |
| [business_process.md](business_process.md) | Governance-process semantics and lifecycle boundaries | Current semantic process through Phase 10; unchanged by documentation-only Phase 11 |
| [data_model.md](data_model.md) | Four-entity logical data model and derived-state semantics | Current |
| [data_contract.md](data_contract.md) | Canonical, operational, generated, snapshot, and REST physical contracts | Current |
| [data_quality.md](data_quality.md) | Submission DQ-001 through DQ-010 | Current |
| [repository_conventions.md](repository_conventions.md) | Naming, status, dependency, privacy, evidence, and source-of-truth conventions | Current Phase 11 handover |

Phase 11 adds no new business entity, status transition, DQ rule, Power BI measure, AI authority, or REST endpoint. The Phase 10 runtime architecture therefore remains the final implemented runtime architecture.

## 2. Phase 11 — Final Documentation & Handover

| Work package / role | Document / artifact | Status |
| --- | --- | --- |
| Consolidated security/privacy/trust boundary | [security_considerations.md](security_considerations.md) | Current |
| PoC-to-production gap analysis | [production_gap_assessment.md](production_gap_assessment.md) | Current |
| Technical setup/operation handover | [handover.md](handover.md) | Current |
| Curated public evidence navigation | [evidence.md](evidence.md) | Current |
| Final handover acceptance | [phase11_handover_acceptance.md](phase11_handover_acceptance.md) | Final acceptance record |
| Reproducible Python dependency set | [`../requirements-lock.txt`](../requirements-lock.txt) | Current accepted environment |

## 3. Phase-Specific Historical Documentation

### Phase 2 — Canonical Synthetic Dataset

| Work package / role | Document | Status |
| --- | --- | --- |
| Dataset coverage and acceptance matrix | [phase2_dataset_coverage.md](phase2_dataset_coverage.md) | Historical acceptance evidence; dataset remains canonical |

### Phase 3 — Deterministic Python Data Quality Pipeline

| Work package / role | Document | Status |
| --- | --- | --- |
| Pipeline implementation contract | [phase3_pipeline_contract.md](phase3_pipeline_contract.md) | Historical contract; implementation remains active |

### Phase 4 — Test Hardening & Acceptance

| Work package / role | Document | Status |
| --- | --- | --- |
| Regression/test acceptance | [phase4_test_acceptance.md](phase4_test_acceptance.md) | Historical acceptance record |

### Phase 5 — Power Automate Evidence Intake

| Work package / role | Document | Status |
| --- | --- | --- |
| Implementation + acceptance | [phase5_evidence_intake.md](phase5_evidence_intake.md) | Implemented and acceptance-tested |

### Phase 6 — Scheduled Reminder Automation

| Work package / role | Document | Status |
| --- | --- | --- |
| Implementation + acceptance | [phase6_reminder_automation.md](phase6_reminder_automation.md) | Implemented and acceptance-tested |

### Phase 7 — Reporting Snapshot Bridge

| Work package / role | Document | Status |
| --- | --- | --- |
| Reporting export contract | [phase7_reporting_export.md](phase7_reporting_export.md) | Historical contract / implemented |
| Implementation preparation | [phase7_implementation_plan.md](phase7_implementation_plan.md) | Historical plan |
| Power Automate runtime acceptance | [phase7_power_automate_acceptance.md](phase7_power_automate_acceptance.md) | Acceptance record |
| Python external-input boundary | [phase7_python_external_input.md](phase7_python_external_input.md) | Implemented / acceptance evidence |
| Final end-to-end acceptance | [phase7_end_to_end_acceptance.md](phase7_end_to_end_acceptance.md) | Final Phase 7 acceptance |

### Phase 8 — Power BI Dashboard

| Work package / role | Document | Status |
| --- | --- | --- |
| Reporting/KPI contract | [phase8_power_bi_contract.md](phase8_power_bi_contract.md) | Historical contract / implemented |
| Canonical reporting baseline | [phase8_canonical_baseline.md](phase8_canonical_baseline.md) | Baseline evidence |
| PBIP/PBIR/TMDL project scaffold | [phase8_power_bi_project.md](phase8_power_bi_project.md) | Implementation evidence |
| Curated loading and typing | [phase8_curated_loading.md](phase8_curated_loading.md) | Implementation evidence |
| Semantic relationship | [phase8_semantic_model.md](phase8_semantic_model.md) | Implementation evidence |
| DAX measures | [phase8_measures.md](phase8_measures.md) | Implementation evidence |
| Management Overview | [phase8_management_overview.md](phase8_management_overview.md) | Page acceptance evidence |
| Control Monitoring | [phase8_control_monitoring.md](phase8_control_monitoring.md) | Page acceptance evidence |
| Process & Data Quality | [phase8_process_data_quality.md](phase8_process_data_quality.md) | Page acceptance evidence |
| Canonical runtime acceptance | [phase8_canonical_acceptance.md](phase8_canonical_acceptance.md) | Acceptance record |
| Operational Phase 7 runtime acceptance | [phase8_operational_acceptance.md](phase8_operational_acceptance.md) | Acceptance record |
| Consistency review | [phase8_consistency_review.md](phase8_consistency_review.md) | Closure review |
| Final acceptance | [phase8_final_acceptance.md](phase8_final_acceptance.md) | Final Phase 8 acceptance |

### Phase 9 — Controlled AI Workflow

| Work package / role | Document | Status |
| --- | --- | --- |
| AI governance/trust/authority contract | [phase9_ai_workflow_contract.md](phase9_ai_workflow_contract.md) | Frozen/implemented contract |
| Structured output contract | [phase9_ai_output_contract.md](phase9_ai_output_contract.md) | Frozen/implemented contract |
| Human-review procedure | [phase9_human_review.md](phase9_human_review.md) | Current procedure for Phase 9 artifacts |
| Human acceptance | [phase9_human_acceptance.md](phase9_human_acceptance.md) | Acceptance record |
| Implementation/final acceptance | [phase9_ai_acceptance.md](phase9_ai_acceptance.md) | Final Phase 9 acceptance |

Phase 9.2–9.6 implementation evidence also lives directly in `ai/`, `src/ai_validation.py`, and the automated tests.

### Phase 10 — Local Read-only REST API Integration

| Work package / role | Document | Status |
| --- | --- | --- |
| REST API contract freeze | [phase10_rest_api_contract.md](phase10_rest_api_contract.md) | Frozen Phase 10.0 design contract |
| Implementation + acceptance | [phase10_rest_api_acceptance.md](phase10_rest_api_acceptance.md) | Final Phase 10 implementation/acceptance record |

The frozen Phase 10.0 contract retains its pre-implementation language. The acceptance record describes what was actually implemented and tested.

## 4. Public Evidence Assets

### Curated Power BI images

```text
docs/images/phase8/
```

Contains the three canonical dashboard images used in the root README.

### Sanitized workflow screenshots

```text
docs/screenshots/phase-5-evidence-intake/
docs/screenshots/phase-6-reminder-automation/
docs/screenshots/phase-7-reporting-export/
```

### Curated cross-phase evidence navigation

See [evidence.md](evidence.md).

Private operational screenshots, live workbooks, tenant identifiers, and reachable identities are not required in public Git.

## 5. Naming Convention

Foundation documents use stable descriptive names:

```text
architecture.md
business_process.md
data_model.md
data_contract.md
data_quality.md
repository_conventions.md
```

Phase-specific records use:

```text
phase<N>_<scope>.md
```

Preferred suffixes:

```text
_contract
_plan
_acceptance
_final_acceptance
```

Existing historical names are retained when renaming would weaken traceability.

## 6. Final Review Path

A maintainer should begin with:

```text
../README.md
        ↓
handover.md
        ↓
architecture.md
        ↓
security_considerations.md
        ↓
production_gap_assessment.md
        ↓
evidence.md
        ↓
phase11_handover_acceptance.md
```

This path separates how the system works, how to run it, what security boundaries exist, what is not production-ready, what evidence supports the claims, and what was finally accepted.
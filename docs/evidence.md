# Engineering Evidence Index

## Document Role

**CURRENT PHASE 11 PUBLIC EVIDENCE NAVIGATION**

Documentation index: [README.md](README.md)

## Purpose

This file provides one curated entry point into the public engineering evidence for the completed Cyber Governance Automation Lab.

It intentionally separates:

```text
implementation evidence
acceptance evidence
historical phase records
private operational evidence
```

Private tenant artifacts are not required for public verification of the repository's engineering claims.

## 1. Canonical Reproducible Evidence

The canonical deterministic baseline is source-controlled and executable.

Inputs:

```text
data/reference/control_catalog.json
data/raw/evidence_submissions.csv
data/raw/actions.csv
```

Acceptance date:

```text
2026-08-15
```

Expected result:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

Primary automated evidence:

```text
tests/test_extract.py
tests/test_validate.py
tests/test_transform.py
tests/test_load.py
tests/test_main.py
```

Current full-suite baseline before Phase 11 documentation-only changes:

```text
84 passed
```

## 2. Phase 5 — Evidence Intake

Public sanitized screenshots:

```text
docs/screenshots/phase-5-evidence-intake/
```

Curated files include:

```text
phase5_forms_intake.webp
phase5_forms_settings.webp
phase5_flow_overview.webp
phase5_flow_core_steps.webp
phase5_happy_path_run.webp
phase5_happy_path_register.webp
phase5_no_match.webp
phase5_duplicate_business_key.webp
phase5_invalid_submission_state.webp
```

What they evidence:

- authenticated Forms configuration,
- workflow structure,
- expected-Submission resolution,
- happy-path update,
- no-match handling,
- duplicate-business-key handling,
- invalid-state handling.

Authoritative implementation/acceptance record:

```text
docs/phase5_evidence_intake.md
```

## 3. Phase 6 — Scheduled Reminder Automation

Public sanitized screenshots:

```text
docs/screenshots/phase-6-reminder-automation/
```

Curated files include:

```text
phase6_flow_overview.webp
phase6_overdue_detection.webp
phase6_control_lookup_guard.webp
phase6_decision_tree.webp
phase6_create_reuse_paths.webp
phase6_same_day_skip.webp
phase6_action_register.webp
```

What they evidence:

- overdue detection,
- Control lookup guardrails,
- active-Action create/reuse decision path,
- duplicate/ambiguous fail-safe behavior,
- same-day idempotency,
- persisted reminder history.

Authoritative implementation/acceptance record:

```text
docs/phase6_reminder_automation.md
```

## 4. Phase 7 — Reporting Snapshot Bridge

Public sanitized workflow source:

```text
power_automate/solutions/cyber_governance_automation/
├── README.md
├── deployment-template.json
└── workflow.template.json
```

Public screenshot evidence:

```text
docs/screenshots/phase-7-reporting-export/
```

Curated files include:

```text
phase7_snapshot_context.webp
phase7_success_catch_skipped.webp
phase7_failure_path.webp
```

What they evidence:

- shared snapshot context,
- successful TRY path,
- skipped CATCH on success,
- controlled failure path,
- sanitized source representation.

Acceptance records:

```text
docs/phase7_power_automate_acceptance.md
docs/phase7_python_external_input.md
docs/phase7_end_to_end_acceptance.md
```

## 5. Phase 8 — Power BI Dashboard

Curated public images:

```text
docs/images/phase8/
├── management-overview.webp
├── control-monitoring.webp
└── process-data-quality.webp
```

Source-controlled BI implementation:

```text
powerbi/CyberGovernanceDashboard/
```

Evidence available directly from source:

```text
PBIP project
PBIR report definition
TMDL semantic model
2 reporting tables
1 active relationship
21 DAX measures
0 calculated tables
0 calculated columns
3 report pages
```

Acceptance records:

```text
docs/phase8_canonical_acceptance.md
docs/phase8_operational_acceptance.md
docs/phase8_final_acceptance.md
```

## 6. Phase 9 — Controlled AI Workflow

Version-controlled prompt:

```text
ai/prompts/control_review_prompt.md
```

Structured output schema:

```text
ai/schemas/control_review.schema.json
```

Synthetic examples:

```text
ai/examples/control_review_input_sub005.json
ai/examples/control_review_input_sub014.json
ai/examples/control_review_output_sub005.json
ai/examples/control_review_output_sub014.json
ai/examples/control_review_input_prompt_injection.json
ai/examples/control_review_output_prompt_injection.json
```

Deterministic validation:

```text
src/ai_validation.py
```

Automated evidence:

```text
tests/test_ai_contract.py
```

Human-review acceptance:

```text
docs/phase9_human_acceptance.md
docs/phase9_ai_acceptance.md
```

Claims supported by this evidence:

- only deterministic DQ-valid exception candidates enter the queue,
- minimized fields exclude selected identity/evidence-reference data,
- supplied record values are treated as untrusted,
- output is schema-constrained,
- Submission/Control correlation is validated,
- compliance fields are not permitted in structured output,
- human review remains mandatory,
- one synthetic prompt-injection scenario is acceptance-tested.

Unsupported claim:

```text
universal prompt-injection resistance
```

## 7. Phase 10 — Local Read-only REST Integration

Server:

```text
api/mock_api.py
```

Client:

```text
src/api_client.py
```

Automated API evidence:

```text
tests/test_api.py
```

Automated client evidence:

```text
tests/test_api_client.py
```

Acceptance records:

```text
docs/phase10_rest_api_contract.md
docs/phase10_rest_api_acceptance.md
```

Claims supported by implementation/tests:

```text
2 GET business endpoints
canonical Control source only
control_id + risk_level public fields only
404 CONTROL_NOT_FOUND
500 CONTROL_SOURCE_ERROR
explicit 3-second client timeout
controlled HTTP/connection/timeout/JSON/shape failures
loopback-only accepted runtime
```

## 8. Continuous Integration Evidence

Workflow:

```text
.github/workflows/tests.yml
```

The workflow:

1. checks out the repository,
2. sets up Python 3.14.5,
3. installs the accepted dependency set,
4. runs `python -m pytest -q`.

The completed Phase 10 `main` baseline passed:

```text
84 passed in 6.51s
```

Phase 11 preserves the same functional baseline and adds dependency-lock/handover documentation.

## 9. Documentation Evidence

Current-state foundation documents:

```text
docs/architecture.md
docs/business_process.md
docs/data_model.md
docs/data_contract.md
docs/data_quality.md
docs/repository_conventions.md
```

Phase 11 handover documents:

```text
docs/security_considerations.md
docs/production_gap_assessment.md
docs/handover.md
docs/evidence.md
docs/phase11_handover_acceptance.md
```

The documentation index maps historical and current-state files:

```text
docs/README.md
```

## 10. Evidence Quality Rules

Public evidence should satisfy:

- source-controlled where practical,
- synthetic or sanitized,
- linked to a concrete claim,
- distinguish automated from manual acceptance,
- distinguish canonical from operational observations,
- avoid screenshots when code/tests provide stronger evidence,
- avoid publishing private tenant identifiers merely to make a portfolio claim look more concrete.

## 11. Private Evidence Boundary

The following may exist during operation but are deliberately not public portfolio evidence:

- live Microsoft 365 workbook,
- private Phase 7 snapshot packages,
- reachable operational e-mail identities,
- tenant/connection/resource identifiers,
- private Power Automate exports,
- private processed operational outputs,
- private evidence references/comments.

Their absence from public Git is a security/privacy property, not a documentation defect.

## 12. Recommended Review Path

A reviewer who wants the shortest technically meaningful tour should inspect:

```text
README.md
        ↓
docs/architecture.md
        ↓
src/main.py + src/validate.py + src/transform.py
        ↓
tests/test_main.py + tests/test_validate.py
        ↓
power_automate/solutions/cyber_governance_automation/workflow.template.json
        ↓
powerbi/CyberGovernanceDashboard/
        ↓
ai/prompts + ai/schemas + tests/test_ai_contract.py
        ↓
api/mock_api.py + src/api_client.py + API/client tests
        ↓
docs/security_considerations.md
        ↓
docs/production_gap_assessment.md
```

This path shows the system's claims through implementation and acceptance evidence rather than through README prose alone.
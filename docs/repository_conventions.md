# Repository Documentation Conventions

## Purpose

This document defines lightweight naming and documentation conventions for the Cyber Governance Automation Lab so later phases extend the repository without reintroducing inconsistent file names, screenshot paths, terminology, or implementation-status claims.

These conventions describe repository organization; they do not add business rules.

## 1. Documentation Roles

Current-state foundation documents use descriptive names because they remain authoritative across phases:

```text
docs/architecture.md
docs/business_process.md
docs/data_model.md
docs/data_contract.md
docs/data_quality.md
```

Phase-specific implementation or acceptance documents use:

```text
docs/phase<N>_<scope>.md
```

Examples:

```text
docs/phase2_dataset_coverage.md
docs/phase3_pipeline_contract.md
docs/phase4_test_acceptance.md
docs/phase5_evidence_intake.md
docs/phase6_reminder_automation.md
```

## 2. Screenshot Paths

Phase-specific screenshot evidence uses:

```text
docs/screenshots/phase-<N>-<scope>/
```

Examples:

```text
docs/screenshots/phase-5-evidence-intake/
docs/screenshots/phase-6-reminder-automation/
```

Screenshot filenames use lower-case phase prefixes and snake_case descriptions:

```text
phase5_flow_overview.webp
phase6_overdue_detection.webp
```

Public screenshots must be sanitized when authenticated identities, reachable e-mail addresses, tenant identifiers, connection identifiers, or similar operational metadata could be exposed.

## 3. Terminology

Logical entity names are capitalized in prose when referring to the domain concept:

```text
Control
Submission
Action
Data Quality Issue
```

Physical/table/field identifiers retain their exact technical representation:

```text
SubmissionRegister
ControlCatalog
ActionRegister
submission_id
control_id
reminder_count
```

The following semantic separations must remain explicit:

```text
Evidence Present != Compliant
Not Submitted != Non-Compliant
Non-Compliant != Overdue
Compliance != Timeliness
Compliance != Data Quality
Submission Status != Action Status
```

## 4. Implementation Status Language

Documentation distinguishes:

```text
IMPLEMENTED AND ACCEPTANCE-TESTED
PLANNED
NOT IMPLEMENTED
```

Historical phase documents may describe what was out of scope for that phase, but current-state documents must not describe a later completed capability as still planned.

Known roadmap deltas remain explicit rather than being rewritten as completed functionality.

## 5. Data-Plane Boundary

Current documentation must preserve the distinction between:

```text
Operational Microsoft 365 state
!=
Canonical repository fixtures
```

Operational acceptance activity must not be copied into canonical repository CSV/JSON merely to make later live state and historical deterministic fixtures look identical.

## 6. Rule and Outcome Naming

Canonical Submission Data Quality rules remain:

```text
DQ-001 through DQ-010
```

Operational workflow outcomes such as:

```text
NO_MATCH
DUPLICATE_BUSINESS_KEY
INVALID_SUBMISSION_STATE
CONTROL_NOT_FOUND
DUPLICATE_CONTROL
DUPLICATE_ACTIVE_ACTION
SAME_DAY_REMINDER_SKIPPED
```

are workflow outcomes, not additional DQ rule IDs.

## 7. Repository Changes

Later phases should:

- update `README.md` when project status or primary architecture changes,
- update `docs/architecture.md` when component/data-plane responsibilities change,
- add or update the relevant phase-specific contract,
- preserve historical acceptance fixtures unless a deliberate contract change is made,
- keep generated runtime outputs out of version control unless a later phase explicitly versions them,
- run `python -m pytest -q` after changes that can affect the deterministic repository baseline,
- avoid production-readiness, compliance-certification, ROI, or similar claims not supported by implemented evidence.

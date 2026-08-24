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

Phase-specific implementation, planning, or acceptance documents use:

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
docs/phase7_reporting_export.md
docs/phase7_power_automate_acceptance.md
docs/phase7_python_external_input.md
docs/phase7_end_to_end_acceptance.md
```

Historical implementation-plan documents may be retained as design evidence, but they must be labeled clearly as historical once the planned runtime has been implemented.

## 2. Current State vs. Historical Acceptance

Current-state documents must describe the present implementation accurately.

Historical phase-specific acceptance documents remain valid for the phase/time they record and do not need their historical observations rewritten merely to resemble later project state.

For example:

```text
historical Phase 4 test count
!=
current repository test count after later phases
```

A historical document may state that a later capability was out of scope at that time. A current-state document must not describe that capability as still planned after it has been implemented.

When a later phase changes the current architecture without invalidating an earlier acceptance result:

- preserve the historical evidence,
- update the current-state foundation documents,
- add a subsequent-status note to the phase-specific document when needed to avoid ambiguity.

## 3. Screenshot and Public Image Paths

Phase-specific raw or sanitized screenshot evidence normally uses:

```text
docs/screenshots/phase-<N>-<scope>/
```

Examples:

```text
docs/screenshots/phase-5-evidence-intake/
docs/screenshots/phase-6-reminder-automation/
docs/screenshots/phase-7-reporting-export/
```

Screenshot filenames use lower-case phase prefixes and snake_case descriptions:

```text
phase5_flow_overview.webp
phase6_overdue_detection.webp
phase7_failure_path.webp
```

Curated public image assets that are embedded directly in top-level portfolio documentation may instead use:

```text
docs/images/phase<N>/
```

This path is appropriate when the image is a deliberately selected public presentation derivative rather than a raw runtime-evidence dump. Phase 8 uses this pattern for its three canonical Power BI dashboard images:

```text
docs/images/phase8/management-overview.webp
docs/images/phase8/control-monitoring.webp
docs/images/phase8/process-data-quality.webp
```

A public image that also supports a phase acceptance document should have one canonical repository path rather than being duplicated solely to satisfy folder conventions.

All public screenshots and image assets must be sanitized when authenticated identities, reachable e-mail addresses, tenant/environment identifiers, connection/resource identifiers, or similar operational metadata could be exposed.

Raw acceptance screenshots do not need to be committed when a sanitized subset plus written acceptance evidence is sufficient to establish the contract.

## 4. Terminology

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
Unknown != False
Not Evaluated != Failed
Action completion != Submission compliance
```

Target business lifecycle and implemented automation must also be distinguished where they differ. A desired lifecycle transition is not described as automated unless the implemented workflow actually performs it.

## 5. Implementation Status Language

Documentation distinguishes:

```text
IMPLEMENTED AND ACCEPTANCE-TESTED
COMPLETE
PLANNED
NOT IMPLEMENTED
HISTORICAL IMPLEMENTATION PLAN
```

Known roadmap deltas remain explicit rather than being rewritten as completed functionality.

Phase completion claims must be supported by the applicable implementation and acceptance evidence.

## 6. Data-Plane Boundary

Current documentation must preserve the distinction between:

```text
Operational Microsoft 365 state
!=
Canonical repository fixtures
```

Operational acceptance activity must not be copied into canonical repository CSV/JSON merely to make later live state and historical deterministic fixtures look identical.

An operational snapshot may be processed through explicit external paths without becoming a canonical repository dataset.

## 7. Rule and Outcome Naming

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

## 8. Repository Changes

Later phases should:

- update `README.md` when project status or primary architecture changes,
- update current-state foundation documents when component, process, or data-plane responsibilities change,
- add or update the relevant phase-specific contract/acceptance document,
- preserve historical acceptance fixtures unless a deliberate contract change is made,
- keep generated runtime outputs and private operational snapshots out of version control,
- keep public workflow/source representations sanitized,
- run `python -m pytest -q` after changes that can affect the deterministic repository baseline,
- distinguish current test counts from historical phase-specific test counts,
- avoid production-readiness, compliance-certification, ROI, or similar claims not supported by implemented evidence.

## 9. Source-of-Truth Priority

For the current project state, use this order:

```text
implemented code + canonical data + automated tests
        ↓
current-state foundation docs
        ↓
latest phase contract / acceptance evidence
        ↓
historical phase-specific documents and plans
```

Historical documents are evidence of what was designed or accepted at that time. They do not override later implemented current-state evidence.

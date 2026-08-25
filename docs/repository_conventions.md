# Repository Documentation Conventions

## Document Role

**CURRENT-STATE FOUNDATION DOCUMENT — CURRENT THROUGH PHASE 10**

Documentation index: [README.md](README.md)

## Purpose

This document defines lightweight repository, naming, status, and documentation conventions for the Cyber Governance Automation Lab. The goal is to keep later changes traceable and prevent inconsistent terminology, file roles, screenshot paths, status claims, or privacy boundaries.

These conventions organize engineering evidence; they do not add business rules.

## 1. Documentation Classes

### Current-state foundation documents

Stable cross-phase documents use descriptive names and describe the **present implementation**:

```text
docs/architecture.md
docs/business_process.md
docs/data_model.md
docs/data_contract.md
docs/data_quality.md
docs/repository_conventions.md
```

Each foundation document begins with a `Document Role` section stating that it is current-state documentation and the latest covered phase where useful.

### Phase-specific documents

Phase-specific contracts, plans, implementation evidence, and acceptance records use:

```text
docs/phase<N>_<scope>.md
```

Preferred role suffixes where useful:

```text
_contract
_plan
_acceptance
_final_acceptance
```

Examples:

```text
docs/phase3_pipeline_contract.md
docs/phase4_test_acceptance.md
docs/phase7_implementation_plan.md
docs/phase8_final_acceptance.md
docs/phase10_rest_api_contract.md
docs/phase10_rest_api_acceptance.md
```

The normalized mapping of all documentation to phase/work-package role and status is maintained in:

```text
docs/README.md
```

## 2. Current State vs. Historical Evidence

Current-state foundation documents must describe the present implementation accurately.

Historical phase-specific documents remain valid for the phase/time they record. Historical observations such as test counts are not rewritten merely to match later phases.

```text
historical Phase 4 test count
!=
current repository test count after Phase 10
```

Historical implementation plans may be retained as engineering evidence but must be clearly identifiable as historical once implementation exists.

When a later phase changes the current architecture without invalidating earlier evidence:

- preserve the historical contract/acceptance record,
- update current-state foundation documents,
- add a new phase-specific acceptance/current-state record,
- add a subsequent-status note only where needed to prevent ambiguity,
- avoid rewriting frozen pre-implementation contracts as if they had been written after implementation.

Phase 10 follows this pattern:

```text
phase10_rest_api_contract.md
→ frozen Phase 10.0 design contract

phase10_rest_api_acceptance.md
→ implemented Phase 10.1–10.10 result
```

## 3. Documentation Index

`docs/README.md` is the navigation layer for the documentation set.

It should identify for each file:

- phase/work-package association,
- document role,
- whether it is current-state, historical plan, contract, implementation evidence, or acceptance evidence.

The index provides consistent assignment without renaming historical files and breaking traceability or links.

## 4. Screenshot and Public Image Paths

Phase-specific runtime/sanitized screenshot evidence normally uses:

```text
docs/screenshots/phase-<N>-<scope>/
```

Examples:

```text
docs/screenshots/phase-5-evidence-intake/
docs/screenshots/phase-6-reminder-automation/
docs/screenshots/phase-7-reporting-export/
```

Screenshot filenames use lower-case phase prefixes and descriptive names.

Curated public image assets embedded in portfolio documentation may use:

```text
docs/images/phase<N>/
```

Phase 8 uses this for the three canonical dashboard images.

A public image should have one canonical repository path rather than being duplicated only to satisfy folder conventions.

Public screenshots/images must be sanitized when authenticated identities, reachable e-mail addresses, tenant/environment identifiers, connection/resource identifiers, or similar operational metadata could be exposed.

## 5. Terminology

Logical entity names are capitalized in prose:

```text
Control
Submission
Action
Data Quality Issue
```

Physical/table/field identifiers keep exact technical representation:

```text
SubmissionRegister
ControlCatalog
ActionRegister
submission_id
control_id
reminder_count
```

Technical integration objects are named as technical objects rather than promoted to domain entities:

```text
snapshot manifest
AI review output
ControlSummary
HTTP response
ApiClientError
```

The following semantic separations remain explicit:

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
Control risk != AI review priority
Schema-valid != factually correct
AI recommendation accepted != Submission compliant
REST API != Governance authority
API response != Compliance decision
```

## 6. Implementation Status Language

Use explicit labels such as:

```text
CURRENT-STATE FOUNDATION DOCUMENT
FROZEN CONTRACT
HISTORICAL IMPLEMENTATION PLAN
IMPLEMENTED AND ACCEPTANCE-TESTED
FINAL ACCEPTANCE RECORD
COMPLETE
PLANNED
NOT IMPLEMENTED
```

Phase-completion claims must be supported by applicable implementation and acceptance evidence.

A final work package that includes PR/CI closure may be described as complete **when the final PR is merged with CI green**; before that point its closure condition should remain explicit.

## 7. Data-Plane Boundary

Documentation and code must preserve:

```text
Operational Microsoft 365 state
!=
Canonical repository fixtures
```

Operational acceptance activity is not copied into canonical CSV/JSON simply to make live and deterministic states look identical.

Phase 7 private source snapshots can be processed through explicit external paths without becoming canonical repository data.

Phase 10 deliberately reads only the canonical synthetic Control Catalog and does not create a new operational data plane.

## 8. Rule and Outcome Naming

Canonical Submission Data Quality rules remain exactly:

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

are workflow outcomes, not DQ rule IDs.

Phase 10 integration outcomes such as:

```text
CONTROL_NOT_FOUND
CONTROL_SOURCE_ERROR
ApiClientError
```

are HTTP/client integration outcomes, not DQ rules or compliance decisions.

## 9. Source-Code Directory Roles

Current source boundaries:

```text
src/      deterministic pipeline, AI validation, REST client
api/      FastAPI service boundary
tests/    automated contract/regression tests
ai/       controlled prompt/schema/examples
data/     canonical fixtures + ignored generated outputs
power_automate/ sanitized workflow source
powerbi/  source-controlled PBIP/PBIR/TMDL project
docs/     current-state and phase-specific engineering evidence
```

Do not duplicate a business rule merely because a new technical integration directory is added.

Phase 10 specifically reuses:

```text
src.extract.load_control_catalog()
```

rather than adding a second Control parser under `api/`.

## 10. Dependency Conventions

`requirements.txt` contains dependencies required by implemented repository functionality and automated tests.

A dependency's presence must not be interpreted as proof that a phase is implemented; implementation code, tests, and acceptance evidence are authoritative.

Current Phase 10 distinction:

```text
requests → runtime REST client
httpx2   → FastAPI/Starlette TestClient support
```

## 11. Git and Privacy Hygiene

Later changes should:

- keep generated runtime outputs outside version control,
- keep private operational snapshots outside version control,
- keep operational workbook copies outside version control,
- keep tenant/environment/resource identifiers and credentials outside version control,
- keep public Power Automate source sanitized,
- keep Power BI local cache/settings excluded,
- remove placeholder `.gitkeep` files when a formerly empty directory receives real tracked implementation files where doing so improves clarity,
- avoid committing unrelated generated editor/runtime changes with a phase implementation.

## 12. Repository Change Checklist

A phase that changes the current system should:

1. implement the smallest code/config change consistent with the frozen contract,
2. add focused automated coverage,
3. run the complete regression suite,
4. perform required manual acceptance separately from unit/in-process tests,
5. verify privacy/security boundaries,
6. update `README.md` when public project status or architecture changes,
7. update current-state foundation documents when responsibilities/process/data boundaries change,
8. add/update the phase-specific acceptance record,
9. update `docs/README.md` when documentation is added or its role changes,
10. review the complete PR diff and CI result before merge.

Avoid unsupported production-readiness, compliance-certification, ROI, security-certification, or universal-resilience claims.

## 13. Test Count Convention

Current documentation distinguishes current and historical test counts.

Examples:

```text
Phase 4 historical baseline = 35
Phase 9 completed state     = 64
Phase 10 completed state    = 84
```

Historical acceptance files keep their historical numbers. Current-state README/architecture use the current complete-suite result.

## 14. Source-of-Truth Priority

For the current project state:

```text
implemented code + canonical data + automated tests
        ↓
current-state foundation documents
        ↓
latest phase implementation/acceptance evidence
        ↓
historical phase-specific contracts/plans/acceptance records
```

For a historical question, use the document tied to that phase and interpret it in its recorded context.

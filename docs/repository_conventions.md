# Repository Documentation Conventions

## Document Role

**CURRENT-STATE FOUNDATION DOCUMENT — PHASE 11 HANDOVER**

Documentation index: [README.md](README.md)

## Purpose

This document defines repository, naming, status, privacy, dependency, and documentation conventions for the completed Cyber Governance Automation Lab. These conventions organize engineering evidence; they do not add business rules.

## 1. Documentation Classes

### Current-state foundation documents

Stable cross-phase documents describe the present implemented semantics:

```text
docs/architecture.md
docs/business_process.md
docs/data_model.md
docs/data_contract.md
docs/data_quality.md
docs/repository_conventions.md
```

Phase 11 does not add new runtime business semantics, so the Phase 10 architecture/process/data foundation remains authoritative and is supplemented by the handover/security documents below.

### Phase 11 handover documents

```text
docs/security_considerations.md
docs/production_gap_assessment.md
docs/handover.md
docs/evidence.md
docs/phase11_handover_acceptance.md
```

### Phase-specific records

Historical contracts, plans, implementation evidence, and acceptance records use:

```text
docs/phase<N>_<scope>.md
```

Preferred suffixes:

```text
_contract
_plan
_acceptance
_final_acceptance
```

Historical documents remain tied to the phase they describe and are not silently rewritten to look current.

## 2. Source-of-Truth Order

For current implementation questions:

```text
implemented code + canonical data + automated tests
        ↓
current-state foundation documents
        ↓
latest handover / acceptance record
        ↓
historical phase contracts, plans, and acceptance evidence
```

For a historical question, use the phase-specific document in its recorded context.

## 3. Current State vs. Historical Evidence

A later test count does not invalidate an earlier acceptance record:

```text
Phase 4 historical baseline = 35 tests
Phase 9 completed state     = 64 tests
Phase 10/11 baseline        = 84 tests
```

Likewise:

```text
canonical repository fixtures
!=
operational Microsoft 365 observations
```

Do not rewrite historical operational counts into canonical source data.

## 4. Naming and Terminology

Logical entities are capitalized in prose:

```text
Control
Submission
Action
Data Quality Issue
```

Technical identifiers preserve their exact representation:

```text
ControlCatalog
SubmissionRegister
ActionRegister
submission_id
control_id
reminder_count
```

Technical integration artifacts are not promoted to business entities:

```text
snapshot manifest
AI review output
ControlSummary
HTTP response
ApiClientError
```

## 5. Frozen Semantic Separations

Documentation, code, tests, workflow automation, reporting, AI review, and REST integration must preserve:

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

Changing one of these requires an explicit re-contracting decision, not a convenience refactor.

## 6. Rule and Outcome Naming

Submission Data Quality remains exactly:

```text
DQ-001 through DQ-010
```

Workflow outcomes such as:

```text
NO_MATCH
DUPLICATE_BUSINESS_KEY
INVALID_SUBMISSION_STATE
CONTROL_NOT_FOUND
DUPLICATE_CONTROL
DUPLICATE_ACTIVE_ACTION
SAME_DAY_REMINDER_SKIPPED
```

are not DQ rule IDs.

REST/client outcomes such as:

```text
CONTROL_NOT_FOUND
CONTROL_SOURCE_ERROR
ApiClientError
```

are integration outcomes, not DQ or compliance results.

## 7. Directory Roles

```text
src/      deterministic pipeline, AI validation, REST client
api/      FastAPI service boundary
tests/    automated contract/regression tests
ai/       controlled prompt/schema/examples
data/     canonical fixtures + ignored generated outputs
power_automate/ sanitized workflow source
powerbi/  source-controlled PBIP/PBIR/TMDL project
docs/     current-state, historical, evidence, and handover documentation
```

Do not duplicate business rules merely because a new technical component is added.

## 8. Dependency Conventions

```text
requirements.txt
```

contains direct project/test dependencies.

```text
requirements-lock.txt
```

records the exact accepted Python environment for reproducible Phase 11 handover and CI.

The lock is an engineering reproducibility artifact, not a guarantee that future operating systems or package indexes will support the environment indefinitely.

Current distinction:

```text
requests -> runtime REST client
httpx2   -> FastAPI/Starlette TestClient support
```

## 9. Generated and Private Artifacts

Generated runtime outputs remain outside normal version control:

```text
data/curated/
```

Private operational artifacts must not be committed:

- live operational workbook,
- private reporting snapshots,
- private processed outputs,
- tenant/environment/resource identifiers,
- reachable private identities,
- credentials/tokens/certificates,
- private deployment ZIPs,
- machine-local Power BI cache/state.

Public Power Automate source and screenshots must remain sanitized.

## 10. Screenshot and Image Conventions

Runtime evidence:

```text
docs/screenshots/phase-<N>-<scope>/
```

Curated public portfolio images:

```text
docs/images/phase<N>/
```

Prefer code/tests over screenshots where they provide stronger evidence. Do not publish private data solely to make a portfolio claim look more concrete.

## 11. Placeholder Hygiene

`.gitkeep` exists only to retain otherwise-empty directories.

Once a directory contains real tracked implementation files, remove the obsolete placeholder when safe. `data/curated/.gitkeep` remains intentional because generated outputs are ignored.

## 12. Status Language

Use explicit status labels:

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

A completion claim must be supported by applicable implementation and acceptance evidence.

## 13. Change Checklist

For future changes:

1. start from current `main`,
2. create a feature branch,
3. preserve frozen semantics unless explicitly re-contracted,
4. implement the smallest coherent change,
5. add focused tests for executable behavior,
6. run the complete regression suite,
7. perform required manual acceptance separately,
8. verify privacy/security boundaries,
9. update current-state documentation,
10. update the documentation index,
11. add/update acceptance evidence,
12. review the complete PR diff,
13. require green CI before merge.

Avoid unsupported claims of production readiness, certification, compliance, universal security, or universal AI resilience.

## 14. Final Handover Convention

The completed portfolio PoC is handed over through:

```text
README.md
        ↓
docs/README.md
        ↓
docs/handover.md
        ↓
docs/security_considerations.md
        ↓
docs/production_gap_assessment.md
        ↓
docs/evidence.md
        ↓
docs/phase11_handover_acceptance.md
```

This sequence makes setup, trust boundaries, residual risk, public evidence, and final acceptance discoverable without reconstructing the project from chat history.
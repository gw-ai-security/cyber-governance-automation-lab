# Technical Handover Runbook

## Document Role

**CURRENT PHASE 11 HANDOVER RUNBOOK**

Documentation index: [README.md](README.md)

## Purpose

This runbook explains how to inspect, run, test, and safely operate the completed Cyber Governance Automation Lab in its accepted proof-of-concept scope.

It is written for a technical maintainer who did not build the project.

## 1. Repository Baseline

Phase 11 starts from the completed Phase 10 `main` baseline:

```text
eebce4e78decf95cd8bb9e031eea471e5d47df8e
```

Accepted canonical reference date:

```text
2026-08-15
```

Accepted canonical result:

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

## 2. Prerequisites

Primary accepted Python runtime:

```text
Python 3.14.5
```

Other local tools used by specific components:

- Git,
- Power BI Desktop for PBIP/PBIR/TMDL runtime inspection,
- Microsoft 365 / Power Automate for the operational workflows,
- optionally Power Platform CLI (`pac`) for solution-source workflows.

The repository does not include tenant credentials or private deployment bindings.

## 3. Clone and Python Environment

Example:

```bash
git clone https://github.com/gw-ai-security/cyber-governance-automation-lab.git
cd cyber-governance-automation-lab
python -m venv .venv
```

Activate the environment using the appropriate command for the operating system, then install dependencies.

### Accepted locked environment

For maximum reproducibility of the final accepted PoC:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
```

### Top-level dependency declaration

For normal development dependency declaration:

```bash
python -m pip install -r requirements.txt
```

`requirements-lock.txt` records the concrete dependency set observed in the accepted Phase 10/11 CI environment. `requirements.txt` remains the concise direct-dependency list.

## 4. Run the Full Test Suite

```bash
python -m pytest -q
```

Phase 10 baseline expectation:

```text
84 passed
```

If Phase 11 adds documentation/CI-only changes, the functional test count is expected to remain 84.

A failing test is a release blocker until understood. Do not update expected canonical values merely to make a regression pass.

## 5. Run the Canonical Deterministic Pipeline

```bash
python src/main.py --as-of-date 2026-08-15
```

Expected console summary:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

Generated outputs are written to:

```text
data/curated/
├── curated_control_status.csv
├── data_quality_issues.csv
└── ai_review_queue.json
```

`data/curated/` is generated runtime state and is ignored by Git except for its directory placeholder.

## 6. Canonical Acceptance Checks

Check:

```text
curated_control_status.csv -> 15 data rows
data_quality_issues.csv     -> 5 data rows
ai_review_queue.json        -> SUB-005 + SUB-014
```

The canonical DQ findings are:

```text
SUB-002 -> DQ-004 Missing Evidence
SUB-006 -> DQ-003 Invalid Status
SUB-008 -> DQ-005 Duplicate Submission
SUB-009 -> DQ-005 Duplicate Submission
SUB-015 -> DQ-002 Unknown Control ID
```

Do not remove invalid rows from curated reporting. Submission grain and lineage preservation are intentional.

## 7. Process an Explicit External Snapshot

The Python CLI supports an explicit coherent source set:

```bash
python src/main.py \
  --as-of-date 2026-08-23 \
  --controls-path "/private/snapshots/security_control_snapshot_<id>.json" \
  --submissions-path "/private/snapshots/security_submission_snapshot_<id>.csv" \
  --actions-path "/private/snapshots/security_action_snapshot_<id>.csv" \
  --output-directory "/private/processed/<id>"
```

Critical rule:

```text
controls + submissions + actions overrides are all-or-none
```

Partial source override is rejected. There is no silent fallback to canonical files.

For a Phase 7 package, pass the `as_of_date` recorded in the matching completion manifest.

Private snapshot and processed output paths must remain outside the public repository.

## 8. Phase 7 Snapshot Package

A successful private package contains:

```text
security_control_snapshot_<snapshot_id>.json
security_submission_snapshot_<snapshot_id>.csv
security_action_snapshot_<snapshot_id>.csv
security_snapshot_manifest_<snapshot_id>.json
```

All files share one `snapshot_id`.

The manifest is created last and marks package completion.

Do not treat orphaned source files without a matching `complete` manifest as a completed snapshot package.

## 9. Power Automate Source Boundary

Sanitized source is stored under:

```text
power_automate/solutions/cyber_governance_automation/
```

Important:

```text
repository source
!=
ready-to-deploy tenant package
```

The repository intentionally replaces environment-specific values with placeholders.

Do not commit:

- live drive/workbook/table identifiers,
- connection credentials,
- reachable notification recipients,
- private tenant exports.

See the directory README for the pack/unpack/import workflow and placeholder map.

## 10. Run the Local REST API

Start only on loopback for accepted Phase 10 behavior:

```bash
python -m uvicorn api.mock_api:app --host 127.0.0.1 --port 8000
```

Useful local checks:

```text
GET http://127.0.0.1:8000/api/v1/controls
GET http://127.0.0.1:8000/api/v1/controls/CTRL-001
GET http://127.0.0.1:8000/api/v1/controls/CTRL-999
```

Expected behavior:

```text
collection -> 200
CTRL-001   -> 200
CTRL-999   -> 404 CONTROL_NOT_FOUND
source fail -> 500 CONTROL_SOURCE_ERROR
```

OpenAPI/Swagger is available from the normal FastAPI local documentation route while the server is running.

The API is not approved for network/cloud exposure in the completed PoC.

## 11. Run the Python API Client

With the local API running:

```bash
python -c "from src.api_client import get_controls; print(get_controls())"
```

The client uses an explicit three-second timeout and converts HTTP, connection, timeout, malformed JSON, and unexpected response-shape problems into `ApiClientError`.

## 12. Power BI Handover

Source-controlled project:

```text
powerbi/CyberGovernanceDashboard/
```

Open:

```text
CyberGovernanceDashboard.pbip
```

Power BI consumes exactly:

```text
curated_control_status.csv
data_quality_issues.csv
```

The semantic model contains:

```text
2 reporting tables
1 active relationship
21 DAX measures
0 calculated tables
0 calculated columns
3 primary report pages
```

The three pages are:

```text
Management Overview
Control Monitoring
Process & Data Quality
```

### Configure DataRoot

The source-controlled `DataRoot` parameter contains a local development default:

```text
C:\dev\cyber-governance-automation-lab\data\curated
```

A maintainer on another workstation must change `DataRoot` to the local directory containing the generated curated outputs before refresh.

Do not hard-code private snapshot directories into source-controlled Power BI metadata.

## 13. Controlled AI Review Handover

Relevant files:

```text
ai/prompts/control_review_prompt.md
ai/schemas/control_review.schema.json
ai/examples/
src/ai_validation.py
tests/test_ai_contract.py
```

The AI queue is generated deterministically. AI does not select its own population.

Allowed AI role:

- factual summary of supplied record,
- identify absent information,
- suggest Low/Medium/High review priority,
- recommend human follow-up.

Forbidden role:

- compliance decision,
- DQ repair,
- source write-back,
- hidden-fact invention,
- bypassing human review.

After an AI output is produced, validate schema and Submission/Control correlation before human review.

The repository examples are synthetic. No external AI provider runtime is implemented.

## 14. Documentation Navigation

Start with:

```text
docs/README.md
```

For current-state questions:

```text
implemented code + canonical data + automated tests
        ↓
current-state foundation documents
        ↓
latest acceptance record
        ↓
historical contracts/plans
```

Key handover documents:

```text
docs/security_considerations.md
docs/production_gap_assessment.md
docs/evidence.md
docs/phase11_handover_acceptance.md
```

## 15. Privacy Checklist Before Any Commit

Verify that the diff does not contain:

```text
real credentials
access tokens
private certificates/keys
tenant IDs
connection IDs
workbook/drive/table IDs
private operational snapshots
live workbook copies
reachable private e-mail addresses
private comments/evidence references
Power BI local cache/state
```

Synthetic `example.com` identities and explicit placeholder tokens are intentional public fixtures.

## 16. Change Procedure

For future changes:

1. create a feature branch,
2. preserve frozen semantic boundaries unless the change explicitly re-contracts them,
3. add focused tests for executable behavior,
4. run the complete suite,
5. verify privacy boundaries,
6. update current-state documentation,
7. add/update phase/release acceptance evidence,
8. open a PR,
9. require green CI before merge.

Do not silently change historical acceptance documents to match later implementation.

## 17. Troubleshooting

### Pipeline fails before loading data

Check file existence, CSV header set/order, Control JSON structure, and duplicate Control IDs.

### External source mode unexpectedly uses canonical data

It should not. Verify all three external source flags were supplied. Partial overrides are rejected by design.

### Power BI cannot find curated files

Generate Python outputs first and correct the `DataRoot` parameter.

### API client cannot connect

Confirm Uvicorn is running on `127.0.0.1:8000`. The accepted client default does not discover arbitrary hosts.

### API returns 500

Check that `data/reference/control_catalog.json` is present and structurally valid. The public API response intentionally hides internal exception details.

### AI output is schema-valid but questionable

Schema validity is not factual correctness. Escalate to the human Governance Reviewer; do not auto-apply the output.

## 18. Handover Completion Criteria

The project is ready for final Phase 11 closure when:

- full CI regression is green,
- canonical acceptance values remain unchanged,
- current architecture/process/data/DQ semantics remain consistent,
- security and production gaps are documented,
- a new maintainer can reproduce the Python pipeline from this runbook,
- Power BI configuration is documented,
- Power Automate private/public boundaries are documented,
- AI and REST authority boundaries are explicit,
- no private operational data or secrets are committed,
- the Phase 11 acceptance record is complete.
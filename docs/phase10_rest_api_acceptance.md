# Phase 10 — REST API Implementation and Acceptance

## Document Role

**FINAL IMPLEMENTATION AND ACCEPTANCE RECORD — PHASE 10 COMPLETE**

Tracking issue: #42 — `Phase 10: Implement local read-only REST API integration`

Frozen design contract: [phase10_rest_api_contract.md](phase10_rest_api_contract.md)

This document records the implementation and acceptance state reached after the Phase 10.0 contract freeze. The frozen contract is retained as historical design evidence and is not rewritten to pretend that its pre-implementation language was written after the implementation existed.

## 1. Purpose

Phase 10 adds a deliberately small local REST integration:

```text
Python source / existing loader
        ↓
FastAPI read-only projection
        ↓
HTTP GET + JSON
        ↓
requests-based Python client
```

The phase demonstrates an explicit technical integration boundary without adding a second governance business-rule engine.

```text
REST API != Governance authority
API response != Compliance decision
```

## 2. Implemented Components

| Component | File | Responsibility |
| --- | --- | --- |
| FastAPI service | `api/mock_api.py` | Read-only minimized Control projection |
| Existing source loader | `src/extract.py` | Canonical Control Catalog loading and structural validation |
| Python HTTP client | `src/api_client.py` | GET requests, timeout, status/JSON handling, response-shape validation |
| API contract tests | `tests/test_api.py` | Server HTTP/data/security contract |
| Client contract tests | `tests/test_api_client.py` | Client success/failure/timeout/shape behavior |
| Frozen design contract | `docs/phase10_rest_api_contract.md` | Pre-implementation architectural and acceptance boundary |

## 3. Source Boundary

The API reads only:

```text
data/reference/control_catalog.json
```

through the existing function:

```text
src.extract.load_control_catalog()
```

The API does not introduce another Control parser and does not read:

- operational Microsoft 365 workbooks,
- private Phase 7 snapshots,
- raw Submission or Action data,
- generated curated outputs,
- Power BI runtime files,
- Phase 9 AI outputs.

This preserves both the single-source boundary and the privacy boundary of the local unauthenticated PoC.

## 4. Frozen HTTP Surface

Exactly two business endpoints are implemented:

```text
GET /api/v1/controls
GET /api/v1/controls/{control_id}
```

FastAPI additionally exposes its framework-generated OpenAPI documentation endpoints. No additional business endpoint, `/health` endpoint, or write endpoint is implemented.

No business operation uses:

```text
POST
PUT
PATCH
DELETE
```

## 5. External Control Contract

The internal Control source contains eight fields, but the public API projection contains exactly:

```text
control_id
risk_level
```

Allowed risk values:

```text
Low
Medium
High
Critical
```

The service uses a Pydantic `ControlSummary` response model so the external contract is explicit in code and OpenAPI.

The following internal Control fields are not exposed:

```text
control_name
control_statement
business_unit
owner_role
owner_email
frequency
```

Project-wide private Submission/Action fields such as `submitted_by`, `evidence_reference`, and comments are not processed by this API at all.

## 6. HTTP Success and Failure Contracts

### Collection

```text
GET /api/v1/controls
→ HTTP 200
→ JSON array
→ exactly 5 canonical Controls
→ canonical source order
```

### Existing Control

```text
GET /api/v1/controls/CTRL-001
→ HTTP 200
```

```json
{
  "control_id": "CTRL-001",
  "risk_level": "Critical"
}
```

### Unknown Control

```text
GET /api/v1/controls/CTRL-999
→ HTTP 404
```

```json
{
  "detail": {
    "code": "CONTROL_NOT_FOUND",
    "message": "Control CTRL-999 was not found."
  }
}
```

### Unusable Control Source

```text
Control source load/validation failure
→ HTTP 500
```

```json
{
  "detail": {
    "code": "CONTROL_SOURCE_ERROR",
    "message": "Control data could not be loaded."
  }
}
```

Internal exception messages, absolute paths, stack traces, credentials, tokens, and private operational identifiers are not part of the external 500 response.

## 7. Python Client Contract

`src/api_client.py` uses `requests` and exposes:

```text
get_controls()
get_control(control_id)
```

Every real request uses the explicit default timeout:

```text
3 seconds
```

The client translates low-level integration failures into one controlled application exception:

```text
ApiClientError
```

Covered failure classes:

```text
timeout
connection failure
HTTP 4xx/5xx
malformed JSON
unexpected collection type
missing/unexpected Control fields
invalid Control field types
unsupported risk_level
```

The client validates the external API shape only. It contains no compliance, timeliness, Data Quality, reminder, Action, or AI-governance business rules.

## 8. Automated Acceptance

Phase 10 adds:

```text
10 API contract tests
10 API client tests
```

Current complete repository suite after Phase 10:

```text
84 passed
```

The 20 Phase 10 tests cover the frozen minimum contract:

### API tests

- collection HTTP 200,
- exactly five canonical Controls,
- deterministic source order,
- exact public field set,
- explicit `owner_email` exclusion,
- existing-Control HTTP 200 and exact body,
- unknown-Control HTTP 404 and exact body,
- collection source failure HTTP 500 and exact body,
- detail source failure HTTP 500 and exact body,
- internal-path/exception-detail non-disclosure.

### Client tests

- valid collection,
- valid single Control,
- controlled HTTP 404,
- controlled HTTP 500,
- timeout translation,
- connection-error translation,
- malformed JSON rejection,
- wrong collection top-level type rejection,
- missing-field rejection,
- explicit configured timeout propagation.

The API tests use FastAPI's in-process `TestClient`; the client tests mock network behavior. A running Uvicorn process is therefore not required for the automated suite.

## 9. Dependency Resolution

The runtime client remains:

```text
requests
```

FastAPI/Starlette's in-process test client required the current compatibility package:

```text
httpx2
```

This replaced the initially tried `httpx` test dependency after Starlette emitted a deprecation warning. `httpx2` is a test-support dependency; it does not replace `requests` as the Phase 10 runtime client.

## 10. Canonical Regression Acceptance

The complete repository suite passed after the Phase 10 implementation:

```text
84 passed
```

The canonical Phase 0–9 deterministic baseline remains unchanged at:

```text
as_of_date = 2026-08-15
```

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

Canonical AI candidates remain:

```text
SUB-005
SUB-014
```

Phase 10 therefore adds an integration surface without changing upstream governance semantics or canonical fixtures.

## 11. Manual Local Uvicorn Acceptance

Service invocation used for acceptance:

```powershell
python -m uvicorn api.mock_api:app --host 127.0.0.1 --port 8000
```

Observed real HTTP/client results:

```text
requests client → GET collection → five canonical Controls
requests client → GET CTRL-001 → expected minimized Control
real GET CTRL-999 → exact CONTROL_NOT_FOUND 404 body
server stopped → ApiClientError: Could not connect to the API.
```

FastAPI `/docs` and `/openapi.json` were also reached locally and showed the two business routes and the `ControlSummary` schema.

The service is accepted on loopback only:

```text
127.0.0.1:8000
```

Exposure through `0.0.0.0` is not required or accepted as part of Phase 10.

## 12. Security and Privacy Acceptance

Manual source inspection and automated tests establish:

| Control | Result |
| --- | --- |
| Business routes | exactly 2 GET routes |
| Write routes | none |
| Canonical source | `control_catalog.json` only |
| Existing loader reused | yes |
| Public fields | exactly `control_id`, `risk_level` |
| `owner_email` exposure | no |
| Submission/Action private data processed | no |
| Internal 500 detail leakage | blocked by external error contract |
| Unknown Control behavior | fail-safe 404 |
| Source failure behavior | fail-safe 500 |
| Client timeout | explicit 3 seconds |
| Client connection failure | controlled `ApiClientError` |
| Governance rules duplicated in API/client | no |
| Authentication | intentionally absent for local synthetic read-only PoC |
| Accepted network bind | loopback `127.0.0.1` |

No-authentication is an explicit local PoC constraint, not a production architecture recommendation.

## 13. Architecture Boundary

Phase 10 does not change the four core entities:

```text
Control
Submission
Action
Data Quality Issue
```

The API response model is an integration DTO/projection, not a fifth business entity.

Phase 10 also preserves:

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
```

## 14. Explicit Non-Goals

Phase 10 does not implement:

- OAuth, JWT, API keys, sessions, or production IAM,
- cloud deployment or API Gateway,
- Docker orchestration,
- a database,
- business write endpoints,
- Power Automate or Power BI calling this API,
- external AI provider integration,
- AI write-back,
- compliance-decision APIs,
- microservices infrastructure,
- Redis/Celery,
- rate limiting,
- enterprise RBAC,
- production observability/telemetry.

## 15. Work-Package Closure

| Work package | Result |
| --- | --- |
| Phase 10.0 — REST API Contract Freeze | ✅ Complete |
| Phase 10.1 — FastAPI Read-only Service | ✅ Complete |
| Phase 10.2 — API Contract Tests | ✅ Complete |
| Phase 10.3 — requests-based Python Client | ✅ Complete |
| Phase 10.4 — Timeout / HTTP / JSON / Connection Failure Handling | ✅ Complete |
| Phase 10.5 — Client Tests | ✅ Complete |
| Phase 10.6 — Phase 0–9 Regression Verification | ✅ Complete |
| Phase 10.7 — Local Uvicorn End-to-End Acceptance | ✅ Complete |
| Phase 10.8 — Security / Privacy Acceptance | ✅ Complete |
| Phase 10.9 — Documentation Synchronization | ✅ Complete |
| Phase 10.10 — PR / CI / Closure | ✅ Complete when final Phase 10 PR is merged with CI green |

## 16. Definition of Done

Phase 10 is accepted when this implementation and documentation are merged with the repository CI green.

At that point the phase demonstrates the complete intended learning path:

```text
canonical Python source
        ↓
FastAPI
        ↓
HTTP GET
        ↓
JSON
        ↓
requests client
        ↓
validated Python data
```

without changing the governance source of truth or introducing write authority.

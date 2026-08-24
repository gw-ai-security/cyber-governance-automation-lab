# Phase 10 REST API Contract

## Status

**Phase 10.0 — REST API Contract Freeze: COMPLETE**

Tracking issue: #42 — `Phase 10: Implement local read-only REST API integration`

This document freezes the architectural, HTTP, data, security, and acceptance boundaries for Phase 10 before implementation code is written.

Phase 10.0 contains **no FastAPI service implementation, no HTTP client implementation, and no new API tests**. Those are intentionally deferred to the later Phase 10 work packages so design decisions remain separate from programming work.

---

## 1. Purpose

Phase 10 adds a deliberately small local REST integration to the Cyber Governance Automation Lab.

The learning and engineering objective is:

```text
Python
  ↓
HTTP GET
  ↓
JSON
  ↓
Python
```

The phase demonstrates:

- a small FastAPI service,
- explicit HTTP GET endpoints,
- JSON response contracts,
- HTTP status semantics,
- a `requests`-based Python client,
- explicit request timeouts,
- controlled HTTP/connection/JSON failure handling,
- automated API and client tests,
- local end-to-end execution through Uvicorn.

Phase 10 is an integration exercise, not a redesign of the governance domain.

---

## 2. Core Architectural Rule

The REST layer is a **technical integration boundary**.

It is not a second business-rule engine.

```text
Existing deterministic repository contracts
        ↓
Read-only API projection
        ↓
HTTP / JSON
        ↓
Python client
```

Therefore:

```text
REST API
!=
Governance authority
```

and:

```text
API response
!=
Compliance decision
```

The API must reuse existing source and validation boundaries rather than reimplementing governance logic.

---

## 3. Relationship to Phases 0–9

Phase 10 must preserve all upstream contracts.

In particular, it must not change:

- the four core domain entities: Control, Submission, Action, Data Quality Issue,
- the Submission technical key `submission_id`,
- the Submission business key `control_id + reporting_period`,
- DQ-001 through DQ-010,
- Control enrichment semantics,
- Action aggregation semantics,
- overdue and late derivations,
- canonical `as_of_date = 2026-08-15` acceptance behavior,
- Power Automate workflow semantics,
- Power BI reporting contracts,
- Phase 9 AI candidate eligibility,
- the Phase 9 AI output schema,
- mandatory human governance authority.

Phase 10 adds an HTTP interface around a narrow read-only Control projection only.

---

## 4. Source Boundary

The Phase 10 API reads only the canonical synthetic Control Catalog:

```text
data/reference/control_catalog.json
```

The service must reuse the existing Python loader:

```text
src.extract.load_control_catalog()
```

The API must not introduce a second Control Catalog parser or a second copy of the physical Control validation rules.

The API does not read:

- the operational Microsoft 365 workbook,
- private Phase 7 snapshot packages,
- `data/raw/evidence_submissions.csv`,
- `data/raw/actions.csv`,
- generated `data/curated/` outputs,
- Power BI files as runtime data,
- Phase 9 AI outputs.

This keeps the unauthenticated local PoC API away from private operational identities and state.

---

## 5. API Authority Boundary

### 5.1 Allowed behavior

The API may:

- load the canonical Control Catalog through the existing loader,
- expose an explicitly minimized Control projection,
- return deterministic JSON responses,
- return HTTP success and failure status codes,
- distinguish an existing Control from an unknown Control,
- expose automatically generated OpenAPI documentation provided by FastAPI.

### 5.2 Forbidden behavior

The API must not:

- assign or change `Compliant`,
- assign or change `Non-Compliant`,
- change any Submission status,
- create, update, or complete Actions,
- send reminders,
- execute or redefine DQ-001 through DQ-010,
- repair source data,
- calculate an alternative overdue or late definition,
- change AI review eligibility,
- approve AI recommendations,
- expose AI output as authoritative governance state,
- write to Microsoft 365,
- mutate canonical repository fixtures,
- accept evidence uploads,
- provide POST, PUT, PATCH, or DELETE business endpoints.

The Phase 10 API is read-only.

---

## 6. API Version and Base Path

The frozen API base path is:

```text
/api/v1
```

The `v1` prefix makes the external HTTP contract explicit without introducing a complex version-management mechanism.

Phase 10 does not implement multiple API versions.

---

## 7. Frozen Endpoint Surface

Phase 10 implements exactly two business endpoints:

```text
GET /api/v1/controls
GET /api/v1/controls/{control_id}
```

No `/health` endpoint is required for this portfolio PoC.

No write endpoint is part of Phase 10.

---

## 8. External Control Response Model

The external API contract is intentionally smaller than the internal Control model.

Each successful Control response contains exactly:

```text
control_id
risk_level
```

Conceptual response model:

```text
ControlSummary
├── control_id
└── risk_level
```

Allowed `risk_level` values remain the existing Control risk enumeration:

```text
Low
Medium
High
Critical
```

The API does not invent a new risk taxonomy.

### 8.1 Fields intentionally not exposed

The following internal Control fields are intentionally excluded from the Phase 10 API response:

```text
control_name
control_statement
business_unit
owner_role
owner_email
frequency
```

This demonstrates the boundary:

```text
Internal source model
!=
External API contract
```

In particular, `owner_email` is not exposed even though canonical repository values are synthetic.

---

## 9. `GET /api/v1/controls`

### Purpose

Return the minimized projection of all canonical Controls.

### Successful response

```text
HTTP 200 OK
Content-Type: application/json
```

Top-level JSON type:

```text
array
```

Canonical response contains exactly five items.

Example shape:

```json
[
  {
    "control_id": "CTRL-001",
    "risk_level": "Critical"
  },
  {
    "control_id": "CTRL-002",
    "risk_level": "High"
  }
]
```

The example is abbreviated; the canonical endpoint returns all five Controls.

### Ordering

The response preserves the deterministic order of the canonical Control Catalog.

Phase 10 does not introduce an independent sorting rule.

### Failure response

If the canonical Control source cannot be loaded or structurally accepted by the existing loader:

```text
HTTP 500 Internal Server Error
```

with the generic external error contract defined below.

---

## 10. `GET /api/v1/controls/{control_id}`

### Purpose

Return one minimized Control projection by exact `control_id`.

### Existing Control

Example:

```text
GET /api/v1/controls/CTRL-001
```

Response:

```text
HTTP 200 OK
```

```json
{
  "control_id": "CTRL-001",
  "risk_level": "Critical"
}
```

### Unknown Control

Example:

```text
GET /api/v1/controls/CTRL-999
```

Response:

```text
HTTP 404 Not Found
```

The service must not guess, substitute, or return the first available Control.

Unknown input is represented as not found.

---

## 11. Error Response Contract

Phase 10 uses controlled error bodies and does not expose stack traces or internal file-system details as normal HTTP responses.

### 11.1 Unknown Control

Status:

```text
404 Not Found
```

Response shape:

```json
{
  "detail": {
    "code": "CONTROL_NOT_FOUND",
    "message": "Control CTRL-999 was not found."
  }
}
```

The supplied Control ID may be reflected in the not-found message.

### 11.2 Control source failure

Status:

```text
500 Internal Server Error
```

Response shape:

```json
{
  "detail": {
    "code": "CONTROL_SOURCE_ERROR",
    "message": "Control data could not be loaded."
  }
}
```

The external 500 response must not disclose:

- local absolute file paths,
- stack traces,
- Python exception internals,
- credentials or tokens,
- private operational identifiers.

The underlying implementation may retain the original exception internally for debugging/testing, but it is not part of the public response contract.

---

## 12. Fail-Safe Semantics

Phase 10 follows the existing project principle:

```text
Ambiguous / invalid state
→ fail safely
```

not:

```text
Ambiguous / invalid state
→ guess
```

Examples:

```text
Unknown control_id
→ 404

Unusable canonical Control source
→ 500

No silent fallback to another data source
```

The API must not silently fall back to private operational data, cached output, or another repository dataset if the canonical source cannot be loaded.

---

## 13. Authentication and Network Boundary

Phase 10 deliberately implements no authentication mechanism.

No:

- OAuth,
- JWT,
- API key,
- session login,
- identity provider integration.

This is acceptable only because Phase 10 is a local portfolio PoC using synthetic canonical Control data and a minimized read-only response.

The local manual acceptance target is:

```text
127.0.0.1:8000
```

The implementation must not require exposure on `0.0.0.0` for acceptance.

Therefore:

```text
No authentication
=
accepted local PoC constraint
```

but:

```text
No authentication
!=
production architecture
```

Production authentication/authorization remains out of scope.

---

## 14. Privacy and Data-Minimization Boundary

Phase 10 must not expose or process private operational data.

The API response intentionally excludes:

```text
owner_email
submitted_by
evidence_reference
comments
```

The latter three are not part of the Control source in any case, but are listed explicitly to preserve the project-wide privacy boundary.

Phase 10 must not commit:

- private snapshots,
- operational workbook copies,
- tenant or connection identifiers,
- credentials,
- tokens,
- reachable private identities.

---

## 15. FastAPI Implementation Boundary for Later Work

The later service implementation is planned at:

```text
api/mock_api.py
```

It must:

- create one FastAPI application,
- reuse `load_control_catalog()`,
- define explicit response models,
- implement only the two frozen GET business endpoints,
- translate source failures into the frozen generic 500 response,
- translate an unknown Control into the frozen 404 response.

The service implementation must remain small enough to read and explain line by line.

No implementation code is added in Phase 10.0.

---

## 16. Python Client Boundary for Later Work

The later client implementation is planned at:

```text
src/api_client.py
```

The client will use:

```text
requests
```

and must demonstrate:

- HTTP GET,
- explicit timeout,
- `raise_for_status()` or equivalent controlled status handling,
- JSON parsing,
- expected response-shape checks,
- controlled timeout handling,
- controlled connection-error handling,
- controlled HTTP-error handling,
- controlled malformed/unexpected JSON handling.

The client must not contain governance business rules.

No client implementation code is added in Phase 10.0.

---

## 17. Timeout Contract

Every real client request must use an explicit timeout.

The planned default Phase 10 timeout is:

```text
3 seconds
```

This is a PoC configuration value rather than a claim that three seconds is a universally correct production timeout.

The implementation must make the timeout visible and testable rather than relying on library defaults.

---

## 18. Automated Test Contract for Later Work

Phase 10 will add automated coverage in two groups.

### 18.1 API tests

Planned file:

```text
tests/test_api.py
```

Minimum contractual scenarios:

```text
GET /api/v1/controls
→ 200

canonical list response
→ exactly 5 Controls

successful items
→ exactly control_id + risk_level

owner_email
→ not exposed

GET /api/v1/controls/CTRL-001
→ 200

GET /api/v1/controls/CTRL-999
→ 404

404 body
→ deterministic CONTROL_NOT_FOUND contract

unusable Control source
→ 500

500 body
→ deterministic CONTROL_SOURCE_ERROR contract

500 body
→ no internal file-path / exception leakage
```

API tests should use FastAPI's in-process testing mechanism rather than requiring a separately running Uvicorn process.

### 18.2 Client tests

Planned file:

```text
tests/test_api_client.py
```

Minimum contractual scenarios:

```text
200 + valid list JSON
→ success

200 + valid single-Control JSON
→ success

404
→ controlled client failure

500
→ controlled client failure

timeout
→ controlled client failure

connection error
→ controlled client failure

invalid JSON
→ controlled client failure

unexpected top-level JSON type
→ controlled client failure

missing required response field
→ controlled client failure

client request
→ explicit timeout passed
```

Client error tests must mock network behavior rather than creating artificial production endpoints solely for testing failures.

---

## 19. Regression Contract

Phase 10 must not change the canonical Phase 0–9 acceptance baseline.

After Phase 10 implementation, this command must still succeed:

```text
python src/main.py --as-of-date 2026-08-15
```

with the existing canonical result:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

The canonical AI candidates remain:

```text
SUB-005
SUB-014
```

The current pre-Phase-10 documented automated-test baseline is:

```text
64 passing tests
```

Phase 10 must preserve all existing tests and add focused API/client tests. No arbitrary target test count is frozen; test cases are added according to actual contract coverage.

---

## 20. Manual End-to-End Acceptance Contract

After implementation and automated testing, Phase 10 will perform a real local HTTP acceptance.

Planned service invocation:

```text
python -m uvicorn api.mock_api:app --host 127.0.0.1 --port 8000
```

Acceptance must prove at least:

```text
real HTTP GET list
→ 200 + expected JSON

real HTTP GET existing Control
→ 200 + expected JSON

real HTTP GET unknown Control
→ 404 + expected error JSON

requests-based Python client against running API
→ successful HTTP/JSON round trip

client while API is stopped
→ controlled connection failure
```

Manual acceptance is separate from in-process automated API tests.

---

## 21. Dependencies

The repository already contains:

```text
fastapi
uvicorn
requests
```

Phase 10 may require `httpx` for FastAPI's test client during the testing work package.

No other dependency is justified by the frozen Phase 10 scope unless implementation proves it necessary.

Phase 10 must not expand into dependency/tooling work unrelated to the REST integration.

---

## 22. Explicit Non-Goals

The following are outside Phase 10:

```text
OAuth / JWT / API keys
API Gateway
cloud deployment
Docker orchestration
new database
POST / PUT / PATCH / DELETE business operations
Power Automate calling the API
Power BI calling the API
external AI provider call
AI review write-back
compliance decision API
human-review mutation API
microservices
Redis
Celery
rate limiting
enterprise RBAC
production observability platform
production telemetry architecture
```

These may be reasonable production topics, but they would add complexity without improving the specific Phase 10 learning contract.

---

## 23. Planned Work Packages

The frozen Phase 10 implementation sequence is:

```text
10.0  REST API Contract Freeze                  COMPLETE
10.1  FastAPI Read-only Service                 PLANNED
10.2  API Contract Tests                        PLANNED
10.3  requests-based Python Client              PLANNED
10.4  Client Error / Timeout Handling           PLANNED
10.5  Client Tests                              PLANNED
10.6  Phase 0–9 Regression Verification         PLANNED
10.7  Local Uvicorn End-to-End Acceptance       PLANNED
10.8  Security / Privacy Acceptance              PLANNED
10.9  Current-State Documentation Sync          PLANNED
10.10 PR / CI / Phase Closure                   PLANNED
```

Implementation should proceed in this order because each step depends on the preceding contract or executable boundary.

---

## 24. Phase 10 Definition of Done

Phase 10 as a whole is complete only when all of the following are true:

1. This REST API contract remains satisfied or any deliberate contract change is explicitly reviewed and documented.
2. `api/mock_api.py` implements the read-only FastAPI service.
3. `GET /api/v1/controls` works according to contract.
4. `GET /api/v1/controls/{control_id}` works according to contract.
5. Successful responses expose only the frozen projection.
6. Unknown Controls return the frozen 404 contract.
7. Source failures return the frozen generic 500 contract.
8. Internal error details are not exposed as normal API responses.
9. Existing `load_control_catalog()` is reused.
10. No governance, compliance, DQ, workflow, reporting, or AI rule is duplicated in the API.
11. `src/api_client.py` performs the HTTP GET integration.
12. Every client request has an explicit timeout.
13. HTTP failures are controlled.
14. Timeout failures are controlled.
15. Connection failures are controlled.
16. JSON parsing failures are controlled.
17. Unexpected response structures are controlled.
18. Automated API tests cover the frozen endpoint contract.
19. Automated client tests cover success and failure paths.
20. Existing Phase 0–9 tests remain passing.
21. The canonical 2026-08-15 pipeline result remains unchanged.
22. A real local Uvicorn end-to-end acceptance succeeds.
23. The API remains read-only and local for acceptance.
24. No private operational data is exposed or committed.
25. Current-state documentation is synchronized after successful implementation.
26. Final Pull Request CI succeeds.
27. Phase 10 tracking issue is closed only after merge and final acceptance.

---

## 25. Phase 10.0 Acceptance Result

Phase 10.0 is accepted when:

- the tracking issue exists,
- the Phase 10 feature branch exists,
- this contract is version-controlled on that branch,
- no implementation code has been added as part of 10.0,
- the API surface, response projection, error semantics, authority boundary, privacy boundary, timeout policy, test strategy, regression contract, and final DoD are explicit before programming begins.

At that point the next implementation step is:

```text
Phase 10.1 — FastAPI Read-only Service
```

The code for Phase 10.1 should be written interactively and reviewed line by line so the implementation remains understandable rather than being treated as generated boilerplate.

# Security Considerations

## Document Role

**CURRENT-STATE SECURITY AND TRUST-BOUNDARY DOCUMENT — PHASE 11 HANDOVER**

Documentation index: [README.md](README.md)

## Purpose

This document consolidates the security, privacy, trust, and authority boundaries implemented or explicitly accepted by the Cyber Governance Automation Lab.

It does not claim production security, regulatory compliance, certification, or universal resistance to attack. The project remains a portfolio proof of concept.

## 1. Security Model at a Glance

The system separates five relevant trust zones:

```text
Operational Microsoft 365 state
        ↓ private snapshot boundary
Deterministic Python processing
        ├──────────────→ Power BI reporting
        └──────────────→ minimized AI review input

Canonical synthetic Control Catalog
        ↓
Local read-only REST API
        ↓
Bounded Python HTTP client
```

Authority remains deliberately constrained:

```text
Forms / Power Automate intake != compliance authority
Reminder automation             != compliance authority
Python DQ                       != compliance authority
Power BI                        != compliance authority
AI                              != compliance authority
REST API                        != governance authority
Human Governance Review          = final governance authority in this PoC
```

## 2. Data Classification and Privacy Boundary

### Public repository data

The repository may contain:

- synthetic Control definitions,
- synthetic Submission and Action fixtures,
- synthetic e-mail addresses using `example.com`,
- sanitized workflow source,
- sanitized screenshots,
- source-controlled Power BI metadata,
- minimized synthetic AI examples,
- local REST API/client source,
- automated tests and non-sensitive acceptance evidence.

### Private operational data

The following remain outside public Git history:

- the live operational workbook,
- private Phase 7 snapshot packages,
- private processed operational outputs,
- reachable operational identities,
- authenticated submitter identities,
- private comments or evidence references,
- tenant/environment/connection identifiers,
- workbook/drive/table identifiers,
- credentials, tokens, certificates, and secrets,
- private Power Platform solution exports and deployment packages,
- local Power BI cache/state.

Operational Microsoft 365 state is therefore not treated as interchangeable with canonical repository fixtures.

## 3. Evidence Handling

The model stores only `evidence_reference`; actual evidence files are not committed.

This avoids making the public repository an evidence store. A production evidence repository would additionally require, at minimum:

- access control,
- classification,
- retention and deletion policy,
- auditability,
- integrity controls,
- legal/regulatory handling rules,
- lifecycle ownership.

The PoC does not claim these controls are implemented.

## 4. Secrets and Configuration

The repository `.gitignore` excludes common secret and environment-file patterns. Public Power Automate source uses explicit placeholders rather than tenant values.

Security rule:

```text
public sanitized source
!=
private deployable environment configuration
```

No private identifier should be copied into a sanitized template and committed.

## 5. Power Automate Trust Boundary

### Evidence intake

Phase 5 accepts authenticated Microsoft Forms input, resolves an existing expected Submission using:

```text
control_id + reporting_period
```

and permits only:

```text
Not Submitted -> In Review
```

It does not assign `Compliant` or `Non-Compliant`.

Ambiguous or invalid state is surfaced rather than guessed.

### Reminder automation

Phase 6 detects overdue missing Submissions and creates or reuses one active Action. More than one active Action results in the controlled outcome:

```text
DUPLICATE_ACTIVE_ACTION
```

Reminder automation cannot assign compliance.

### Reporting snapshot

Phase 7 exports source facts and writes the completion manifest last. It does not repair, reinterpret, or classify source data.

The three Microsoft 365 reads are not transactionally atomic. This is an accepted PoC limitation.

## 6. Deterministic Python Boundary

Python owns:

- structural source validation,
- DQ-001 through DQ-010,
- deterministic normalization,
- Control enrichment,
- timing derivation,
- Action aggregation,
- curated reporting output,
- deterministic AI-candidate selection.

Source facts are not silently repaired.

Physical input failure and business Data Quality remain separate:

```text
physical input failure -> execution failure
DQ finding             -> successful run + DQ output
```

### Action-data limitation

The logical model permits at most one non-completed Action per Submission for missing-submission reminder tracking, and Phase 6 enforces this operationally.

The Python reporting pipeline does not implement a separate Action-specific DQ rule catalog. Malformed external Action data containing duplicate active Actions is therefore outside the guaranteed deterministic Submission-DQ contract. This remains an explicit residual limitation rather than being mislabeled as DQ-011.

## 7. Power BI Boundary

Power BI consumes only:

```text
curated_control_status.csv
data_quality_issues.csv
```

It does not directly read private workbook state, private snapshots, canonical raw Submission/Action files, the AI queue, or REST responses.

Power Query performs loading, blank-to-null conversion, and typing. It does not duplicate Python business rules.

The source-controlled project contains a configurable `DataRoot` parameter. Its repository default is a local development path and must be changed for another workstation. This is a portability/configuration concern, not a secret-management mechanism.

Power BI Service/Fabric deployment, enterprise RLS, tenant governance, and production access control are not implemented.

## 8. Controlled AI Trust Boundary

AI receives only deterministic candidates satisfying:

```text
data_quality_status = Valid
AND
(
    submission_status = Non-Compliant
    OR
    overdue_flag = True
)
```

The queue excludes fields including:

```text
owner_email
submitted_by
evidence_reference
```

Data minimization does not make free text trustworthy. Every supplied record value, including `comment`, is treated as untrusted input data.

The version-controlled prompt explicitly forbids:

- following instructions embedded in record values,
- assigning or changing compliance,
- changing source state,
- repairing DQ findings,
- inventing missing facts,
- automatic source-system write-back,
- bypassing human review.

Output is constrained by JSON Schema Draft 2020-12 and then validated for Submission/Control correlation.

Critical boundary:

```text
schema-valid AI output
!=
factually correct or governance-approved output
```

The synthetic prompt-injection case demonstrates one controlled acceptance scenario. It is not evidence of universal prompt-injection resistance.

No external AI provider runtime/API integration exists in the completed PoC.

## 9. REST API Boundary

Phase 10 exposes only canonical synthetic Control reference data through:

```text
GET /api/v1/controls
GET /api/v1/controls/{control_id}
```

The public representation contains exactly:

```text
control_id
risk_level
```

The API does not expose `owner_email`, operational Submission/Action data, private snapshots, evidence references, or AI output.

The accepted runtime target is loopback only:

```text
127.0.0.1:8000
```

It has no production authentication/authorization. This is acceptable only inside the explicitly local, synthetic, minimized, read-only Phase 10 scope.

Source failures return a generic 500 contract without leaking local paths or exception internals. Unknown Controls return a controlled 404.

## 10. REST Client Boundary

The Python client uses:

- explicit three-second timeout,
- HTTP status handling,
- JSON parsing,
- response-shape validation,
- controlled `ApiClientError` translation.

A timeout is a bounded integration failure, not a Data Quality Issue and not a compliance result.

## 11. CI and Supply-Chain Boundary

GitHub Actions runs the full Python test suite for pull requests targeting `main` and pushes to `main` using Python 3.14.5.

Phase 11 adds a lock file for the accepted Python dependency set so the validated environment can be reproduced intentionally instead of relying only on floating top-level requirements.

The repository does not claim a full software-supply-chain security program. It does not currently include artifact signing, SBOM enforcement, SLSA provenance, dependency-policy gates, or mandatory vulnerability scanning.

The Python CI check is active but repository branch protection does not currently enforce it as a required status check before merge.

## 12. Logging, Monitoring and Audit Limitations

The PoC has workflow run history, explicit failure handling, deterministic outputs, Git history, and CI history, but it does not implement a unified production audit/observability platform.

Missing production controls include:

- centralized immutable audit logging,
- security event monitoring,
- API telemetry,
- metrics/SLIs/SLOs,
- alert routing/on-call integration,
- correlation IDs across all components,
- retention enforcement,
- production incident response integration.

## 13. Residual Risks

Accepted residual risks include:

1. Excel/OneDrive is not a transactional production datastore.
2. Phase 7 multi-table reads are not transactionally atomic.
3. Operational snapshots can contain private data and depend on correct handling outside Git.
4. Python has no Action-specific DQ rule catalog.
5. Power BI has no production RLS/service deployment architecture.
6. AI guardrails do not prove universal prompt-injection resistance or factual correctness.
7. The REST API is unauthenticated and must remain local in the accepted design.
8. Dependencies and external platforms can evolve beyond the tested baseline.
9. CI is not currently enforced as a required merge gate.
10. No production IAM, DLP, retention, audit, telemetry, HA, DR, or secrets-management architecture is implemented end to end.

## 14. Production Security Requirements

Before treating a derivative system as production capable, design and verify at least:

- centralized identity and least-privilege RBAC,
- service identities and managed secret storage,
- environment separation and deployment approvals,
- Power Platform DLP and tenant governance,
- transactional persistence and concurrency control,
- evidence classification and retention,
- immutable audit logging,
- monitoring/alerting and incident response,
- authenticated and authorized APIs,
- TLS/gateway/rate limiting where applicable,
- Power BI Service/Fabric access model and RLS,
- AI provider approval, transfer assessment, model/data governance, and runtime controls,
- backup/restore and disaster-recovery procedures,
- vulnerability/dependency management,
- documented ownership and operational support.

## 15. Final Security Statement

The completed lab demonstrates explicit trust boundaries, minimization, fail-safe handling, deterministic validation, human authority, and honest limitation disclosure.

It is not production-ready and does not claim compliance certification. Its security value lies in making authority, data movement, trust, failure behavior, and residual risk visible and reviewable.
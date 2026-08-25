# Production Gap Assessment

## Document Role

**PHASE 11 HANDOVER — PROOF-OF-CONCEPT TO PRODUCTION GAP ANALYSIS**

Documentation index: [README.md](README.md)

## Purpose

This document distinguishes what the Cyber Governance Automation Lab actually implements from capabilities that would be required for a production cybersecurity-governance platform.

The project is intentionally a portfolio proof of concept. The table below is not a roadmap commitment and does not imply that adding every listed control would automatically make the system production-ready.

## Assessment Matrix

| Area | Implemented PoC state | Production requirement / gap |
| --- | --- | --- |
| Domain model | Four explicit entities: Control, Submission, Action, Data Quality Issue | Versioned schemas, lifecycle governance, migration strategy, ownership model |
| Expected state | Expected Submissions exist before evidence | Automated period generation, scheduling ownership, calendar/version handling |
| Operational persistence | Excel Online / OneDrive tables | Transactional datastore, concurrency control, constraints, backup/restore, HA |
| Evidence intake | Authenticated Microsoft Forms + Power Automate | Formal authorization model, input validation strategy, attachment/evidence repository, audit trail |
| Compliance authority | Human Governance Reviewer | Formal approval workflow, delegated authority, segregation of duties, audit evidence |
| Data Quality | Deterministic Submission DQ-001 through DQ-010 | Broader data-domain validation, Action validation, reference-data governance, quality observability |
| Reminder workflow | Scheduled overdue detection, Action create/reuse, same-day idempotency | SLA/escalation hierarchy, calendars, retries, queueing, operational dashboards, ownership fallback |
| Snapshot bridge | Three private source snapshots + manifest written last | Transactionally coherent extraction or governed CDC/ELT, manifest ingestion, automated orchestration |
| Python runtime | Deterministic CLI pipeline | Managed execution environment, scheduling, monitoring, retries, artifact retention, deployment pipeline |
| Reporting | Source-controlled PBIP/PBIR/TMDL, 21 measures, 3 pages | Power BI Service/Fabric deployment, RLS, workspace governance, refresh monitoring, promotion pipeline |
| AI workflow | Minimized deterministic candidates, controlled prompt/schema, human review | Approved provider runtime, contractual/privacy assessment, model governance, logging, evaluation, content controls |
| Prompt injection | Explicit untrusted-input prompt + synthetic adversarial acceptance | Continuous red-team/evaluation program; no universal resistance claim |
| AI write-back | Not implemented | If ever added: authorization, approval, audit, rollback, safety gates, policy enforcement |
| REST API | Local loopback, read-only, canonical synthetic data, 2 fields | Authentication, authorization, TLS, gateway, rate limits, telemetry, deployment, lifecycle/versioning |
| REST client | Timeout, HTTP/JSON/shape handling | Retry/backoff policy, observability, auth/token handling, service discovery, resilience policy |
| Identity | Synthetic public identities; private operational identities kept out of Git | Central IdP, service identities, least privilege, joiner/mover/leaver controls |
| Secrets | No secrets committed; placeholders in sanitized workflow source | Managed secret store, rotation, workload identity, secret scanning and response process |
| DLP / privacy | Explicit public/private boundary | Formal classification, DLP, retention, deletion, data-transfer and legal assessment |
| Audit | Git history, CI history, workflow run history, deterministic outputs | Centralized immutable audit trail with retention and access governance |
| Monitoring | Component-level run/test feedback | Central metrics, logs, traces, SLOs, alert routing, incident response integration |
| CI | GitHub Actions full Python suite | Required protected checks, review policy, dependency/security gates, release governance |
| Dependencies | Top-level requirements plus Phase 11 accepted lock file | Automated dependency updates, vulnerability policy, SBOM/provenance/signing where required |
| Deployment | Manual/local and tenant-specific operational setup | Environment promotion, infrastructure/configuration as code, approvals, rollback, release management |
| Availability / DR | Not designed as HA service | RTO/RPO, redundancy, backup validation, failover, recovery exercises |

## Priority Production Gaps

If this PoC were evolved into a real internal platform, the first engineering priorities should be:

1. **Replace Excel as the authoritative state store.** Use a transactional persistence layer with enforced keys, constraints, concurrency control, and auditability.
2. **Establish identity and authorization.** Define users, service identities, roles, least privilege, and segregation of duties before exposing write-capable services.
3. **Formalize evidence storage and privacy.** Separate evidence metadata from protected evidence content and define classification, access, retention, and deletion.
4. **Make extraction and execution operationally reliable.** Replace manual snapshot-to-CLI handoff with coherent ingestion/orchestration, monitored scheduling, retries, and provenance.
5. **Deploy reporting under governed access.** Introduce managed Power BI/Fabric workspaces, RLS where required, refresh monitoring, and environment promotion.
6. **Treat AI as a governed external dependency.** Only add provider runtime after privacy/security/legal approval, evaluation criteria, monitoring, and human-control design are defined.
7. **Secure the API before network exposure.** Authentication, authorization, TLS, gateway policy, telemetry, abuse controls, and version management are prerequisites for anything beyond loopback PoC use.
8. **Enforce delivery controls.** Protected branches, required CI, dependency management, security scanning appropriate to risk, and release governance should become mandatory.

## What Should Not Be Inferred

The following claims are unsupported and must not be made from this repository:

```text
production ready
enterprise ready
certified secure
compliant with a named regulation or standard
universally prompt-injection resistant
fully automated governance
AI makes compliance decisions
zero-trust architecture implemented
high availability implemented
```

## Conclusion

The completed PoC demonstrates architecture separation, deterministic processing, workflow guardrails, reporting, AI governance boundaries, and local API integration. Its production value is primarily architectural and educational: it makes the next engineering controls explicit rather than hiding them behind a generic `production-ready` claim.
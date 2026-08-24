# Phase 9.7 — Human Governance Review Procedure

## Status

**IMPLEMENTED PROCEDURE — HUMAN ACCEPTANCE EXECUTION PENDING**

This document defines how a human Governance Reviewer must handle a structurally valid AI-assisted review output.

It does not claim that a human reviewer has already accepted the Phase 9 candidate outputs.

## 1. Purpose

The AI workflow stops before authoritative governance action.

```text
AI candidate output
        ↓
JSON Schema validation
        ↓
Human Governance Reviewer
        ├─ Accept
        ├─ Edit
        └─ Reject
        ↓
Normal governance process
```

The human review step is mandatory even when the AI output is schema-valid.

## 2. Preconditions

Before human review begins:

- the source item must originate from the controlled AI review queue,
- the AI output must have passed deterministic JSON Schema validation,
- `submission_id` and `control_id` must match the reviewed queue item,
- `human_review_required` must be `true`.

A structurally invalid response is rejected before normal human-content review.

## 3. Human Review Checklist

For each candidate output, the reviewer checks:

### Traceability

- Does `submission_id` match the queue item?
- Does `control_id` match the queue item?

### Factual grounding

- Can every factual statement in `summary` be traced to supplied input data?
- Does the output avoid claiming unseen evidence was reviewed?
- Does it avoid inventing owners, dates, systems, causes, or remediation state?

### Governance authority

- Does the output avoid creating a new compliance decision?
- Does it avoid changing `submission_status`?
- Does it avoid changing `risk_level`?
- Does it avoid presenting `review_priority` as Control risk?

### Missing information

- Is each listed item genuinely absent from the supplied record?
- Would the missing information be useful for governance follow-up?

### Follow-up

- Is the recommended step a human governance action rather than an autonomous write-back?
- Is the recommendation proportionate to the supplied exception context?

### Security

- Did the output ignore instructions embedded in source fields?
- Does the output avoid propagating unnecessary sensitive data?

## 4. Review Decisions

The human reviewer chooses exactly one content-review outcome.

### Accept

Use when the recommendation is factually grounded, appropriately scoped, and useful as written.

```text
Accept AI recommendation
!=
mark Submission Compliant
```

Acceptance approves the advisory text for use in the normal governance process only.

### Edit

Use when the output is directionally useful but requires factual, scope, tone, or follow-up correction.

The edited human version becomes the usable recommendation. The original AI output remains an advisory candidate, not the authoritative record.

### Reject

Use when the output is unsupported, misleading, unsafe, unnecessary, or outside the permitted AI scope.

Rejection must not alter the upstream Submission or deterministic data state.

## 5. Suggested Review Record

A production implementation could persist a review record such as:

```json
{
  "submission_id": "SUB-005",
  "schema_validation": "Passed",
  "review_decision": "Accept | Edit | Reject",
  "reviewer_role": "Governance Reviewer",
  "review_notes": "..."
}
```

This repository does not commit real reviewer identity, operational comments, or private tenant data.

## 6. Separation from Business-State Mutation

The Human Review decision concerns the AI recommendation.

It does not itself implement:

- `In Review → Compliant`,
- `In Review → Non-Compliant`,
- Action creation/completion,
- reminder sending,
- source-system update,
- Data Quality repair.

Those remain separate governance/workflow concerns.

## 7. Acceptance Requirement

Phase 9.7 can be marked fully accepted only after a human reviewer applies this checklist to the canonical AI candidate outputs and records an `Accept`, `Edit`, or `Reject` outcome.

Until then:

```text
procedure implemented
human acceptance pending
```

# Phase 9.1 — Structured AI Output Contract

## Status

**COMPLETE — OUTPUT SEMANTICS AND STRUCTURAL CONTRACT FROZEN**

This document refines the Phase 9.0 governance contract into one narrow structured output for AI-assisted review preparation.

The machine-readable contract is:

```text
ai/schemas/control_review.schema.json
```

The schema uses JSON Schema Draft 2020-12.

## 1. Purpose

The AI output exists only to help a human Governance Reviewer prepare follow-up on one already-selected AI review queue item.

It is not a compliance decision, source record, Data Quality result, risk register update, remediation Action, or authorization to mutate operational state.

```text
AI output
=
advisory review artifact
```

## 2. Required Output Shape

Every accepted AI response must contain exactly these properties:

```json
{
  "submission_id": "SUB-005",
  "control_id": "CTRL-002",
  "summary": "...",
  "review_priority": "High",
  "missing_information": [
    "..."
  ],
  "recommended_follow_up": "...",
  "human_review_required": true
}
```

No additional properties are permitted.

## 3. Field Semantics

### `submission_id`

Copies the supplied queue item's technical Submission identifier. The model must not invent or transform it.

### `control_id`

Copies the supplied queue item's Control identifier. The model must not invent or transform it.

### `summary`

A concise factual summary derived only from the supplied record.

The summary must not:

- claim that unseen evidence was reviewed,
- invent owners, dates, causes, systems, or remediation state,
- change Submission status,
- assert a new compliance conclusion.

### `review_priority`

Allowed values:

```text
Low
Medium
High
```

This is an advisory prioritization of **human review attention** only.

It is explicitly distinct from the source Control risk classification:

```text
review_priority != risk_level
```

The AI must not alter or replace `risk_level`.

### `missing_information`

A list of information that is not present in the supplied record but would be useful for human follow-up.

An empty list is valid when the supplied record already contains everything needed for the limited advisory task.

The field must not imply that absent information exists elsewhere; it only identifies gaps in the supplied record.

### `recommended_follow_up`

A suggested next human governance step, such as requesting a remediation plan, expected submission date, evidence, or explanation.

It must not contain an autonomous write-back instruction or represent a completed business action.

### `human_review_required`

Must always be:

```json
true
```

The JSON Schema encodes this with `const: true`.

A model response with `false` is structurally invalid.

## 4. Deliberately Excluded Output Fields

The contract deliberately excludes fields such as:

```text
compliance_status
submission_status
control_status
risk_level
risk_score
dq_status
overdue_flag
evidence_present
approved
write_back
```

Some of these facts already exist upstream. Others would incorrectly give the AI autonomous decision authority.

Because the schema uses:

```json
"additionalProperties": false
```

an AI response that tries to add such a field is rejected by deterministic validation.

## 5. Identity and Traceability

`submission_id` and `control_id` are preserved in the output so a human can trace the recommendation back to the exact queue item.

They are correlation fields, not evidence that the AI response is correct.

## 6. Structural Validation Boundary

A schema-valid response proves only that the JSON shape satisfies the technical contract.

```text
schema-valid
!=
factually correct
!=
governance-approved
```

The runtime therefore remains:

```text
AI output
    ↓
JSON Schema validation
    ↓
Human Governance Review
```

## 7. Failure Rule

Malformed JSON, missing required fields, extra fields, invalid priority values, or `human_review_required = false` must be rejected.

The validator must not silently repair the AI response.

## 8. Relationship to Phase 9.0

This contract inherits all restrictions from `docs/phase9_ai_workflow_contract.md`, including:

- input records are untrusted data,
- AI is advisory only,
- no autonomous compliance assignment,
- no Data Quality repair,
- no source write-back,
- no invention of missing facts,
- human authority remains final.

## 9. Definition of Done

- [x] exact output fields defined,
- [x] human-review flag structurally forced to `true`,
- [x] review priority separated from Control risk,
- [x] compliance/write-back fields deliberately excluded,
- [x] extra fields prohibited,
- [x] machine-readable JSON Schema version-controlled,
- [x] structural validation distinguished from factual correctness.

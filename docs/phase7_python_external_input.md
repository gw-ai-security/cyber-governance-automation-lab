# Phase 7.3 — Python External Input Boundary

## Status

**PYTHON EXTERNAL INPUT BOUNDARY IMPLEMENTED AND AUTOMATED-TESTED**

Phase 7.3 connects private source snapshots produced by the acceptance-tested Phase 7.2 Power Automate flow to the existing Python pipeline.

The subsequent WP3 real-snapshot acceptance has now also completed successfully. Full Phase 7 is therefore complete; this document remains the Phase 7.3 implementation and automated-test record.

## Purpose

The Python CLI can process either:

```text
canonical repository fixtures
```

or:

```text
one explicitly supplied Control / Submission / Action snapshot set
```

Both modes reuse:

```text
EXTRACT → NORMALIZE → VALIDATE → TRANSFORM / ENRICH → DERIVE → LOAD
```

No operational snapshot is copied over canonical repository fixtures.

## CLI Contract

Phase 7.3 added:

```text
--controls-path
--submissions-path
--actions-path
--output-directory
```

`--as-of-date` remains the explicit temporal evaluation parameter.

### Canonical mode

With no source overrides:

```text
controls    = data/reference/control_catalog.json
submissions = data/raw/evidence_submissions.csv
actions     = data/raw/actions.csv
outputs     = data/curated/
```

Example:

```bash
python src/main.py --as-of-date 2026-08-15
```

`--output-directory` may be used independently while retaining all canonical inputs.

### External snapshot mode

```bash
python src/main.py \
  --as-of-date 2026-08-23 \
  --controls-path "/private/snapshots/security_control_snapshot_<id>.json" \
  --submissions-path "/private/snapshots/security_submission_snapshot_<id>.csv" \
  --actions-path "/private/snapshots/security_action_snapshot_<id>.csv" \
  --output-directory "/private/processed/<id>"
```

External files are read directly. They are not copied, renamed, mutated, or written into `data/reference/` or `data/raw/`.

## All-or-None Source Rule

The source-path options form one coherent set:

```text
none supplied      → use all three canonical defaults
all three supplied → use all three explicit paths
partial set        → reject before pipeline processing
```

This prevents operational Submission or Action state from being combined silently with canonical synthetic sources.

`--output-directory` is independent.

## Error Behavior

Fatal physical/input-contract failures remain non-zero execution failures, including:

- explicitly requested file missing,
- malformed JSON or CSV,
- missing/unexpected/incorrectly ordered CSV columns,
- duplicate Control technical identifiers rejected by Extract,
- partial external source-path sets.

An explicitly requested external source never falls back to its canonical equivalent.

Submission Data Quality findings remain normal business outputs:

```text
DQ finding → exit code 0 + DQ output
```

Invalid Submission rows remain visible in curated reporting.

## Snapshot Time and Manifest Boundary

Phase 7.3 intentionally does not automatically consume, discover, or select a manifest.

It does not infer:

- latest snapshot,
- snapshot directory,
- filenames,
- `as_of_date`.

The caller reads the matching completion manifest and passes its `as_of_date` through:

```text
--as-of-date
```

This keeps snapshot provenance explicit without expanding Phase 7.3 into a storage/discovery integration service.

## Empty Action Snapshot

A header-only Action CSV with the exact ten-column header is valid.

Automated acceptance proved:

```text
Actions loaded: 0
```

while preserving Submission grain and existing output contracts.

## Automated Acceptance Coverage

Black-box subprocess tests prove:

- exact canonical `5 / 15 / 5` source behavior,
- distinct synthetic external `EXT-*` source paths are actually used,
- Action reminder state reaches curated output,
- one intended DQ finding remains non-fatal,
- invalid rows remain visible,
- explicit `as_of_date` drives overdue calculations,
- custom output routing is exclusive,
- external and canonical source files remain byte-identical,
- all six non-empty partial source combinations are rejected,
- missing external files do not fall back,
- malformed external physical contracts fail,
- header-only Action CSV is supported,
- custom output works in canonical source mode,
- fatal external-input errors do not produce a misleading complete output set.

Final Phase 7.3 test state at merge:

```text
focused CLI tests: 18 passed
complete suite:     53 passed
```

Canonical acceptance remained:

```text
Controls loaded: 5
Submissions loaded: 15
Actions loaded: 5
DQ issues: 5
Valid submissions: 10
Invalid submissions: 5
AI review queue items: 2
```

## Security and Privacy Boundary

- private operational snapshots remain outside GitHub,
- tests use synthetic `EXT-*` identifiers and `example.com` identities,
- canonical fixtures remain unchanged,
- output may be written to a private location outside the repository,
- Phase 7.2 sanitized workflow source remains unchanged,
- no OneDrive, Graph, or live tenant dependency exists in the tests.

## Scope Limitations

Phase 7.3 intentionally does not add:

- automatic manifest parsing,
- automatic snapshot discovery,
- latest-snapshot selection,
- automatic `as_of_date` inference,
- OneDrive or Microsoft Graph calls,
- Power Automate API calls,
- transactional guarantees across Excel source reads,
- automatic Python scheduling,
- Power BI functionality.

It also does not add or change business rules, DQ rule IDs, Action lifecycle semantics, curated columns, or AI queue policy.

## Subsequent WP3 Acceptance

After Phase 7.3 merged, the new boundary was exercised with a real private complete operational snapshot.

Observed source-count reconciliation:

```text
Manifest: Controls 5 / Submissions 17 / Actions 2
Python:   Controls 5 / Submissions 17 / Actions 2
```

Observed operational processing:

```text
DQ issues: 5
Valid submissions: 12
Invalid submissions: 5
AI review queue items: 3
```

Phase 6 reminder facts crossed into curated reporting, and the canonical `2026-08-15` regression remained exactly unchanged. The complete suite remained 53 passing tests and the working tree remained clean.

See [phase7_end_to_end_acceptance.md](phase7_end_to_end_acceptance.md).

**Phase 7.3 status: COMPLETE**

**Full Phase 7 status: COMPLETE**

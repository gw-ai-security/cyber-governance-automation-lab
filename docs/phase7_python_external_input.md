# Phase 7.3 — Python External Input Boundary

## Status

**PYTHON EXTERNAL INPUT BOUNDARY IMPLEMENTED AND AUTOMATED-TESTED**

Phase 7.3 connects the private source snapshots produced by the
acceptance-tested Phase 7.2 Power Automate flow to the existing Python
pipeline. Full Phase 7 is not complete: WP3 still requires one private
operational snapshot to be processed end to end and reconciled with its
manifest.

## Purpose

The Python CLI can now process either the deterministic repository fixtures
or one explicitly supplied Control / Submission / Action snapshot set. Both
modes use the same pipeline:

```text
EXTRACT → NORMALIZE → VALIDATE → TRANSFORM / ENRICH → DERIVE → LOAD
```

No operational snapshot is copied into or substituted for the canonical
repository fixtures.

## CLI Contract

Phase 7.3 adds exactly:

```text
--controls-path
--submissions-path
--actions-path
--output-directory
```

All path arguments are parsed as filesystem paths. `--as-of-date` remains the
explicit temporal evaluation parameter.

### Canonical mode

With no source-path overrides, the existing defaults remain:

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

`--output-directory` may be used independently while retaining all three
canonical inputs:

```bash
python src/main.py \
  --as-of-date 2026-08-15 \
  --output-directory "/private/processed/canonical-check"
```

### External snapshot mode

An external run supplies all three source paths and may select a private
output directory:

```bash
python src/main.py \
  --as-of-date 2026-08-23 \
  --controls-path "/private/snapshots/security_control_snapshot_<id>.json" \
  --submissions-path "/private/snapshots/security_submission_snapshot_<id>.csv" \
  --actions-path "/private/snapshots/security_action_snapshot_<id>.csv" \
  --output-directory "/private/processed/<id>"
```

The external files are read directly. They are not copied, renamed, mutated,
or written into `data/reference/` or `data/raw/`.

## All-or-None Source Rule

The three source-path options form one coherent source set:

```text
none supplied      → use all three canonical defaults
all three supplied → use all three explicit paths
partial set        → reject before pipeline processing
```

This prevents live Submission or Action state from being combined silently
with canonical synthetic reference data.

`--output-directory` is independent of this rule. When supplied, the pipeline
writes the three contractual outputs only to that directory:

```text
curated_control_status.csv
data_quality_issues.csv
ai_review_queue.json
```

It does not additionally write them to `data/curated/`.

## Error Behavior

Fatal physical or input-contract failures retain non-zero process exit
semantics, including:

- a requested file does not exist,
- malformed JSON or CSV,
- missing, unexpected, or incorrectly ordered CSV columns,
- duplicate Control technical identifiers rejected by Extract,
- a partial external source-path set.

An explicitly requested file never falls back to its canonical equivalent.
Fatal input failures occur before a successful three-file output set is
written.

Submission Data Quality findings remain successful business outputs. A run
with DQ findings exits with code `0`, writes `data_quality_issues.csv`, retains
invalid Submission rows in curated output, and excludes invalid rows from the
controlled AI review queue according to the existing policy.

## Snapshot Time and Manifest Boundary

Phase 7.3 does not automatically consume or discover a Phase 7 manifest. It
does not infer the latest snapshot, snapshot directory, filenames, or
`as_of_date`.

The caller must read the matching manifest and pass its `as_of_date` explicitly
through `--as-of-date`. The supplied value drives overdue calculations and the
AI queue's `as_of_date` exactly.

## Security and Privacy Boundary

- Private operational snapshots remain outside GitHub.
- No operational workbook or snapshot is committed as a test fixture.
- Tests use only synthetic `EXT-*` identifiers and `example.com` identities.
- Canonical fixtures remain unchanged.
- Output paths can point to a private location outside the repository.
- Phase 7.2 source-control sanitization and deployment placeholders remain
  unchanged.

## Automated Acceptance Coverage

Black-box subprocess tests prove:

- exact canonical 5 / 15 / 5 regression behavior,
- distinct `EXT-*` source paths are actually used,
- explicit Action state reaches curated output,
- one intended DQ-003 finding remains non-fatal,
- invalid Submission rows remain visible,
- the explicit as-of date produces exactly five overdue days,
- output-directory routing is exclusive,
- external and canonical source files remain byte-identical,
- all six non-empty partial source combinations are rejected,
- missing external files do not fall back,
- malformed external physical contracts fail,
- a header-only Action CSV loads as zero Actions without changing Submission
  grain,
- a custom output directory also works in canonical source mode,
- fatal external-input errors do not produce a misleading complete output set.

The external fixture is generated inside pytest temporary directories; no
private snapshot content is committed.

## Known Limitations and Remaining Phase 7 Work

Phase 7.3 intentionally does not add:

- manifest parsing or validation,
- automatic snapshot discovery or latest-snapshot selection,
- automatic `as_of_date` inference,
- OneDrive, Microsoft Graph, or Power Automate API calls,
- transactional guarantees across the three Excel source-table reads,
- automatic scheduling of Python processing,
- Power BI implementation.

WP3 remains pending. It must process one real private operational snapshot,
reconcile manifest row counts with Python load counts, verify live Phase 6
reminder state in curated reporting, and rerun the canonical regression without
mutating repository fixtures. Until that acceptance is complete, full Phase 7
must not be marked complete and Phase 8 has not started.

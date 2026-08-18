# Cyber Governance Automation Lab

Security Control Evidence, Follow-up & Reporting Automation

## Project Overview

The Cyber Governance Automation Lab is a small portfolio proof of concept for automating recurring cybersecurity control evidence processes.

The project demonstrates how Microsoft Power Automate, Python, Power BI, CSV/JSON data processing, data quality checks, and controlled AI-assisted workflows can be combined into a simple end-to-end governance process.

The solution is intentionally limited in scope. Its purpose is to demonstrate process understanding, automation, data integration, reporting, testing, and documentation rather than to simulate a production-ready enterprise platform.

## Business Problem

Cybersecurity governance teams often depend on recurring control confirmations, evidence submissions, manual follow-ups, and management reporting.

Without automation, a typical process may involve:

- maintaining control information in spreadsheets,
- contacting control owners manually,
- collecting evidence through emails or files,
- checking whether required information is complete,
- identifying overdue submissions,
- sending reminders,
- updating tracking data,
- preparing management reports manually.

This creates several risks and inefficiencies:

- missing or incomplete evidence,
- inconsistent data,
- overdue submissions,
- repeated manual follow-up,
- weak process traceability,
- time-consuming reporting.

The target solution is designed as a simplified workflow in which evidence submissions are collected and processed through Power Automate, validated and transformed with Python, reported through Power BI, and selectively prepared for controlled AI-assisted review.

## Current Implementation Status

The repository currently includes:

- project foundation and repository structure,
- architecture documentation,
- business-process definition,
- data model,
- raw flat-file data contract,
- data-quality rule catalog,
- canonical synthetic Control Catalog,
- synthetic Submission dataset,
- synthetic Action dataset,
- Phase 2 dataset coverage / validation matrix,
- Phase 3.0 Python pipeline and output contract,
- executable Extract, Normalize/Transform, and Submission Validate modules,
- deterministic curated-data and controlled AI-queue builders,
- automated tests for the implemented Phase 3 scope.

Phase 0 through Phase 2 are complete. Phase 3 is in progress: the contract, Extract, Normalize/Transform, and Submission Validate stages are implemented and covered by automated tests. The canonical Phase 2 dataset produces the five documented Data Quality issues and the expected derived results.

The remaining Phase 3 implementation steps are:

- output serialization in `src/load.py`,
- orchestration and command-line handling in `src/main.py`,
- an executable end-to-end run that writes all three contractual outputs.

The following components remain planned and will be implemented incrementally:

- Power Automate workflows,
- Power BI dashboard,
- controlled AI runtime workflow,
- mock REST API.

## Source of Truth

Historical initial project briefs and plans provide background context only. The current canonical business and technical definitions are the repository documents linked below together with [data/reference/control_catalog.json](data/reference/control_catalog.json). If a historical brief conflicts with these current artifacts, the repository documentation and canonical Control Catalog take precedence.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the initial system architecture.

## Tech Stack

- Python and pandas for flat-file extraction, validation, transformation, and derivation,
- pytest for automated verification,
- JSON and CSV for the current synthetic inputs and contractual outputs.

Power Automate, Power BI, FastAPI, and the controlled AI runtime are target components; they are not implemented merely because their dependencies or placeholder directories exist.

## Business Process

The project models a recurring control evidence process: control ownership, periodic submissions per reporting period, status assessment, timeliness evaluation, and data-quality validation.

See [docs/business_process.md](docs/business_process.md) for the detailed process definition.

## Data Model

The data model defines stable control definitions, recurring submissions, follow-up actions, derived metrics, and data-quality issues.

See [docs/data_model.md](docs/data_model.md) for the detailed data model.

See [docs/data_contract.md](docs/data_contract.md) for the physical flat-file representation of raw Submission and Action data.

## Power Automate Workflows

Planned. No Power Automate workflow export is implemented in the repository yet.

## Python Pipeline

Phase 3 uses the explicit processing model:

```text
EXTRACT
   ↓
NORMALIZE
   ↓
VALIDATE
   ↓
TRANSFORM / ENRICH
   ↓
DERIVE
   ↓
LOAD
```

The Phase 3.0 contract fixes the exact inputs, output schemas, module responsibilities, Data Quality issue emission semantics, Action aggregation behavior, deterministic `as_of_date` execution, and AI review queue policy. `src/extract.py`, `src/transform.py`, and `src/validate.py` implement the currently completed portion of that contract.

See [docs/phase3_pipeline_contract.md](docs/phase3_pipeline_contract.md) for the canonical Phase 3 implementation contract.

## Data Quality

The project applies explicit validation rules covering completeness, referential integrity, validity, consistency, and uniqueness.

See [docs/data_quality.md](docs/data_quality.md) for the rule catalog.

See [docs/phase2_dataset_coverage.md](docs/phase2_dataset_coverage.md) for the deterministic Phase 2 dataset validation matrix.

## Power BI Dashboard

Planned. No Power BI report artifact is implemented in the repository yet.

## Controlled AI Workflow

The deterministic, data-minimized AI review queue builder is implemented in Python. External model invocation and human-review workflow integration remain planned.

## Security Considerations

- repository datasets and identities are synthetic,
- evidence is represented only by references; no evidence files are stored,
- credentials and secrets must not be committed,
- AI-assisted output remains advisory and cannot assign compliance status autonomously.

## How to Run

Create a virtual environment, install `requirements.txt`, and run the automated verification from the repository root:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

The contractual `python src/main.py --as-of-date YYYY-MM-DD` command is not available yet because serialization and orchestration remain open Phase 3 work.

## Testing

The automated test suite covers:

- exact Extract schemas and raw-string preservation,
- technical normalization and source-row lineage,
- DQ-001 through DQ-010, dependency behavior, ordering, and deterministic issue IDs,
- canonical Phase 3 acceptance counts and findings,
- row-preserving Control enrichment, Action aggregation, timing metrics, and AI queue selection.

The canonical regression uses `as_of_date = 2026-08-15` and must produce 5 Data Quality issues, 10 valid Submissions, 5 invalid Submissions, and 2 AI review queue items.

## Limitations

- no output serialization or command-line orchestration yet,
- no committed curated output files until the contractual loader exists,
- no Action-specific DQ rule IDs; the canonical Action dataset is treated as trusted synthetic workflow input after structural parsing,
- flat-file proof of concept rather than a production data platform.

## Screenshots

No UI or dashboard screenshots are included at the current implementation stage.

## Learning Outcomes

The implemented scope demonstrates explicit data contracts, raw-value preservation, deterministic Data Quality evaluation, source-row lineage, row-preserving enrichment, reproducible time-based metrics, and automated regression testing without conflating compliance, timeliness, and data quality.

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
- canonical synthetic Control Catalog.

The following components are planned and will be implemented incrementally:

- synthetic Submission and Action datasets,
- Python ETL and Data Quality pipeline,
- unit tests,
- Power Automate workflows,
- Power BI dashboard,
- controlled AI workflow,
- mock REST API.

## Source of Truth

Historical initial project briefs and plans provide background context only. The current canonical business and technical definitions are the repository documents linked below together with [data/reference/control_catalog.json](data/reference/control_catalog.json). If a historical brief conflicts with these current artifacts, the repository documentation and canonical Control Catalog take precedence.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the initial system architecture.

## Tech Stack

## Business Process

The project models a recurring control evidence process: control ownership, periodic submissions per reporting period, status assessment, timeliness evaluation, and data-quality validation.

See [docs/business_process.md](docs/business_process.md) for the detailed process definition.

## Data Model

The data model defines stable control definitions, recurring submissions, follow-up actions, derived metrics, and data-quality issues.

See [docs/data_model.md](docs/data_model.md) for the detailed data model.

See [docs/data_contract.md](docs/data_contract.md) for the physical flat-file representation of raw Submission and Action data.

## Power Automate Workflows

## Python Pipeline

## Data Quality

The project applies explicit validation rules covering completeness, referential integrity, validity, consistency, and uniqueness.

See [docs/data_quality.md](docs/data_quality.md) for the rule catalog.

## Power BI Dashboard

## Controlled AI Workflow

## Security Considerations

## How to Run

## Testing

## Limitations

## Screenshots

## Learning Outcomes

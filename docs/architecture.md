# Architecture

## Purpose

This document describes the initial architecture of the Cyber Governance Automation Lab.

It is a simplified cybersecurity control evidence process built as a portfolio proof of concept. The system is not production-ready. Its focus is a small, traceable, end-to-end data flow rather than a fully engineered platform.

## High-Level Architecture

```mermaid
flowchart TD
    A[Microsoft Forms] --> B[Power Automate]
    B --> C[Excel Online / OneDrive]
    C --> D[Raw Submission CSV]
    D --> F[Python ETL]
    E[Control Catalog JSON] --> F
    F --> G[Curated CSV]
    G --> H[Power BI]
    F --> I[AI Review Queue JSON]
    I --> J[Controlled AI Review]
    J --> K[Structured JSON Output]
```

The physical representation of the Raw Submission CSV is defined in the [Raw Data Contract](data_contract.md). The Control Catalog JSON provides the stable control reference data joined by Python ETL.

## Expected Submission Initialization and Evidence Updates

For the proof of concept, expected Submission records are pre-generated from the Control Catalog for the relevant synthetic reporting periods. Each record is seeded in the Submission Register with status `Not Submitted`. This gives the reminder workflow a record to evaluate even when a Control Owner submits nothing.

```mermaid
flowchart TD
    A[Control Catalog] --> C[Seed Expected Submissions for Synthetic Reporting Periods]
    B[Relevant Synthetic Reporting Periods] --> C
    C --> D[Submission Register: Not Submitted]
    E[Evidence Received through Microsoft Forms] --> F[Find Expected Submission by control_id and reporting_period]
    D --> F
    F --> G[Update Existing Submission to In Review]
```

The later Power Automate evidence-intake workflow must find the existing expected Submission by the `control_id + reporting_period` business key and update it. It must not blindly append another Submission row. A future extended design could automate period initialization with a scheduled flow, but that implementation is outside the current phase.

## Scheduled Reminder Workflow

```mermaid
flowchart TD
    A[Scheduled Flow] --> B[Read Submission Register]
    A --> C[Read Control Catalog]
    B --> D[Identify Overdue Submissions]
    C --> D
    D --> E[Resolve Control Owner]
    E --> F[Resolve or Create Follow-up Action]
    F --> G[Send Reminder]
    G --> H[Update Action Reminder Tracking]
```

For the proof of concept, reminder tracking is stored on the follow-up Action associated with the overdue Submission. The scheduled workflow reuses the Submission's existing non-completed Action or creates one when none exists. After sending a reminder, it increments `Action.reminder_count` and sets `Action.last_reminder_at` to the processing date. Synthetic Action data must therefore contain at most one non-completed Action per Submission.

## Component Responsibilities

### Microsoft Forms

* Collects evidence submissions from control owners.

### Power Automate

* Processes evidence submissions.
* Validates required information.
* Writes data to the central register.
* Sends confirmations.
* Identifies overdue submissions.
* Sends reminders.
* Creates reporting snapshots.

### Excel Online / OneDrive

* Excel Online provides the tabular control register used by the workflow.
* OneDrive provides the underlying file storage for the portfolio proof of concept.
* This combination is chosen deliberately for its low complexity and direct Power Automate integration.
* For a production environment, Dataverse, SharePoint Lists, or a relational database would be more appropriate.

### Python

* Reads CSV and JSON data.
* Normalizes values.
* Applies data quality rules.
* Merges control reference data with submission data.
* Computes derived fields.
* Produces a curated reporting dataset.
* Produces structured AI review inputs.

### Power BI

* Provides governance and management reporting based on curated data.

### Controlled AI Workflow

* May summarize supplied control information.
* May identify missing information.
* May recommend follow-up actions.
* May not autonomously assign `Compliant` status to a Submission.
* Human review is mandatory.

## Architecture Principles

* Small and modular design.
* Explicit component responsibilities.
* Synthetic data only.
* No credentials or secrets in the repository.
* Human-in-the-loop for AI-assisted decisions.
* Data quality checks before reporting.
* Simple technology choices over unnecessary enterprise complexity.

## Business Model Reference

The technical architecture implements the governance process and data model defined in:

* [business_process.md](business_process.md)
* [data_model.md](data_model.md)
* [data_contract.md](data_contract.md)
* [data_quality.md](data_quality.md)

## Out of Scope

* SIEM
* SOC operations
* Malware analysis
* Penetration testing
* Machine learning
* Kubernetes
* Kafka
* Spark
* Complex cloud infrastructure
* Custom frontend
* Enterprise authentication architecture

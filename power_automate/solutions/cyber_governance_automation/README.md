# Cyber Governance Automation Lab — Power Automate Solution Source

This directory contains a **sanitized, source-controlled representation** of the Phase 7 Power Automate solution.

The private tenant export is not committed. It contains environment-specific bindings such as OneDrive/Excel resource identifiers and a reachable notification recipient. The repository version preserves the workflow structure, connector types, expressions, scopes, serialization logic, error handling, and ALM shape while replacing environment-specific values with explicit placeholders.

## Scope

Solution:

```text
CyberGovernanceAutomationLab
```

Cloud flow:

```text
Cyber Governance - Weekly Reporting Snapshot
```

Runtime schedule:

```text
Weekly
Monday
09:00
W. Europe Standard Time
```

The flow exports:

```text
ControlCatalog     → security_control_snapshot_<snapshot_id>.json
SubmissionRegister → security_submission_snapshot_<snapshot_id>.csv
ActionRegister     → security_action_snapshot_<snapshot_id>.csv
                     security_snapshot_manifest_<snapshot_id>.json
```

The manifest is created last and is the completion marker for a valid snapshot package.

## Source-Control Boundary

The files in this directory are intentionally sanitized.

Replaced values include:

```text
<ENV_DRIVE_ID>
<ENV_WORKBOOK_FILE_ID>
<ENV_CONTROL_TABLE_ID>
<ENV_SUBMISSION_TABLE_ID>
<ENV_ACTION_TABLE_ID>
phase7-alerts@example.com
```

Connection-reference logical names are normalized to stable repository placeholders:

```text
gw_sharedexcelonlinebusiness_reporting
gw_sharedonedriveforbusiness_reporting
gw_sharedoffice365_reporting
```

These values are not the private tenant deployment bindings.

The operational workbook, private snapshot files, exported tenant Solution ZIP files, connection credentials, and reachable notification recipient are not committed.

## Files

```text
workflow.template.json
deployment-template.json
```

The workflow template preserves:

- scheduled recurrence,
- snapshot ID / as-of-date / local timestamp expressions,
- Excel reads for all three source tables,
- ISO 8601 date handling,
- pagination configuration,
- deterministic Select mappings,
- Control JSON serialization,
- Submission and Action CSV serialization,
- snapshot file creation,
- row counts,
- completion manifest construction,
- TRY/CATCH scopes,
- failure notification,
- explicit failed termination.

## ALM Workflow

The project used a real unmanaged Solution as the scaffold rather than inventing a Power Platform package from scratch.

Conceptual development loop:

```text
Power Automate unmanaged Solution
        ↓
export .zip
        ↓
pac solution unpack
        ↓
source-controlled files
        ↓
workflow/source changes
        ↓
pac solution pack
        ↓
import into Power Platform
        ↓
bind environment-specific Connections/resources
        ↓
acceptance test
```

Typical CLI shape:

```powershell
pac solution unpack `
  --zipfile .\CyberGovernanceAutomationLab.zip `
  --folder .\power_automate\solutions\cyber_governance_automation

pac solution pack `
  --zipfile .\dist\CyberGovernanceAutomationLab.zip `
  --folder .\power_automate\solutions\cyber_governance_automation

pac solution import `
  --path .\dist\CyberGovernanceAutomationLab.zip
```

The repository source is a **portfolio-safe sanitized representation**, not a ready-to-deploy tenant package. Deployment requires restoring valid environment bindings or using a formal deployment-settings/environment-variable strategy.

## Acceptance Evidence

The Phase 7 Power Automate runtime was acceptance-tested with:

- normal happy path,
- four-file snapshot package creation,
- exact shared `snapshot_id`,
- manifest row-count consistency,
- Action reminder-state propagation,
- controlled failure injection,
- failure notification,
- explicit failed flow termination,
- no completion manifest for partial failed packages,
- empty `ActionRegister` behavior,
- header-only Action CSV with zero action rows,
- final cleanup and normal smoke run.

See:

```text
docs/phase7_power_automate_acceptance.md
```

## Security Note

Do not replace the repository placeholders with real private identifiers and then commit them. Private deployment exports belong outside the public repository.

import argparse
import re
import sys
from datetime import date
from pathlib import Path


if __package__:
    from .extract import (
        load_actions,
        load_control_catalog,
        load_submissions,
    )
    from .load import write_pipeline_outputs
    from .transform import (
        add_source_row_number,
        build_ai_review_queue,
        build_curated_control_status,
        normalize_actions,
        normalize_control_catalog,
        normalize_submissions,
    )
    from .validate import validate_submissions
else:
    from extract import (
        load_actions,
        load_control_catalog,
        load_submissions,
    )
    from load import write_pipeline_outputs
    from transform import (
        add_source_row_number,
        build_ai_review_queue,
        build_curated_control_status,
        normalize_actions,
        normalize_control_catalog,
        normalize_submissions,
    )
    from validate import validate_submissions


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_iso_date(value: str) -> date:
    """Parse an exact YYYY-MM-DD command-line date."""

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise argparse.ArgumentTypeError(
            "as-of date must use the exact YYYY-MM-DD format"
        )

    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "as-of date must be a valid calendar date in YYYY-MM-DD format"
        ) from error


def parse_arguments(arguments=None):
    """Parse the supported pipeline command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Run the Cyber Governance data pipeline."
    )
    parser.add_argument(
        "--as-of-date",
        type=parse_iso_date,
        help="Processing date in exact YYYY-MM-DD format (default: today).",
    )
    parser.add_argument(
        "--controls-path",
        type=Path,
        help="Path to an external Control Catalog JSON snapshot.",
    )
    parser.add_argument(
        "--submissions-path",
        type=Path,
        help="Path to an external Submission CSV snapshot.",
    )
    parser.add_argument(
        "--actions-path",
        type=Path,
        help="Path to an external Action CSV snapshot.",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        help="Directory for the three contractual pipeline outputs.",
    )

    parsed = parser.parse_args(arguments)

    try:
        validate_source_path_overrides(
            parsed.controls_path,
            parsed.submissions_path,
            parsed.actions_path,
        )
    except ValueError as error:
        parser.error(str(error))

    return parsed


def validate_source_path_overrides(
    controls_path: Path | None,
    submissions_path: Path | None,
    actions_path: Path | None,
) -> None:
    """Require external Control, Submission, and Action paths as one set."""

    provided_paths = (
        controls_path is not None,
        submissions_path is not None,
        actions_path is not None,
    )

    if any(provided_paths) and not all(provided_paths):
        raise ValueError(
            "all three source paths must be supplied together: "
            "--controls-path, --submissions-path, and --actions-path"
        )


def run_pipeline(
    as_of_date: date,
    project_root: Path = PROJECT_ROOT,
    controls_path: Path | None = None,
    submissions_path: Path | None = None,
    actions_path: Path | None = None,
    output_directory: Path | None = None,
) -> dict[str, int]:
    """Run the pipeline and return its contractual summary counts."""

    validate_source_path_overrides(
        controls_path,
        submissions_path,
        actions_path,
    )

    if controls_path is None:
        controls_path = project_root / "data/reference/control_catalog.json"
        submissions_path = project_root / "data/raw/evidence_submissions.csv"
        actions_path = project_root / "data/raw/actions.csv"

    if output_directory is None:
        output_directory = project_root / "data/curated"

    raw_controls = load_control_catalog(controls_path)
    raw_submissions = load_submissions(submissions_path)
    raw_actions = load_actions(actions_path)

    controls = normalize_control_catalog(raw_controls)
    submissions = add_source_row_number(
        normalize_submissions(raw_submissions)
    )
    actions = normalize_actions(raw_actions)

    dq_issues = validate_submissions(submissions, controls)
    curated = build_curated_control_status(
        submissions,
        controls,
        actions,
        dq_issues,
        as_of_date,
    )
    ai_review_queue = build_ai_review_queue(
        curated,
        as_of_date,
    )

    write_pipeline_outputs(
        curated,
        dq_issues,
        ai_review_queue,
        output_directory,
    )

    valid_submissions = int(
        (curated["data_quality_status"] == "Valid").sum()
    )
    invalid_submissions = int(
        (curated["data_quality_status"] == "Invalid").sum()
    )

    return {
        "controls_loaded": len(controls),
        "submissions_loaded": len(submissions),
        "actions_loaded": len(actions),
        "dq_issues": len(dq_issues),
        "valid_submissions": valid_submissions,
        "invalid_submissions": invalid_submissions,
        "ai_review_queue_items": len(ai_review_queue["items"]),
    }


def print_run_summary(summary: dict[str, int]) -> None:
    """Print the concise contractual run counts."""

    print(f"Controls loaded: {summary['controls_loaded']}")
    print(f"Submissions loaded: {summary['submissions_loaded']}")
    print(f"Actions loaded: {summary['actions_loaded']}")
    print(f"DQ issues: {summary['dq_issues']}")
    print(f"Valid submissions: {summary['valid_submissions']}")
    print(f"Invalid submissions: {summary['invalid_submissions']}")
    print(
        "AI review queue items: "
        f"{summary['ai_review_queue_items']}"
    )


def main(arguments=None, project_root: Path = PROJECT_ROOT) -> int:
    """Run the command-line pipeline and return its process exit status."""

    parsed = parse_arguments(arguments)
    as_of_date = parsed.as_of_date or date.today()

    try:
        summary = run_pipeline(
            as_of_date,
            project_root=project_root,
            controls_path=parsed.controls_path,
            submissions_path=parsed.submissions_path,
            actions_path=parsed.actions_path,
            output_directory=parsed.output_directory,
        )
    except (OSError, ValueError) as error:
        print(f"Pipeline failed: {error}", file=sys.stderr)
        return 1

    print_run_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

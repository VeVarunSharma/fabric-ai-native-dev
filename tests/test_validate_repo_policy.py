from __future__ import annotations

from pathlib import Path

from scripts.validate_repo_policy import (
    scan_sensitive_values,
    summarize_fabric_items,
    validate_pr_context,
)


def test_copy_job_change_requires_removed_tables_statement() -> None:
    errors = validate_pr_context(
        ["workspace/Load.CopyJob/copyjob-content.json"],
        "## Copy Job table changes\nAdded tables: Customers",
    )

    assert errors == ["Copy Job changes must explicitly state 'Removed tables:'."]


def test_lakehouse_change_accepts_explicit_no_security_change() -> None:
    errors = validate_pr_context(
        ["workspace/Analytics.Lakehouse/.platform"],
        "## OneLake security impact\n- [x] No OneLake security change",
    )

    assert errors == []


def test_lakehouse_change_rejects_unchecked_template_defaults() -> None:
    errors = validate_pr_context(
        ["workspace/Analytics.Lakehouse/.platform"],
        (
            "## OneLake security impact\n"
            "- [ ] No OneLake security change\n"
            "- [ ] Security runbook:"
        ),
    )

    assert errors == [
        "Lakehouse changes must state no OneLake security change or link a runbook."
    ]


def test_sensitive_value_scanner_is_conservative(tmp_path: Path) -> None:
    script = tmp_path / "scripts" / "deploy.py"
    script.parent.mkdir()
    script.write_text('client_secret = "not-a-placeholder-secret"\n', encoding="utf-8")

    findings = scan_sensitive_values(tmp_path, ["scripts/deploy.py"])

    assert findings == ["scripts/deploy.py: possible hard-coded credential value"]


def test_changed_fabric_items_are_summarized_once() -> None:
    items = summarize_fabric_items(
        [
            "workspace/Load.CopyJob/copyjob-content.json",
            "workspace/Load.CopyJob/.platform",
            "workspace/Prepare.Notebook/notebook-content.py",
        ]
    )

    assert items == ["Load.CopyJob", "Prepare.Notebook"]

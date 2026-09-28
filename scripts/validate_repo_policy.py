"""Enforce the small set of Fabric-specific repository policies."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

COPY_JOB_MARKER = ".CopyJob/"
LAKEHOUSE_MARKER = ".Lakehouse/"
FABRIC_ITEM_SUFFIXES = {
    "CopyJob",
    "DataPipeline",
    "Dataflow",
    "Eventhouse",
    "Eventstream",
    "KQLDatabase",
    "Lakehouse",
    "Notebook",
    "Report",
    "SemanticModel",
    "VariableLibrary",
    "Warehouse",
}
SENSITIVE_ASSIGNMENT = re.compile(
    r"""(?ix)
    (client[_-]?secret|password|accountkey)
    ["']?\s*[:=]\s*
    ["'](?!<|\$\{|@Microsoft\.KeyVault|REPLACE_ME)([^"']{8,})["']
    """
)


def validate_pr_context(changed_files: list[str], pr_body: str) -> list[str]:
    """Validate acknowledgements required for risky Fabric item changes."""
    errors: list[str] = []
    normalized = [path.replace("\\", "/") for path in changed_files]

    if any(COPY_JOB_MARKER in path for path in normalized):
        if "## Copy Job table changes" not in pr_body:
            errors.append("Copy Job changes require the 'Copy Job table changes' section.")
        if "Removed tables:" not in pr_body:
            errors.append("Copy Job changes must explicitly state 'Removed tables:'.")

    if any(LAKEHOUSE_MARKER in path for path in normalized):
        if "## OneLake security impact" not in pr_body:
            errors.append("Lakehouse changes require the 'OneLake security impact' section.")
        if not any(
            phrase in pr_body
            for phrase in (
                "- [x] No OneLake",
                "- [X] No OneLake",
                "- [x] Security runbook:",
                "- [X] Security runbook:",
            )
        ):
            errors.append(
                "Lakehouse changes must state no OneLake security change or link a runbook."
            )
    return errors


def scan_sensitive_values(repo_root: Path, paths: list[str]) -> list[str]:
    """Find likely committed credentials in human-authored automation files."""
    findings: list[str] = []
    allowed_roots = {"scripts", "config", ".github"}
    for relative in paths:
        path = repo_root / relative
        parts = Path(relative).parts
        if not parts or parts[0] not in allowed_roots or not path.is_file():
            continue
        if path.suffix.lower() not in {".py", ".json", ".yml", ".yaml", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if SENSITIVE_ASSIGNMENT.search(text):
            findings.append(f"{relative}: possible hard-coded credential value")
    return findings


def summarize_fabric_items(paths: list[str]) -> list[str]:
    """Return unique Fabric item folders represented by changed paths."""
    items: set[str] = set()
    for relative in paths:
        for part in Path(relative.replace("\\", "/")).parts:
            if "." not in part:
                continue
            suffix = part.rsplit(".", 1)[-1]
            if suffix in FABRIC_ITEM_SUFFIXES:
                items.add(part)
    return sorted(items)


def _changed_files(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def _all_files(repo_root: Path) -> list[str]:
    return [
        str(path.relative_to(repo_root))
        for path in repo_root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    ]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Fabric repository policies.")
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument(
        "--changed-files-file",
        type=Path,
        help="Text file containing one changed repository path per line.",
    )
    parser.add_argument("--pr-body-file", type=Path)
    parser.add_argument("--all", action="store_true", help="Scan all repository files.")
    return parser


def main() -> int:
    args = _parser().parse_args()
    repo_root = Path.cwd()
    if args.all:
        paths = _all_files(repo_root)
    elif args.changed_files_file:
        paths = [
            line
            for line in args.changed_files_file.read_text(encoding="utf-8").splitlines()
            if line
        ]
    else:
        paths = args.changed_file or _changed_files(args.base, args.head)
    pr_body = (
        args.pr_body_file.read_text(encoding="utf-8") if args.pr_body_file else ""
    )
    errors = scan_sensitive_values(repo_root, paths)
    if args.pr_body_file:
        errors.extend(validate_pr_context(paths, pr_body))

    items = summarize_fabric_items(paths)
    print("Changed Fabric items:")
    if items:
        for item in items:
            print(f"- {item}")
    else:
        print("- none detected")

    if errors:
        print("Repository policy validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Repository policy validation passed for {len(paths)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Explain Fabric Git status without changing the workspace or repository."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fabric_api import FabricApiClient


@dataclass(frozen=True)
class ChangeSummary:
    """One Fabric item change expressed in developer-friendly terms."""

    name: str
    item_type: str
    category: str
    workspace_change: str | None
    remote_change: str | None
    conflict_type: str


def classify_change(change: dict[str, Any]) -> ChangeSummary:
    """Classify one item from the Fabric Git status response."""
    metadata = change.get("itemMetadata", {})
    workspace_change = change.get("workspaceChange")
    remote_change = change.get("remoteChange")
    conflict_type = change.get("conflictType", "None")

    if conflict_type == "Conflict":
        category = "conflict"
    elif conflict_type == "SameChanges":
        category = "same-changes"
    elif workspace_change and remote_change:
        category = "both-sides"
    elif workspace_change:
        category = "workspace-only"
    elif remote_change:
        category = "remote-only"
    else:
        category = "unknown"

    return ChangeSummary(
        name=str(metadata.get("displayName", "<unnamed item>")),
        item_type=str(metadata.get("itemType", "<unknown type>")),
        category=category,
        workspace_change=str(workspace_change) if workspace_change else None,
        remote_change=str(remote_change) if remote_change else None,
        conflict_type=str(conflict_type),
    )


def analyze_status(status: dict[str, Any]) -> dict[str, Any]:
    """Return a stable, testable analysis of a Fabric Git status payload."""
    workspace_head = status.get("workspaceHead")
    remote_hash = status.get("remoteCommitHash")
    changes = [classify_change(change) for change in status.get("changes", [])]
    categories: dict[str, list[dict[str, Any]]] = {}
    for change in changes:
        categories.setdefault(change.category, []).append(asdict(change))

    if not changes and workspace_head == remote_hash:
        next_step = "No action required. The workspace and Git branch are synchronized."
    elif categories.get("conflict"):
        next_step = (
            "Stop and review each same-item conflict. Choose which version should win; "
            "this tool will not overwrite either side."
        )
    elif categories.get("workspace-only") and categories.get("remote-only"):
        next_step = (
            "Both sides have independent changes. Commit or selectively preserve the "
            "workspace changes before updating from Git."
        )
    elif categories.get("workspace-only"):
        next_step = "Review and commit the workspace-only changes to Git."
    elif categories.get("remote-only"):
        next_step = (
            "Update the workspace from Git using the current workspaceHead and "
            "remoteCommitHash shown below."
        )
    else:
        next_step = "Review the unclassified changes before running a Git operation."

    return {
        "workspaceHead": workspace_head,
        "remoteCommitHash": remote_hash,
        "categories": categories,
        "nextStep": next_step,
    }


def render_analysis(analysis: dict[str, Any]) -> str:
    """Render analysis for a data scientist rather than a Git specialist."""
    lines = [
        f"Workspace head: {analysis.get('workspaceHead')}",
        f"Remote commit: {analysis.get('remoteCommitHash')}",
        "",
    ]
    categories = analysis["categories"]
    if not categories:
        lines.append("Changes: none")
    else:
        lines.append("Changes:")
        for category, changes in categories.items():
            lines.append(f"- {category}:")
            for change in changes:
                detail = (
                    f"workspace={change['workspace_change'] or '-'}, "
                    f"remote={change['remote_change'] or '-'}"
                )
                lines.append(
                    f"  - {change['item_type']} / {change['name']} ({detail})"
                )
    lines.extend(["", f"Safest next step: {analysis['nextStep']}"])
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Diagnose Fabric/Git synchronization without changing either side."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--status-file", type=Path, help="Saved Fabric git/status JSON.")
    source.add_argument("--workspace-id", help="Workspace ID for a live read-only check.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable analysis.")
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.status_file:
        status = json.loads(args.status_file.read_text(encoding="utf-8"))
    else:
        client = FabricApiClient.from_service_principal(
            skill_name="git-integration-operations-cli"
        )
        status = client.get_json(
            f"workspaces/{args.workspace_id}/git/status",
            params={"includeFilesDetails": "true"},
        )

    analysis = analyze_status(status)
    print(json.dumps(analysis, indent=2) if args.json else render_analysis(analysis))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

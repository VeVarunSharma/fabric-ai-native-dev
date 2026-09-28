"""Select and verify the active Fabric Variable Library value set."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Protocol

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fabric_api import FabricApiClient, FabricApiError


class VariableLibraryClient(Protocol):
    """Narrow client contract used by the operation and its tests."""

    def patch_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]: ...

    def get_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...


def activate_value_set(
    client: VariableLibraryClient,
    *,
    workspace_id: str,
    library_id: str,
    value_set_name: str,
) -> str:
    """Select a value set, read it back, and return the verified name."""
    path = f"workspaces/{workspace_id}/variableLibraries/{library_id}"
    client.patch_json(
        path,
        {"properties": {"activeValueSetName": value_set_name}},
    )
    current = client.get_json(path)
    active_name = current.get("properties", {}).get("activeValueSetName")
    if active_name != value_set_name:
        raise FabricApiError(
            f"Variable Library verification failed: expected '{value_set_name}', "
            f"but Fabric returned '{active_name}'."
        )
    return str(active_name)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Select a Variable Library value set after deployment. "
            "This updates workspace state and does not create a Git diff."
        )
    )
    workspace = parser.add_mutually_exclusive_group(required=True)
    workspace.add_argument("--workspace-id")
    workspace.add_argument("--workspace-name")
    library = parser.add_mutually_exclusive_group(required=True)
    library.add_argument("--library-id")
    library.add_argument("--library-name")
    parser.add_argument("--value-set", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    client = FabricApiClient.from_service_principal(skill_name="variable-library-cli")

    workspace_id = args.workspace_id
    if not workspace_id:
        workspace_id = client.resolve_workspace_id(args.workspace_name)

    library_id = args.library_id
    if not library_id:
        library_id = client.resolve_item_id(
            workspace_id,
            "VariableLibrary",
            args.library_name,
        )

    active_name = activate_value_set(
        client,
        workspace_id=workspace_id,
        library_id=library_id,
        value_set_name=args.value_set,
    )
    print(
        f"Active value set is now '{active_name}'. "
        "This workspace-state change is intentionally not stored in Git."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

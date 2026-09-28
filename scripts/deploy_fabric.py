"""Deploy Fabric item definitions from the repository with fabric-cicd."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fabric_api import FabricApiError


def build_workspace_kwargs(
    *,
    repository_directory: Path,
    environment: str,
    credential: object,
    workspace_id: str | None,
    workspace_name: str | None,
    item_types: list[str] | None,
) -> dict[str, Any]:
    """Build the explicit FabricWorkspace arguments used by the deployer."""
    if bool(workspace_id) == bool(workspace_name):
        raise FabricApiError("Specify exactly one of workspace_id or workspace_name.")
    if not repository_directory.is_dir():
        raise FabricApiError(
            f"Fabric repository directory does not exist: {repository_directory}"
        )
    if not environment:
        raise FabricApiError(
            "Deployment environment is required and should match a Variable Library "
            "value-set name when VariableLibrary items are in scope."
        )

    kwargs: dict[str, Any] = {
        "repository_directory": str(repository_directory.resolve()),
        "environment": environment,
        "token_credential": credential,
    }
    if workspace_id:
        kwargs["workspace_id"] = workspace_id
    else:
        kwargs["workspace_name"] = workspace_name
    if item_types:
        kwargs["item_type_in_scope"] = item_types
    return kwargs


def deploy(
    *,
    repository_directory: Path,
    environment: str,
    credential: object,
    workspace_id: str | None = None,
    workspace_name: str | None = None,
    item_types: list[str] | None = None,
    unpublish_orphans: bool = False,
) -> None:
    """Publish repository items and optionally remove target-only orphan items."""
    from fabric_cicd import (  # type: ignore[import-not-found]
        FabricWorkspace,
        publish_all_items,
        unpublish_all_orphan_items,
    )

    workspace = FabricWorkspace(
        **build_workspace_kwargs(
            repository_directory=repository_directory,
            environment=environment,
            credential=credential,
            workspace_id=workspace_id,
            workspace_name=workspace_name,
            item_types=item_types,
        )
    )
    publish_all_items(workspace)
    if unpublish_orphans:
        unpublish_all_orphan_items(workspace)


def _credential_from_environment() -> object:
    tenant_id = os.environ.get("FABRIC_TENANT_ID")
    client_id = os.environ.get("FABRIC_CLIENT_ID")
    client_secret = os.environ.get("FABRIC_CLIENT_SECRET")
    missing = [
        name
        for name, value in (
            ("FABRIC_TENANT_ID", tenant_id),
            ("FABRIC_CLIENT_ID", client_id),
            ("FABRIC_CLIENT_SECRET", client_secret),
        )
        if not value
    ]
    if missing:
        raise FabricApiError(
            "Missing service principal configuration: " + ", ".join(missing)
        )
    assert tenant_id is not None
    assert client_id is not None
    assert client_secret is not None

    from azure.identity import ClientSecretCredential

    return ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deploy Fabric item definitions with fabric-cicd 1.3.0."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--workspace-id")
    target.add_argument("--workspace-name")
    parser.add_argument("--repository-directory", type=Path, required=True)
    parser.add_argument(
        "--environment",
        required=True,
        help="Deployment stage name; use the exact Variable Library value-set name.",
    )
    parser.add_argument(
        "--item-type",
        action="append",
        dest="item_types",
        help="Optional Fabric item type to include. Repeat for multiple types.",
    )
    parser.add_argument(
        "--unpublish-orphans",
        action="store_true",
        help=(
            "Delete target items missing from the repository. "
            "Off by default because this is destructive."
        ),
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    deploy(
        repository_directory=args.repository_directory,
        environment=args.environment,
        credential=_credential_from_environment(),
        workspace_id=args.workspace_id,
        workspace_name=args.workspace_name,
        item_types=args.item_types,
        unpublish_orphans=args.unpublish_orphans,
    )
    target = args.workspace_id or args.workspace_name
    print(
        f"Published Fabric definitions from '{args.repository_directory}' "
        f"to '{target}' for environment '{args.environment}'."
    )
    if not args.unpublish_orphans:
        print("Target-only orphan items were not deleted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

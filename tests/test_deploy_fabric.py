from __future__ import annotations

from pathlib import Path

import pytest

from scripts.deploy_fabric import build_workspace_kwargs
from scripts.fabric_api import FabricApiError


def test_workspace_kwargs_use_id_and_explicit_environment(tmp_path: Path) -> None:
    credential = object()

    kwargs = build_workspace_kwargs(
        repository_directory=tmp_path,
        environment="prod",
        credential=credential,
        workspace_id="workspace-id",
        workspace_name=None,
        item_types=["Notebook", "VariableLibrary"],
    )

    assert kwargs == {
        "repository_directory": str(tmp_path.resolve()),
        "environment": "prod",
        "token_credential": credential,
        "workspace_id": "workspace-id",
        "item_type_in_scope": ["Notebook", "VariableLibrary"],
    }


def test_workspace_target_must_be_unambiguous(tmp_path: Path) -> None:
    with pytest.raises(FabricApiError, match="exactly one"):
        build_workspace_kwargs(
            repository_directory=tmp_path,
            environment="prod",
            credential=object(),
            workspace_id="workspace-id",
            workspace_name="workspace-name",
            item_types=None,
        )


def test_repository_directory_must_exist(tmp_path: Path) -> None:
    with pytest.raises(FabricApiError, match="does not exist"):
        build_workspace_kwargs(
            repository_directory=tmp_path / "missing",
            environment="prod",
            credential=object(),
            workspace_id="workspace-id",
            workspace_name=None,
            item_types=None,
        )

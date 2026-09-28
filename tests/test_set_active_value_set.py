from __future__ import annotations

from typing import Any

import pytest

from scripts.fabric_api import FabricApiError
from scripts.set_active_value_set import activate_value_set


class FakeClient:
    def __init__(self, readback_name: str) -> None:
        self.readback_name = readback_name
        self.patch_calls: list[tuple[str, dict[str, Any]]] = []

    def patch_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        self.patch_calls.append((path, body))
        return {}

    def get_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {"properties": {"activeValueSetName": self.readback_name}}


def test_active_value_set_is_verified() -> None:
    client = FakeClient("prod")

    result = activate_value_set(
        client,
        workspace_id="workspace-id",
        library_id="library-id",
        value_set_name="prod",
    )

    assert result == "prod"
    assert client.patch_calls == [
        (
            "workspaces/workspace-id/variableLibraries/library-id",
            {"properties": {"activeValueSetName": "prod"}},
        )
    ]


def test_active_value_set_mismatch_fails() -> None:
    client = FakeClient("nonprod")

    with pytest.raises(FabricApiError, match="verification failed"):
        activate_value_set(
            client,
            workspace_id="workspace-id",
            library_id="library-id",
            value_set_name="prod",
        )

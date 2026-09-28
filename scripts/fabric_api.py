"""Small Microsoft Fabric REST client used by the demo scripts."""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Iterator
from typing import Any

import requests

FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"
FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"


class FabricApiError(RuntimeError):
    """Raised when a Fabric REST operation fails."""


TokenProvider = Callable[[], str]


class FabricApiClient:
    """Call Fabric APIs with explicit error handling and bounded LRO polling."""

    def __init__(
        self,
        token_provider: TokenProvider,
        *,
        skill_name: str,
        session: requests.Session | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        self._token_provider = token_provider
        self._skill_name = skill_name
        self._session = session or requests.Session()
        self._timeout_seconds = timeout_seconds

    @classmethod
    def from_service_principal(
        cls,
        *,
        skill_name: str,
        tenant_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> FabricApiClient:
        """Create a client from explicit values or standard environment variables."""
        tenant_id = tenant_id or os.environ.get("FABRIC_TENANT_ID")
        client_id = client_id or os.environ.get("FABRIC_CLIENT_ID")
        client_secret = client_secret or os.environ.get("FABRIC_CLIENT_SECRET")
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

        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        return cls(
            lambda: credential.get_token(FABRIC_SCOPE).token,
            skill_name=skill_name,
        )

    def request(
        self,
        method: str,
        path_or_url: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> requests.Response:
        """Send one request and raise a readable error for non-success responses."""
        url = (
            path_or_url
            if path_or_url.startswith("https://")
            else f"{FABRIC_API_BASE}/{path_or_url.lstrip('/')}"
        )
        response = self._session.request(
            method,
            url,
            headers={
                "Authorization": f"Bearer {self._token_provider()}",
                "Content-Type": "application/json",
                "x-ms-fabric-skill": self._skill_name,
            },
            json=json_body,
            params=params,
            timeout=self._timeout_seconds,
        )
        if response.status_code >= 400:
            detail = response.text.strip() or "<empty response>"
            raise FabricApiError(
                f"Fabric API {method.upper()} {url} failed "
                f"with HTTP {response.status_code}: {detail}"
            )
        return response

    def get_json(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """GET JSON, including the Fabric long-running-operation pattern."""
        response = self.request("GET", path, params=params)
        if response.status_code == 202:
            self._wait_for_operation(response)
            response = self.request("GET", path, params=params)
        return _response_json(response)

    def patch_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        """PATCH JSON and wait if the operation is asynchronous."""
        response = self.request("PATCH", path, json_body=body)
        if response.status_code == 202:
            return self._wait_for_operation(response)
        return _response_json(response, allow_empty=True)

    def iter_values(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield paginated objects from a Fabric list endpoint."""
        next_url: str | None = path
        next_params = params
        while next_url:
            payload = self.get_json(next_url, params=next_params)
            yield from payload.get("value", [])
            next_url = payload.get("continuationUri")
            next_params = None

    def resolve_workspace_id(self, display_name: str) -> str:
        """Resolve one workspace by its exact display name."""
        matches = [
            workspace
            for workspace in self.iter_values("workspaces")
            if workspace.get("displayName") == display_name
        ]
        return _require_single_id(matches, "workspace", display_name)

    def resolve_item_id(self, workspace_id: str, item_type: str, display_name: str) -> str:
        """Resolve one item by exact type and display name."""
        matches = [
            item
            for item in self.iter_values(
                f"workspaces/{workspace_id}/items",
                params={"type": item_type},
            )
            if item.get("displayName") == display_name and item.get("type") == item_type
        ]
        return _require_single_id(matches, item_type, display_name)

    def _wait_for_operation(
        self,
        response: requests.Response,
        *,
        attempts: int = 120,
    ) -> dict[str, Any]:
        operation_url = response.headers.get("Location")
        operation_id = response.headers.get("x-ms-operation-id")
        if not operation_url and operation_id:
            operation_url = f"{FABRIC_API_BASE}/operations/{operation_id}"
        if not operation_url:
            raise FabricApiError("Fabric returned HTTP 202 without an operation URL or ID.")

        delay = max(int(response.headers.get("Retry-After", "5")), 1)
        for _ in range(attempts):
            operation = self.request("GET", operation_url)
            payload = _response_json(operation, allow_empty=True)
            status = payload.get("status")
            if status == "Succeeded":
                return payload
            if status in {"Failed", "Cancelled", "Undefined"}:
                raise FabricApiError(f"Fabric operation ended with status {status}: {payload}")
            time.sleep(delay)
        raise FabricApiError("Fabric operation did not complete within the polling limit.")


def _response_json(
    response: requests.Response,
    *,
    allow_empty: bool = False,
) -> dict[str, Any]:
    if allow_empty and not response.content:
        return {}
    try:
        payload = response.json()
    except requests.JSONDecodeError as exc:
        raise FabricApiError("Fabric returned a non-JSON response.") from exc
    if not isinstance(payload, dict):
        raise FabricApiError("Fabric returned an unexpected JSON shape.")
    return payload


def _require_single_id(items: list[dict[str, Any]], item_type: str, name: str) -> str:
    if not items:
        raise FabricApiError(f"No {item_type} named '{name}' was found.")
    if len(items) > 1:
        raise FabricApiError(f"Multiple {item_type} items named '{name}' were found.")
    item_id = items[0].get("id")
    if not isinstance(item_id, str) or not item_id:
        raise FabricApiError(f"The resolved {item_type} '{name}' has no ID.")
    return item_id

"""HTTP client for Cursor Cloud Agents + Admin APIs."""

from __future__ import annotations

import time
from typing import Any

import httpx

from .config import Settings, load_settings


class CursorApiError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, hint: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.hint = hint


class CursorClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()

    def _auth(self, key: str) -> httpx.BasicAuth:
        return httpx.BasicAuth(key, "")

    async def _request(
        self,
        method: str,
        path: str,
        *,
        api_key: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.settings.api_base}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method,
                url,
                auth=self._auth(api_key),
                json=json_body,
                params=params,
            )
        if response.status_code == 401:
            raise CursorApiError("Invalid Cursor API key", status_code=401)
        if response.status_code == 403:
            raise CursorApiError(
                "Cursor API forbidden — Admin API may require Team/Enterprise key",
                status_code=403,
                hint="Create Admin API key at cursor.com/dashboard → Settings → Advanced → Admin API Keys",
            )
        if response.status_code == 429:
            raise CursorApiError("Cursor API rate limited — back off and retry", status_code=429)
        if not response.is_success:
            detail = response.text[:500]
            raise CursorApiError(f"Cursor API error {response.status_code}: {detail}", status_code=response.status_code)
        if not response.content:
            return {}
        data = response.json()
        return data if isinstance(data, dict) else {"data": data}

    def require_user_key(self) -> str:
        if not self.settings.user_api_key:
            raise CursorApiError(
                "CURSOR_API_KEY not set",
                hint="Create user API key at cursor.com/dashboard → Integrations",
            )
        return self.settings.user_api_key

    def require_admin_key(self) -> str:
        key = self.settings.admin_api_key or self.settings.user_api_key
        if not key:
            raise CursorApiError(
                "CURSOR_ADMIN_API_KEY not set",
                hint="Admin spend endpoints need crsr_ team admin key",
            )
        return key

    async def me(self) -> dict[str, Any]:
        return await self._request("GET", "/v1/me", api_key=self.require_user_key())

    async def list_agents(self, *, limit: int = 50) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/v1/agents",
            api_key=self.require_user_key(),
            params={"limit": limit},
        )

    async def get_agent(self, agent_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/agents/{agent_id}", api_key=self.require_user_key())

    async def list_runs(self, agent_id: str, *, limit: int = 20) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"/v1/agents/{agent_id}/runs",
            api_key=self.require_user_key(),
            params={"limit": limit},
        )

    async def cancel_run(self, agent_id: str, run_id: str) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/v1/agents/{agent_id}/runs/{run_id}/cancel",
            api_key=self.require_user_key(),
        )

    async def team_spend(
        self,
        *,
        search_term: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"page": page, "pageSize": page_size}
        if search_term:
            body["searchTerm"] = search_term
        return await self._request(
            "POST",
            "/teams/spend",
            api_key=self.require_admin_key(),
            json_body=body,
        )

    async def usage_events(
        self,
        *,
        start_ms: int,
        end_ms: int,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/teams/filtered-usage-events",
            api_key=self.require_admin_key(),
            json_body={
                "startDate": start_ms,
                "endDate": end_ms,
                "page": page,
                "pageSize": page_size,
            },
        )

    @staticmethod
    def hour_window_ms(hours: float = 1.0) -> tuple[int, int]:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - int(hours * 3600 * 1000)
        return start_ms, end_ms

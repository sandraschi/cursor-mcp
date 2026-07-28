"""Environment configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    api_base: str
    user_api_key: str | None
    admin_api_key: str | None
    host: str
    port: int
    cache_path: Path
    hourly_spend_warn_cents: float
    on_demand_warn_cents: float
    running_agents_warn: int
    user_email_filter: str | None


def load_settings() -> Settings:
    cache_dir = Path(os.environ.get("CURSOR_MCP_CACHE_DIR", Path.home() / ".cursor-mcp"))
    return Settings(
        api_base=os.environ.get("CURSOR_API_BASE", "https://api.cursor.com").rstrip("/"),
        user_api_key=_pick_key("CURSOR_API_KEY", "CURSOR_USER_API_KEY"),
        admin_api_key=_pick_key("CURSOR_ADMIN_API_KEY", "CURSOR_TEAM_API_KEY"),
        host=os.environ.get("CURSOR_MCP_HOST", "127.0.0.1"),
        port=int(os.environ.get("CURSOR_MCP_PORT", "11000")),
        cache_path=cache_dir / "usage_cache.json",
        hourly_spend_warn_cents=float(os.environ.get("CURSOR_HOURLY_SPEND_WARN_CENTS", "300")),
        on_demand_warn_cents=float(os.environ.get("CURSOR_ON_DEMAND_WARN_CENTS", "2000")),
        running_agents_warn=int(os.environ.get("CURSOR_RUNNING_AGENTS_WARN", "3")),
        user_email_filter=os.environ.get("CURSOR_USAGE_EMAIL") or None,
    )


def _pick_key(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return None

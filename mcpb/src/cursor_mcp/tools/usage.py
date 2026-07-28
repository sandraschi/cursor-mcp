"""cursor_usage portmanteau — spend guardrails."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from ..alerts import evaluate_alerts, pick_member_spend, sum_event_cents
from ..cache import load_cache, save_cache, stamp_snapshot
from ..client import CursorApiError, CursorClient
from ..config import load_settings

Operation = Literal["summary", "spend", "events", "alert_check", "limits", "me"]


async def cursor_usage(
    operation: Annotated[Operation, Field(description="Usage operation to run.")],
    hours: Annotated[float, Field(description="Lookback window for events/alert_check.", ge=0.25, le=24)] = 1.0,
    email: Annotated[str | None, Field(description="Filter spend row by email (Admin API).")] = None,
) -> dict[str, Any]:
    """Cursor billing and spend guardrails (read-only).

    Requires CURSOR_API_KEY. Admin endpoints also accept CURSOR_ADMIN_API_KEY (crsr_ team key).
    Use alert_check on a schedule (e.g. Fritz every 2h) instead of manual dashboard checks.
    """
    settings = load_settings()
    client = CursorClient(settings)
    email_filter = email or settings.user_email_filter

    if operation == "me":
        data = await client.me()
        return {"success": True, "operation": operation, "data": data, "message": "API key identity"}

    if operation == "limits":
        return {
            "success": True,
            "operation": operation,
            "thresholds": {
                "hourly_spend_warn_usd": settings.hourly_spend_warn_cents / 100,
                "on_demand_warn_usd": settings.on_demand_warn_cents / 100,
                "running_agents_warn": settings.running_agents_warn,
            },
            "keys": {
                "user_api_key": bool(settings.user_api_key),
                "admin_api_key": bool(settings.admin_api_key),
            },
            "dashboard": "https://cursor.com/dashboard",
            "message": "Configured alert thresholds",
        }

    spend_row: dict[str, Any] | None = None
    spend_error: str | None = None
    hourly_cents = 0.0
    events_error: str | None = None

    try:
        spend_payload = await client.team_spend(search_term=email_filter)
        spend_row = pick_member_spend(spend_payload, email_filter)
    except CursorApiError as exc:
        spend_error = str(exc)

    try:
        start_ms, end_ms = CursorClient.hour_window_ms(hours)
        events_payload = await client.usage_events(start_ms=start_ms, end_ms=end_ms)
        hourly_cents = sum_event_cents(events_payload)
    except CursorApiError as exc:
        events_error = str(exc)

    running_agents = 0
    agents_error: str | None = None
    agents_payload: dict[str, Any] = {}
    try:
        agents_payload = await client.list_agents(limit=50)
        from ..alerts import count_running_agents

        running_agents = count_running_agents(agents_payload)
    except CursorApiError as exc:
        agents_error = str(exc)

    if operation == "spend":
        return {
            "success": spend_row is not None,
            "operation": operation,
            "spend": spend_row,
            "error": spend_error,
            "message": "Team spend row" if spend_row else (spend_error or "No spend data"),
        }

    if operation == "events":
        return {
            "success": events_error is None,
            "operation": operation,
            "hourly_cents": hourly_cents,
            "hours": hours,
            "error": events_error,
            "message": f"Events last {hours}h ≈ ${hourly_cents / 100:.2f}",
        }

    previous = load_cache(settings.cache_path)
    alert = evaluate_alerts(
        settings=settings,
        spend_row=spend_row,
        hourly_cents=hourly_cents,
        running_agents=running_agents,
        previous=previous,
    )

    snapshot = stamp_snapshot(
        hourly_cents=hourly_cents,
        on_demand_cents=(spend_row or {}).get("spendCents"),
        overall_cents=(spend_row or {}).get("overallSpendCents"),
        running_agents=running_agents,
        alert_level=alert["level"],
    )
    save_cache(settings.cache_path, snapshot)

    if operation == "alert_check":
        return {
            "success": True,
            "operation": operation,
            "alert": alert,
            "partial_errors": {
                "spend": spend_error,
                "events": events_error,
                "agents": agents_error,
            },
            "message": f"Alert level: {alert['level']} — {'; '.join(alert['reasons'])}",
        }

    # summary
    return {
        "success": True,
        "operation": "summary",
        "identity": await client.me() if settings.user_api_key else None,
        "spend": spend_row,
        "hourly_cents": hourly_cents,
        "running_cloud_agents": running_agents,
        "alert": alert,
        "partial_errors": {
            "spend": spend_error,
            "events": events_error,
            "agents": agents_error,
        },
        "cache_path": str(settings.cache_path),
        "message": f"Summary — alert {alert['level']}, {running_agents} active cloud agents",
    }

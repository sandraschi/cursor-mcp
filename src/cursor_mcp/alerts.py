"""Spend and runaway-agent alert evaluation."""

from __future__ import annotations

from typing import Any

from .config import Settings


def _cents_to_usd(cents: float | int | None) -> float | None:
    if cents is None:
        return None
    return round(float(cents) / 100.0, 4)


def pick_member_spend(spend_payload: dict[str, Any], email: str | None) -> dict[str, Any] | None:
    members = spend_payload.get("teamMemberSpend") or []
    if not members:
        return None
    if email:
        lowered = email.lower()
        for row in members:
            if str(row.get("email", "")).lower() == lowered:
                return row
    return members[0]


def sum_event_cents(events_payload: dict[str, Any]) -> float:
    events = events_payload.get("usageEvents") or events_payload.get("events") or []
    total = 0.0
    for event in events:
        charged = event.get("chargedCents")
        if charged is not None:
            total += float(charged)
    return total


def count_running_agents(agents_payload: dict[str, Any]) -> int:
    agents = agents_payload.get("agents") or agents_payload.get("data") or []
    running = 0
    for agent in agents:
        status = str(agent.get("status") or agent.get("state") or "").lower()
        if status in {"running", "active", "in_progress", "working"}:
            running += 1
    return running


def evaluate_alerts(
    *,
    settings: Settings,
    spend_row: dict[str, Any] | None,
    hourly_cents: float,
    running_agents: int,
    previous: dict[str, Any] | None,
) -> dict[str, Any]:
    reasons: list[str] = []
    level = "ok"

    on_demand_cents = float((spend_row or {}).get("spendCents") or 0)
    overall_cents = float((spend_row or {}).get("overallSpendCents") or 0)
    monthly_limit = (spend_row or {}).get("monthlyLimitDollars")

    if hourly_cents >= settings.hourly_spend_warn_cents:
        reasons.append(
            f"Hourly spend ${_cents_to_usd(hourly_cents):.2f} >= warn ${_cents_to_usd(settings.hourly_spend_warn_cents):.2f}"
        )
        level = "warn"

    if on_demand_cents >= settings.on_demand_warn_cents:
        reasons.append(
            f"On-demand ${_cents_to_usd(on_demand_cents):.2f} >= warn ${_cents_to_usd(settings.on_demand_warn_cents):.2f}"
        )
        level = "warn"

    if running_agents >= settings.running_agents_warn:
        reasons.append(f"{running_agents} cloud agents look active (warn >= {settings.running_agents_warn})")
        level = _raise_level(level, "critical" if running_agents >= settings.running_agents_warn + 2 else "warn")

    if previous:
        prev_hourly = float(previous.get("hourly_cents") or 0)
        if hourly_cents > prev_hourly * 2 and hourly_cents >= settings.hourly_spend_warn_cents:
            reasons.append("Hourly spend doubled since last check")
            level = "critical"

    if monthly_limit is not None and monthly_limit > 0:
        limit_cents = float(monthly_limit) * 100
        if overall_cents >= limit_cents * 0.9:
            reasons.append(f"Overall spend at {overall_cents / limit_cents * 100:.0f}% of monthly limit")
            level = "critical"

    if not reasons:
        reasons.append("Within configured guardrails")

    return {
        "level": level,
        "reasons": reasons,
        "metrics": {
            "hourly_spend_usd": _cents_to_usd(hourly_cents),
            "on_demand_spend_usd": _cents_to_usd(on_demand_cents),
            "overall_spend_usd": _cents_to_usd(overall_cents),
            "running_cloud_agents": running_agents,
            "monthly_limit_dollars": monthly_limit,
        },
    }


def _level_rank(level: str) -> int:
    return {"ok": 0, "warn": 1, "critical": 2}.get(level, 0)


def _raise_level(current: str, proposed: str) -> str:
    return proposed if _level_rank(proposed) > _level_rank(current) else current

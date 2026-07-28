from pathlib import Path

from cursor_mcp.alerts import evaluate_alerts, sum_event_cents
from cursor_mcp.config import Settings


def _settings() -> Settings:
    return Settings(
        api_base="https://api.cursor.com",
        user_api_key="x",
        admin_api_key=None,
        host="127.0.0.1",
        port=11000,
        cache_path=Path("/tmp/usage_cache.json"),
        hourly_spend_warn_cents=300,
        on_demand_warn_cents=2000,
        running_agents_warn=3,
        user_email_filter=None,
    )


def test_sum_event_cents():
    payload = {"usageEvents": [{"chargedCents": 50}, {"chargedCents": 25.5}]}
    assert sum_event_cents(payload) == 75.5


def test_alert_ok():
    result = evaluate_alerts(
        settings=_settings(),
        spend_row={"spendCents": 100, "overallSpendCents": 500},
        hourly_cents=50,
        running_agents=0,
        previous=None,
    )
    assert result["level"] == "ok"


def test_alert_critical_many_agents():
    result = evaluate_alerts(
        settings=_settings(),
        spend_row=None,
        hourly_cents=0,
        running_agents=5,
        previous=None,
    )
    assert result["level"] == "critical"

# Fritz — Cursor spend watch + inbox relay

Automate the "am I about to token-bomb?" check and inter-agent messaging via **fleet-agent-mcp** + **cursor-mcp**.

## Prerequisites

1. `cursor-mcp` running HTTP: `.\start.ps1 -Serve` (port **11000**)
2. `CURSOR_API_KEY` in cursor-mcp env (and `CURSOR_ADMIN_API_KEY` for full spend API)
3. `fleet-agent-mcp` running (port **10996**)
4. `cursor` registered in `fleet_bridge` FLEET_SERVERS

---

## Scheduled spend watch

| Field | Value |
|-------|-------|
| Flow key | `cursor_spend_watch` |
| Task id | `coworker-cursor-spend-watch` |
| Recurrence | `2h` (every 2 hours) |
| MCP tool | `coworker_cursor_spend_watch` |
| Underlying call | `cursor_usage(operation=alert_check)` |

### Bootstrap

```text
coworker_bootstrap()
```

Seeds `coworker-cursor-spend-watch` when `coworker_cursor_spend_watch_enabled` is true (default).

### Manual run

```text
coworker_cursor_spend_watch(deliver=true)
```

On `warn` / `critical`, Fritz emails via `notify_email` when SMTP is configured.

### Threshold tuning

Set on **cursor-mcp** process env:

| Variable | Default | Meaning |
|----------|---------|---------|
| `CURSOR_HOURLY_SPEND_WARN_CENTS` | 300 | ~$3 in last hour |
| `CURSOR_ON_DEMAND_WARN_CENTS` | 2000 | ~$20 on-demand cycle |
| `CURSOR_RUNNING_AGENTS_WARN` | 3 | Parallel cloud agents |

### Why 2 hours?

Matches Cursor Admin API hourly aggregation and avoids rate limits (20 req/min). Still catches runaway cloud agent parallelism via `/v1/agents`.

---

## Inbox relay (v0.2.0+)

Fritz can post structured messages to the Cursor agent inbox — useful for alerting the agent about fleet state changes, cold-install results, or scheduled heads-ups.

### Post a message from Fritz

```text
cursor_inbox(
    operation="post",
    sender="fritz",
    subject="Cold-install probe complete — 3 broken",
    body="fleet_cold_install_probe finished. Outcomes: install_ok=108, install_failed=2, doc_gap=1. Run BrokenOnly to retry.",
    priority="high",
    tags=["meta_mcp", "cold-install", "fritz-alert"]
)
```

### Cursor agent picks it up

The Cursor agent calls `cursor_inbox(operation="list")` at task start and sees the message waiting.

### Inbox dir

`CURSOR_INBOX_DIR` env (default `~/.cursor-mcp/inbox/`). Fritz and cursor-mcp must share the same path if running on different processes — both default to the same location on Goliath.

---

## Jun 2026 SDK alignment

- `cursor_docs(topic=changelog-jun-2026)` — fleet adoption digest
- `cursor_sdk(operation=autoreview_template)` — permissions.json for headless SDK scripts
- Pair IDE **context usage canvas** with `alert_check` for token diagnosis

MCD: `mcp-central-docs/ecosystem/cursor/CHANGELOG_DIGEST_JUN_2026.md`

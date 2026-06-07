# cursor-mcp — PRD

**Status:** Active  
**Version:** 0.2.0  
**Owner:** Sandra (sandraschi)  
**Port:** 11000 (HTTP `/mcp`), stdio  
**Started:** 2026-06-01

---

## Problem

Running 100+ MCP fleet repos with active Cursor agents creates two chronic problems:

1. **Spend blindness** — no way to know hourly API costs without manually checking the Cursor dashboard. Cloud agents in particular can run up unexpected bills silently.
2. **Agent isolation** — no structured way to pass information between Claude Desktop, meta_mcp, fleet scripts, and a running Cursor agent. The only option was dropping markdown files and hoping the agent picked them up.

---

## Solution

A focused FastMCP 3.2 server with two responsibilities:

**1. Spend guardrails** (`cursor_usage`, `cursor_cloud`)  
Poll Cursor's platform API on a schedule (Fritz, every 2h). Alert on hourly spend, on-demand totals, and runaway parallel cloud agents before they become a bill.

**2. Inter-agent inbox** (`cursor_inbox`)  
Filesystem drop dir for structured messages to Cursor agents. Any process posts; the Cursor agent polls at task start. No daemon, no network, pure JSON files.

---

## Out of scope

- IDE automation / Glass / DOM interaction → cursor-app-control
- Agent spawning or SDK orchestration → use Cursor SDK directly
- Replacing the Cursor dashboard for billing management

---

## Tools

### `cursor_usage`

| Operation | Purpose |
|-----------|---------|
| `alert_check` | Main guardrail — hourly spend, on-demand total, running agents, cache delta |
| `summary` | One-shot dashboard replacement |
| `spend` | Admin API `/teams/spend` row |
| `events` | Last N hours usage events |
| `limits` | Show configured thresholds |
| `me` | API key identity |

Requires `CURSOR_API_KEY`. Admin operations also accept `CURSOR_ADMIN_API_KEY`.

### `cursor_cloud`

| Operation | Purpose |
|-----------|---------|
| `list` | All cloud agents — spot runaway parallelism |
| `status` | Single agent detail |
| `runs` | Runs for agent |
| `cancel` | Cancel a run (gated) |

### `cursor_inbox`

Inter-agent message drop. Any sender writes; Cursor agent reads and acknowledges.

| Operation | Purpose |
|-----------|---------|
| `post` | Drop a structured message (subject, body, priority, tags, payload) |
| `list` | Poll for unread messages — call at agent task start |
| `read` | Read full message by id |
| `ack` | Acknowledge — moves to `inbox/acked/` |
| `ack_all` | Acknowledge all unread |
| `purge` | Delete acked messages older than N days |

**Drop dir:** `CURSOR_INBOX_DIR` env (default `~/.cursor-mcp/inbox/`)

**Who can write:**
- Claude Desktop via `cursor_inbox post` (cursor-mcp in Claude MCP config)
- meta_mcp or any fleet MCP server — direct JSON file drop
- PowerShell / Python scripts — same
- Sandra directly via any MCP client

**Cursor agent convention:** call `cursor_inbox list` at the start of any agent session.

### `cursor_docs`

Fleet-curated doc snippets. Topics: `cloud-agents`, `profiles`, `mcp-config`, `spend-guardrails`, `cursor-mcp`, `cursor-inbox`, `sdk-jun-2026`, `design-mode`, `auto-review`, `context-canvas`, `changelog-jun-2026`.

### `cursor_sdk`

Read-only SDK guidance (Jun 2026): `capabilities`, `upgrade_notes`, `autoreview_template`, `custom_tools_guide`, `store_options`.

### `cursor_help`

Tool index and setup. Always current.

---

## Configuration

| Env var | Default | Purpose |
|---------|---------|---------|
| `CURSOR_API_KEY` | — | User key, required |
| `CURSOR_ADMIN_API_KEY` | — | Team admin key, optional |
| `CURSOR_MCP_HOST` | `127.0.0.1` | HTTP bind host |
| `CURSOR_MCP_PORT` | `11000` | HTTP port |
| `CURSOR_INBOX_DIR` | `~/.cursor-mcp/inbox/` | Inbox drop dir |
| `CURSOR_HOURLY_SPEND_WARN_CENTS` | `300` | ~$3/h warn threshold |
| `CURSOR_ON_DEMAND_WARN_CENTS` | `2000` | ~$20 on-demand threshold |
| `CURSOR_RUNNING_AGENTS_WARN` | `3` | Parallel cloud agents warn |
| `CURSOR_USAGE_EMAIL` | — | Filter spend by email |
| `CURSOR_MCP_CACHE_DIR` | `~/.cursor-mcp/` | Cache + inbox root |

---

## Architecture

```
Claude Desktop  ──┐
meta_mcp        ──┼──► cursor_inbox post  ──► ~/.cursor-mcp/inbox/*.json
PS1 scripts     ──┘                                    │
                                                       ▼
Cursor agent ──────────────── cursor_inbox list/read/ack
                                     (polls at task start)

Fritz (every 2h) ──► cursor_usage alert_check ──► notify on warn/critical
```

Server runs in two modes:
- **stdio** — Cursor `mcp.json`, Claude Desktop `claude_desktop_config.json`
- **HTTP** — port 11000, Fritz `fleet_bridge`

---

## Fritz integration

Scheduled task `coworker_cursor_spend_watch` runs every 2 hours, calls `cursor_usage(operation=alert_check)`, emails on `warn` or `critical`. See `docs/FRITZ_INTEGRATION.md`.

---

## Roadmap

- `cursor_inbox` webhook mode — POST to a URL when a message arrives (for Fritz integration)
- `cursor_inbox` expiry — `ttl_hours` on post, auto-purge on read
- Inbox stats in `cursor_help` — unread count at startup

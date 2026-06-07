# cursor-mcp

**FastMCP 3.2** server for Cursor **platform APIs** — spend guardrails, cloud agent monitoring, and inter-agent inbox.

Complements **cursor-app-control** (IDE/Glass). Does not replace it.

| Port | Role |
|------|------|
| **11000** | HTTP `/mcp` (Fritz `fleet_bridge`) |
| stdio | Cursor `mcp.json` / Claude Desktop |

**MCD:** [CHANGELOG_DIGEST_JUN_2026.md](../mcp-central-docs/ecosystem/cursor/CHANGELOG_DIGEST_JUN_2026.md) · [CURSOR_MCP_PROPOSAL.md](../mcp-central-docs/ecosystem/cursor/CURSOR_MCP_PROPOSAL.md)

---

## Quick start

```powershell
cd D:\Dev\repos\cursor-mcp
Copy-Item .env.example .env
# Edit .env — set CURSOR_API_KEY (and CURSOR_ADMIN_API_KEY for full spend API)

uv sync
.\start.ps1 -Serve
```

### Cursor `mcp.json`

```json
{
  "mcpServers": {
    "cursor-mcp": {
      "command": "D:\\Dev\\repos\\cursor-mcp\\.venv\\Scripts\\python.exe",
      "args": ["-m", "cursor_mcp", "--stdio"],
      "env": {
        "CURSOR_API_KEY": "cursor_...",
        "CURSOR_ADMIN_API_KEY": "crsr_..."
      }
    }
  }
}
```

---

## Tools

### `cursor_usage`

| Operation | Purpose |
|-----------|---------|
| `alert_check` | **Main guardrail** — hourly spend, on-demand, running cloud agents, cache delta |
| `summary` | One-shot dashboard replacement |
| `spend` | Admin API `/teams/spend` row |
| `events` | Last N hours usage events (sum `chargedCents`) |
| `limits` | Show configured thresholds |
| `me` | API key identity |

### `cursor_cloud`

| Operation | Purpose |
|-----------|---------|
| `list` | All cloud agents — spot runaway parallelism |
| `status` | Single agent |
| `runs` | Runs for agent |
| `cancel` | Cancel a run (use sparingly) |

### `cursor_inbox`

Structured message drop for Cursor agents. Any process posts; agent polls at task start.

| Operation | Purpose |
|-----------|---------|
| `post` | Drop a message (subject, body, priority, tags, optional payload dict) |
| `list` | Poll unread — call at agent task start |
| `read` | Full message by id |
| `ack` | Acknowledge (moves to `inbox/acked/`) |
| `ack_all` | Acknowledge all unread |
| `purge` | Delete acked messages older than N days |

**Drop dir:** `CURSOR_INBOX_DIR` env (default `~/.cursor-mcp/inbox/`). No daemon, no network — pure JSON files.

**Who can write:**
- Claude Desktop: `cursor_inbox post` (add cursor-mcp to Claude Desktop MCP config)
- meta_mcp / any fleet server: direct JSON file drop to `CURSOR_INBOX_DIR`
- PowerShell / Python scripts: same
- Sandra: `cursor_inbox post` from any MCP client

**Cursor agent convention:** add `cursor_inbox list` to AGENTS.md or Cursor rules so agents check for messages at the start of every session.

### `cursor_docs`

Fleet snippets. Topics: `cloud-agents`, `profiles`, `mcp-config`, `spend-guardrails`, `cursor-mcp`, `cursor-inbox`, `sdk-jun-2026`, `design-mode`, `auto-review`, `context-canvas`, `changelog-jun-2026`.

### `cursor_sdk`

Read-only SDK guidance (no agent spawn): `capabilities`, `upgrade_notes`, `autoreview_template`, `custom_tools_guide`, `store_options`.

Starter permissions: [docs/permissions.fleet.example.json](docs/permissions.fleet.example.json)

### `cursor_help`

Tool index and setup. Always current.

---

## Auth notes

| Key | Endpoints |
|-----|-----------|
| `CURSOR_API_KEY` | `/v1/me`, `/v1/agents/*` |
| `CURSOR_ADMIN_API_KEY` | `/teams/spend`, `/teams/filtered-usage-events` |

**Individual Pro** without Admin API: `alert_check` still works via cloud agent count + cache; spend/events show `partial_errors` until you add a team admin key.

Poll **at most every 1–2 hours** — Admin API aggregates hourly.

---

## Env

| Variable | Default | Purpose |
|----------|---------|---------|
| `CURSOR_API_KEY` | — | User key, required |
| `CURSOR_ADMIN_API_KEY` | — | Team admin key, optional |
| `CURSOR_MCP_HOST` | `127.0.0.1` | HTTP bind |
| `CURSOR_MCP_PORT` | `11000` | HTTP port |
| `CURSOR_INBOX_DIR` | `~/.cursor-mcp/inbox/` | Message drop dir |
| `CURSOR_HOURLY_SPEND_WARN_CENTS` | `300` | ~$3/h warn |
| `CURSOR_ON_DEMAND_WARN_CENTS` | `2000` | ~$20 on-demand warn |
| `CURSOR_RUNNING_AGENTS_WARN` | `3` | Parallel agents warn |
| `CURSOR_USAGE_EMAIL` | — | Filter spend by email |

Copy [.env.example](.env.example). Never commit real keys.

---

## Fritz task

Scheduled **`coworker_cursor_spend_watch`** — every **2 hours**, emails on `warn` or `critical`.

See [docs/FRITZ_INTEGRATION.md](docs/FRITZ_INTEGRATION.md).

---

## MCPB (Claude Desktop)

```powershell
uv sync
just mcpb-pack
# → dist/cursor-mcp-v0.2.0.mcpb — drag into Claude Desktop Extensions
```

Requires `uv` on PATH. Set `CURSOR_API_KEY` / `CURSOR_ADMIN_API_KEY` in the extension env.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md). Current: **v0.2.0** (2026-06-07) — `cursor_inbox` + MCPB packaging.

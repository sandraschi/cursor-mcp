# cursor-mcp — CHANGELOG

## v0.2.0 — 2026-06-07

### Added

- **`cursor_inbox`** — inter-agent message drop for Cursor agents (new tool, `tools/inbox.py`)
  - Filesystem drop dir: `CURSOR_INBOX_DIR` env (default `~/.cursor-mcp/inbox/`)
  - Operations: `post`, `list`, `read`, `ack`, `ack_all`, `purge`
  - Any sender (Claude Desktop, meta_mcp, PS1 script, Sandra directly) writes messages via `post` or by dropping a JSON file
  - Cursor agent polls with `list` at task start, reads with `read`, acknowledges with `ack`
  - Acked messages move to `inbox/acked/`; `purge` cleans by age (default 7 days)
  - No daemon, no network — pure filesystem
  - Message schema: `id`, `sender`, `subject`, `body`, `priority`, `tags`, `payload`, `sent_at`
- `cursor_docs` topic `cursor-inbox` — full doc snippet with schema, workflow, and who-posts guide
- `cursor_help` now lists `cursor_inbox` operations and `CURSOR_INBOX_DIR`
- `permissions.fleet.example.json` — `cursor_inbox list` added to always-allowed instructions

### Changed

- `server.py` — `cursor_inbox` registered
- `docs.py` — `cursor-inbox` topic added to `Topic` literal and `_SNIPPETS`; `cursor-mcp` snippet updated to include `cursor_inbox` in tools list
- `pyproject.toml` — version bumped to `0.2.0`, description updated
- Version strings aligned in `__init__.py` and `app.py`
- `.env.example` — `CURSOR_INBOX_DIR`, `CURSOR_MCP_CACHE_DIR` documented

### Packaging

- **MCPB** — `mcpb/manifest.json`, `pack.ps1`, `just mcpb-pack` → `dist/cursor-mcp-v0.2.0.mcpb`
- **Git** — initial public repo + GitHub release `v0.2.0`
- **Fleet rule** — workspace `.cursor/rules/cursor-inbox-chat-start.mdc` (poll inbox at Cursor chat start)

---

## v0.1.1 — 2026-06-04

### Added

- `cursor_sdk` tool — Jun 2026 SDK guidance: `capabilities`, `upgrade_notes`, `autoreview_template`, `custom_tools_guide`, `store_options`
- `cursor_docs` topics: `sdk-jun-2026`, `design-mode`, `auto-review`, `context-canvas`, `changelog-jun-2026`
- `docs/permissions.fleet.example.json` — starter autoReview permissions for headless SDK scripts
- Fritz: `CHANGELOG_DIGEST_JUN_2026.md` in mcd (`mcp-central-docs/ecosystem/cursor/`)

### Changed

- `cursor_help` — SDK ops listed; version 0.1.1

---

## v0.1.0 — 2026-06-01

### Initial release

- `cursor_usage` — spend guardrails: `summary`, `spend`, `events`, `alert_check`, `limits`, `me`
- `cursor_cloud` — cloud agent monitoring: `list`, `status`, `runs`, `cancel`
- `cursor_docs` — fleet snippets: `cloud-agents`, `profiles`, `mcp-config`, `spend-guardrails`, `cursor-mcp`
- `cursor_help` — tool index
- HTTP surface on port 11000 for Fritz `fleet_bridge`
- Fritz scheduled task `coworker_cursor_spend_watch` (every 2h)
- `docs/FRITZ_INTEGRATION.md`

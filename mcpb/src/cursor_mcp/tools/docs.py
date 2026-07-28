"""Fleet-curated Cursor doc snippets."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

Topic = Literal[
    "cloud-agents",
    "profiles",
    "mcp-config",
    "spend-guardrails",
    "cursor-mcp",
    "cursor-inbox",
    "sdk-jun-2026",
    "design-mode",
    "auto-review",
    "context-canvas",
    "changelog-jun-2026",
]

_SNIPPETS: dict[str, dict[str, Any]] = {
    "cloud-agents": {
        "title": "Cloud Agents",
        "summary": "Async cloud VMs; always Max Mode; not fleet default.",
        "url": "https://cursor.com/docs/cloud-agents",
        "mcd": "mcp-central-docs/ecosystem/cursor/CLOUD_AGENTS.md",
        "guardrails": [
            "Use Composer 2.5, not Opus, unless necessary",
            "Set cloud spend cap in dashboard",
            "Avoid spinning VMs for context reset",
        ],
    },
    "profiles": {
        "title": "Public Profiles",
        "summary": "cursor.com/@handle — not billing or multi-account.",
        "url": "https://cursor.com/help/account-and-billing/profiles",
        "mcd": "mcp-central-docs/ecosystem/cursor/PROFILES.md",
    },
    "mcp-config": {
        "title": "MCP config",
        "summary": "Windows: %USERPROFILE%\\.cursor\\mcp.json",
        "master": "mcp-central-docs/operations/MASTER_MCP_CONFIG.json",
    },
    "spend-guardrails": {
        "title": "Spend guardrails",
        "summary": "Poll cursor_usage alert_check; Admin API for spend/events; cloud list for runaway agents.",
        "env": [
            "CURSOR_API_KEY",
            "CURSOR_ADMIN_API_KEY (optional, for /teams/spend)",
            "CURSOR_HOURLY_SPEND_WARN_CENTS (default 300)",
            "CURSOR_ON_DEMAND_WARN_CENTS (default 2000)",
            "CURSOR_RUNNING_AGENTS_WARN (default 3)",
        ],
        "dashboard": "https://cursor.com/dashboard",
    },
    "cursor-mcp": {
        "title": "cursor-mcp",
        "summary": "Platform API MCP; complements cursor-app-control (IDE).",
        "tools": ["cursor_usage", "cursor_cloud", "cursor_docs", "cursor_sdk", "cursor_inbox", "cursor_help"],
        "fritz": "coworker_cursor_spend_watch every 2h",
        "port": 11000,
    },
    "cursor-inbox": {
        "title": "cursor_inbox — inter-agent message drop",
        "summary": "Filesystem drop dir for structured messages to Cursor agents. No daemon, no network.",
        "drop_dir": "CURSOR_INBOX_DIR env (default ~/.cursor-mcp/inbox/)",
        "operations": {
            "post": "Any sender drops a message (subject, body, priority, tags, payload).",
            "list": "Cursor agent polls for unread messages at task start.",
            "read": "Read full message by id.",
            "ack": "Acknowledge (moves to inbox/acked/).",
            "ack_all": "Acknowledge all unread at once.",
            "purge": "Delete acked messages older than N days.",
        },
        "who_posts": [
            "Claude Desktop: via cursor_inbox post (cursor-mcp is in Claude's MCP config)",
            "meta_mcp: direct filesystem write to CURSOR_INBOX_DIR",
            "Any PS1/Python script: write JSON to inbox dir directly",
            "Sandra: cursor_inbox post from any MCP client",
        ],
        "message_schema": {
            "id": "uuid4",
            "sender": "e.g. 'claude-desktop', 'meta_mcp', 'sandra'",
            "subject": "one-line subject",
            "body": "plain text or markdown",
            "priority": "low | normal | high | critical",
            "tags": "list of strings e.g. ['meta_mcp', 'cold-install', 'heads-up']",
            "payload": "optional structured data dict",
            "sent_at": "ISO8601 UTC",
        },
        "workflow": "post → list (agent polls at start) → read → ack",
        "note": "cursor_inbox is only needed to READ from Cursor. Any process can WRITE by dropping a JSON file or calling post.",
    },
    "sdk-jun-2026": {
        "title": "SDK Jun 2026",
        "summary": "customTools, autoReview, JSONL stores, nested subagents, requestId.",
        "url": "https://cursor.com/changelog",
        "mcd": "mcp-central-docs/ecosystem/cursor/CHANGELOG_DIGEST_JUN_2026.md",
        "cursor_sdk_ops": ["capabilities", "upgrade_notes", "autoreview_template", "custom_tools_guide"],
        "upgrade": ["npm install @cursor/sdk", "pip install -U cursor-sdk"],
    },
    "design-mode": {
        "title": "Design Mode",
        "summary": "Browser + canvas: multi-select DOM, voice while agent runs, annotate UI.",
        "url": "https://cursor.com/changelog",
        "fleet_use": "Wrapper webapp repos — point at elements instead of prose prompts",
        "browser": "Multi-select elements; voice queues next change mid-run",
        "canvas": "Same annotate model inside agent canvases",
    },
    "auto-review": {
        "title": "Auto-review",
        "summary": "IDE run mode + SDK local.autoReview — classifier for Shell/MCP/Fetch.",
        "ide": "Settings → Agents → Run Mode → Auto-review",
        "sdk": "local.autoReview + permissions.json",
        "example": "cursor-mcp/docs/permissions.fleet.example.json",
        "cursor_sdk_op": "autoreview_template",
    },
    "context-canvas": {
        "title": "Context usage canvas",
        "summary": "Interactive token breakdown — rules, skills, MCP tools, system prompt.",
        "fleet_use": "Run before enabling more MCPs; Debug with Agent to trim bloat",
        "pairs_with": "cursor_usage alert_check + this canvas for diagnosis",
    },
    "changelog-jun-2026": {
        "title": "Changelog digest Jun 2026",
        "summary": "Fleet adoption guide for 3.6–3.7 releases.",
        "mcd": "mcp-central-docs/ecosystem/cursor/CHANGELOG_DIGEST_JUN_2026.md",
        "priority": ["IDE auto-review", "context canvas", "SDK autoReview for CI", "Design Mode webapps"],
    },
}


async def cursor_docs(
    topic: Annotated[Topic, Field(description="Doc topic key.")],
) -> dict[str, Any]:
    """Return fleet-curated Cursor documentation snippets."""
    snippet = _SNIPPETS[topic]
    return {
        "success": True,
        "topic": topic,
        "snippet": snippet,
        "message": snippet.get("title", topic),
    }


async def cursor_help() -> dict[str, Any]:
    """List cursor-mcp tools and setup."""
    return {
        "success": True,
        "version": "0.2.0",
        "tools": {
            "cursor_usage": ["summary", "spend", "events", "alert_check", "limits", "me"],
            "cursor_cloud": ["list", "status", "runs", "cancel"],
            "cursor_docs": list(_SNIPPETS.keys()),
            "cursor_sdk": [
                "capabilities",
                "upgrade_notes",
                "autoreview_template",
                "custom_tools_guide",
                "store_options",
            ],
            "cursor_inbox": ["post", "list", "read", "ack", "ack_all", "purge"],
        },
        "auth": {
            "CURSOR_API_KEY": "User key — cloud agents /v1/*",
            "CURSOR_ADMIN_API_KEY": "Team admin key — /teams/spend, usage events",
        },
        "inbox_dir": "CURSOR_INBOX_DIR env (default ~/.cursor-mcp/inbox/)",
        "fritz_task": "coworker_cursor_spend_watch (every 2h, Europe/Vienna)",
        "changelog_digest": "mcp-central-docs/ecosystem/cursor/CHANGELOG_DIGEST_JUN_2026.md",
        "message": "cursor-mcp v0.2.0 — spend guardrails + inbox + Jun 2026 SDK/docs",
    }

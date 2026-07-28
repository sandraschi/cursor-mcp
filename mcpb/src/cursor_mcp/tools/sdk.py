"""cursor_sdk — fleet guidance for @cursor/sdk / cursor-sdk (Jun 2026)."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

Operation = Literal[
    "capabilities",
    "upgrade_notes",
    "autoreview_template",
    "custom_tools_guide",
    "store_options",
]

_AUTOREVIEW_TEMPLATE = {
    "autoRun": {
        "allow_instructions": [
            "Read-only inspections of build artifacts under ./dist are fine.",
            "cursor_usage with operation summary or alert_check is always allowed.",
        ],
        "block_instructions": [
            "Always pause delete operations and docker compose down.",
            "Pause git push, force push, and any production deploy.",
        ],
    }
}

_CAPABILITIES = {
    "custom_tools": {
        "api": "local.customTools on Agent.create() or per send()",
        "mcp_name": "custom-user-tools",
        "fleet_note": "Thin glue only; keep FastMCP servers for fleet portmanteau + Fritz HTTP",
    },
    "auto_review": {
        "api": "local.autoReview",
        "config": "permissions.json autoRun.allow_instructions / block_instructions",
        "fleet_note": "Required for headless Fritz/CI SDK scripts",
    },
    "stores": ["SqliteLocalAgentStore", "JsonlLocalAgentStore", "LocalAgentStore (custom)"],
    "nested_subagents": "Automatic; subagents inherit parent custom tools",
    "run_correlation": "requestId on every send() — log alongside cursor-mcp spend checks",
    "models": "composer-2 slugs auto-route to composer-2.5",
    "python_fixes": ["workspace-scoped list_runs(cwd=...)", "clearer not-found errors"],
}

_UPGRADE_NOTES = [
    "Jun 4 2026: customTools, autoReview, JSONL stores, nested subagents",
    "Jun 4 2026: requestId on Run/RunResult for log correlation",
    "Jun 4 2026: reliable wait() on local runs; cloud HTTP/1.1 streaming fix",
    "Jun 4 2026: Python cursor-sdk 0.1.6 — workspace list_runs cwd",
    "Upgrade: npm install @cursor/sdk | pip install -U cursor-sdk",
    "MCD: mcp-central-docs/ecosystem/cursor/CHANGELOG_DIGEST_JUN_2026.md",
]


async def cursor_sdk(
    operation: Annotated[Operation, Field(description="SDK guidance operation.")],
) -> dict[str, Any]:
    """Fleet-curated @cursor/sdk / cursor-sdk guidance (read-only, no agent spawn).

    Jun 2026 SDK release: custom tools, auto-review, JSONL stores, nested subagents.
    Use before writing new headless automation — complements cursor_docs topics.
    """
    if operation == "capabilities":
        return {
            "success": True,
            "operation": operation,
            "capabilities": _CAPABILITIES,
            "docs": "https://cursor.com/docs/sdk/typescript",
            "message": "Jun 2026 SDK capabilities summary",
        }

    if operation == "upgrade_notes":
        return {
            "success": True,
            "operation": operation,
            "notes": _UPGRADE_NOTES,
            "changelog": "https://cursor.com/changelog",
            "message": f"{len(_UPGRADE_NOTES)} upgrade notes",
        }

    if operation == "autoreview_template":
        return {
            "success": True,
            "operation": operation,
            "permissions_json": _AUTOREVIEW_TEMPLATE,
            "path_hint": ".cursor/permissions.json or SDK local.permissions path",
            "message": "Starter autoReview permissions.json for fleet scripts",
        }

    if operation == "custom_tools_guide":
        return {
            "success": True,
            "operation": operation,
            "when_to_use": [
                "Single function, no persistence, no HTTP surface",
                "CI one-liner wrapping an internal API",
            ],
            "when_not": [
                "Fleet MCP with portmanteau + concurrency safety",
                "Fritz fleet_bridge over HTTP :port/mcp",
                "Tool catalog >3 operations",
            ],
            "example_shape": "local.customTools=[{name, description, parameters, handler}]",
            "message": "customTools vs full FastMCP server decision guide",
        }

    if operation == "store_options":
        return {
            "success": True,
            "operation": operation,
            "stores": {
                "sqlite": "Default; good for resume on same machine",
                "jsonl": "Append-only; diff and VCS friendly",
                "custom": "Postgres, in-memory CI — implement LocalAgentStore",
            },
            "message": "Agent/run persistence options",
        }

    raise ValueError(f"Unknown operation: {operation}")

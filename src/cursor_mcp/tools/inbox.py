"""cursor_inbox — structured inter-agent message drop for Cursor agents.

Drop directory: CURSOR_INBOX_DIR (default %USERPROFILE%/.cursor-mcp/inbox/)

Any process (Claude Desktop, meta_mcp, a PS1 script, another agent) writes a
JSON message file to the inbox dir. The Cursor agent calls cursor_inbox to read
and acknowledge messages. No polling daemon, no network — pure filesystem drop.

Message file format: <timestamp>-<sender>-<id>.json
Schema: InboxMessage (see below).

Operations
----------
post    Write a new message into the inbox (from any sender).
list    List unread messages (by default) or all.
read    Read a single message by id.
ack     Mark a message as acknowledged (moves to inbox/acked/).
ack_all Acknowledge all unread messages at once.
purge   Delete acknowledged messages older than N days.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

Operation = Literal["post", "list", "read", "ack", "ack_all", "purge"]

Priority = Literal["low", "normal", "high", "critical"]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def _inbox_root() -> Path:
    base = Path(os.environ.get("CURSOR_INBOX_DIR", Path.home() / ".cursor-mcp" / "inbox"))
    base.mkdir(parents=True, exist_ok=True)
    (base / "acked").mkdir(exist_ok=True)
    return base


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S")


def _msg_filename(sender: str, msg_id: str) -> str:
    safe_sender = "".join(c if c.isalnum() or c in "-_" else "_" for c in sender)[:32]
    return f"{_stamp()}-{safe_sender}-{msg_id[:8]}.json"


def _read_msg(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_msg(path: Path, msg: dict[str, Any]) -> None:
    path.write_text(json.dumps(msg, indent=2, ensure_ascii=False), encoding="utf-8")


def _list_inbox(root: Path, *, include_acked: bool = False) -> list[Path]:
    paths = sorted(root.glob("*.json"), key=lambda p: p.name)
    if include_acked:
        paths += sorted((root / "acked").glob("*.json"), key=lambda p: p.name)
    return paths


def _find_by_id(root: Path, msg_id: str, *, include_acked: bool = True) -> Path | None:
    for p in _list_inbox(root, include_acked=include_acked):
        msg = _read_msg(p)
        if msg and msg.get("id") == msg_id:
            return p
    return None


def _msg_summary(msg: dict[str, Any], path: Path) -> dict[str, Any]:
    return {
        "id": msg.get("id"),
        "sender": msg.get("sender"),
        "subject": msg.get("subject"),
        "priority": msg.get("priority", "normal"),
        "sent_at": msg.get("sent_at"),
        "acked": "acked" in str(path),
        "filename": path.name,
    }


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------


async def cursor_inbox(
    operation: Annotated[Operation, Field(description="Inbox operation.")],
    # post
    sender: Annotated[str, Field(description="Sender identity (e.g. 'claude-desktop', 'meta_mcp', 'sandra').")] = "unknown",
    subject: Annotated[str, Field(description="One-line subject.")] = "",
    body: Annotated[str, Field(description="Message body — plain text or markdown.")] = "",
    priority: Annotated[Priority, Field(description="Message priority.")] = "normal",
    tags: Annotated[list[str], Field(description="Optional tags e.g. ['meta_mcp', 'cold-install', 'heads-up'].")] = [],  # noqa: B006
    payload: Annotated[dict[str, Any] | None, Field(description="Optional structured data attached to the message.")] = None,
    # read / ack
    msg_id: Annotated[str | None, Field(description="Message id for read/ack.")] = None,
    # list
    include_acked: Annotated[bool, Field(description="Include acknowledged messages in list.")] = False,
    limit: Annotated[int, Field(description="Max messages to return.", ge=1, le=100)] = 20,
    # purge
    older_than_days: Annotated[int, Field(description="Purge acked messages older than N days.", ge=1, le=365)] = 7,
) -> dict[str, Any]:
    """Inter-agent message drop for Cursor agents.

    Any process writes a message to the shared inbox dir (CURSOR_INBOX_DIR).
    The Cursor agent calls cursor_inbox to poll, read, and acknowledge.

    Typical flow:
      - Claude Desktop / meta_mcp / a script calls 'post' to leave a heads-up.
      - Cursor agent calls 'list' at task start to check for waiting messages.
      - Cursor agent calls 'read' for detail, then 'ack' when handled.
      - Periodic 'purge' to clean old acked messages.

    No daemon, no network — pure filesystem. Default dir: ~/.cursor-mcp/inbox/
    Override with CURSOR_INBOX_DIR env var.
    """
    root = _inbox_root()

    # ------------------------------------------------------------------
    # POST
    # ------------------------------------------------------------------
    if operation == "post":
        if not subject.strip():
            return {"success": False, "message": "subject is required for post"}
        msg_id_new = str(uuid.uuid4())
        msg: dict[str, Any] = {
            "id": msg_id_new,
            "sender": sender.strip() or "unknown",
            "subject": subject.strip(),
            "body": body,
            "priority": priority,
            "tags": tags or [],
            "sent_at": _now_iso(),
            "acked": False,
            "payload": payload,
        }
        filename = _msg_filename(msg["sender"], msg_id_new)
        path = root / filename
        _write_msg(path, msg)
        return {
            "success": True,
            "operation": "post",
            "id": msg_id_new,
            "filename": filename,
            "path": str(path),
            "message": f"Message posted — id {msg_id_new[:8]}",
        }

    # ------------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------------
    if operation == "list":
        paths = _list_inbox(root, include_acked=include_acked)
        summaries = []
        for p in paths:
            msg = _read_msg(p)
            if msg:
                summaries.append(_msg_summary(msg, p))
        summaries = summaries[-limit:]
        unread = sum(1 for s in summaries if not s["acked"])
        return {
            "success": True,
            "operation": "list",
            "unread": unread,
            "total": len(summaries),
            "messages": summaries,
            "inbox_dir": str(root),
            "message": f"{unread} unread message(s)" if unread else "Inbox empty",
        }

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------
    if operation == "read":
        if not msg_id:
            return {"success": False, "message": "msg_id required for read"}
        path = _find_by_id(root, msg_id)
        if not path:
            return {"success": False, "message": f"Message {msg_id[:8]} not found"}
        msg = _read_msg(path)
        if not msg:
            return {"success": False, "message": f"Could not parse {path.name}"}
        return {
            "success": True,
            "operation": "read",
            "message_data": msg,
            "acked": "acked" in str(path),
            "filename": path.name,
            "message": f"Message {msg_id[:8]} — {msg.get('subject', '')}",
        }

    # ------------------------------------------------------------------
    # ACK
    # ------------------------------------------------------------------
    if operation == "ack":
        if not msg_id:
            return {"success": False, "message": "msg_id required for ack"}
        path = _find_by_id(root, msg_id, include_acked=False)
        if not path:
            return {"success": False, "message": f"Unread message {msg_id[:8]} not found (already acked?)"}
        msg = _read_msg(path)
        if not msg:
            return {"success": False, "message": f"Could not parse {path.name}"}
        msg["acked"] = True
        msg["acked_at"] = _now_iso()
        dest = root / "acked" / path.name
        _write_msg(dest, msg)
        path.unlink()
        return {
            "success": True,
            "operation": "ack",
            "id": msg_id,
            "message": f"Message {msg_id[:8]} acknowledged",
        }

    # ------------------------------------------------------------------
    # ACK_ALL
    # ------------------------------------------------------------------
    if operation == "ack_all":
        paths = list(root.glob("*.json"))
        count = 0
        for p in paths:
            msg = _read_msg(p)
            if not msg:
                continue
            msg["acked"] = True
            msg["acked_at"] = _now_iso()
            _write_msg(root / "acked" / p.name, msg)
            p.unlink()
            count += 1
        return {
            "success": True,
            "operation": "ack_all",
            "acknowledged": count,
            "message": f"{count} message(s) acknowledged",
        }

    # ------------------------------------------------------------------
    # PURGE
    # ------------------------------------------------------------------
    if operation == "purge":
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=older_than_days)
        acked_dir = root / "acked"
        removed = 0
        for p in acked_dir.glob("*.json"):
            msg = _read_msg(p)
            if not msg:
                p.unlink(missing_ok=True)
                removed += 1
                continue
            acked_at_str = msg.get("acked_at") or msg.get("sent_at", "")
            try:
                acked_at = datetime.fromisoformat(acked_at_str.replace("Z", "+00:00"))
                if acked_at < cutoff:
                    p.unlink()
                    removed += 1
            except ValueError:
                pass
        return {
            "success": True,
            "operation": "purge",
            "removed": removed,
            "older_than_days": older_than_days,
            "message": f"Purged {removed} acked message(s) older than {older_than_days}d",
        }

    return {"success": False, "message": f"Unknown operation: {operation}"}

"""cursor_cloud portmanteau — cloud agent monitoring."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from ..client import CursorApiError, CursorClient

Operation = Literal["list", "status", "cancel", "runs"]


async def cursor_cloud(
    operation: Annotated[Operation, Field(description="Cloud agent operation.")],
    agent_id: Annotated[str | None, Field(description="Agent id (bc-...). Required for status/cancel/runs.")] = None,
    run_id: Annotated[str | None, Field(description="Run id for cancel.")] = None,
    limit: Annotated[int, Field(description="Page size for list/runs.", ge=1, le=100)] = 20,
) -> dict[str, Any]:
    """List and inspect Cursor cloud agents (read-first; cancel is gated).

    Runaway spend often correlates with many parallel cloud agents — list often.
    """
    client = CursorClient()

    if operation == "list":
        data = await client.list_agents(limit=limit)
        agents = data.get("agents") or []
        return {
            "success": True,
            "operation": operation,
            "count": len(agents),
            "agents": agents,
            "message": f"{len(agents)} cloud agents returned",
        }

    if not agent_id:
        raise CursorApiError("agent_id required for status, runs, and cancel")

    if operation == "status":
        data = await client.get_agent(agent_id)
        return {"success": True, "operation": operation, "agent": data, "message": f"Agent {agent_id}"}

    if operation == "runs":
        data = await client.list_runs(agent_id, limit=limit)
        runs = data.get("runs") or []
        return {
            "success": True,
            "operation": operation,
            "agent_id": agent_id,
            "count": len(runs),
            "runs": runs,
            "message": f"{len(runs)} runs for {agent_id}",
        }

    if operation == "cancel":
        if not run_id:
            raise CursorApiError("run_id required for cancel")
        data = await client.cancel_run(agent_id, run_id)
        return {
            "success": True,
            "operation": operation,
            "agent_id": agent_id,
            "run_id": run_id,
            "result": data,
            "message": f"Cancel requested for run {run_id}",
        }

    raise CursorApiError(f"Unknown operation: {operation}")

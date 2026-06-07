import pytest

from cursor_mcp.tools.sdk import cursor_sdk


@pytest.mark.asyncio
async def test_cursor_sdk_capabilities():
    result = await cursor_sdk("capabilities")
    assert result["success"]
    assert "custom_tools" in result["capabilities"]


@pytest.mark.asyncio
async def test_cursor_sdk_autoreview_template():
    result = await cursor_sdk("autoreview_template")
    assert result["success"]
    assert "autoRun" in result["permissions_json"]

"""Unit and integration tests for FastMCP tools using the Mock Vulcan Test Harness."""

import pytest

try:
    from mcp.server.fastmcp.exceptions import ToolError
except ImportError:
    from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ImageContent

from vulcan_mcp.server import (
    vulcan_block_model,
    vulcan_canvas,
    vulcan_design,
    vulcan_drillholes,
    vulcan_execute_code,
    vulcan_legend,
    vulcan_screenshot,
    vulcan_system,
    vulcan_triangulation,
)

pytestmark = pytest.mark.anyio


@pytest.mark.asyncio
async def test_tool_system_ping_and_inventory(mock_vulcan):
    ping_res = await vulcan_system(action="ping")
    assert ping_res["connected"] is True
    assert "Mock Harness" in ping_res["app"]

    inv_res = await vulcan_system(action="project_info")
    assert inv_res["connected"] is True
    assert "block_models" in inv_res["inventory"]
    assert inv_res["inventory"]["block_models"]["count"] == 1


@pytest.mark.asyncio
async def test_tool_block_model(mock_vulcan):
    # 1. list
    models = await vulcan_block_model(action="list")
    assert "models" in models
    assert "deposit_block_model.bmf" in models["models"]

    # 2. info
    info = await vulcan_block_model(action="info", model="deposit_block_model.bmf")
    assert info["model"] == "deposit_block_model.bmf"
    assert info["dimensions"]["nx"] == 120

    # 3. query_xyz
    val = await vulcan_block_model(
        action="query_xyz", model="deposit_block_model.bmf", x=474500.0, y=4479500.0, z=650.0
    )
    assert val["values"]["CU"] == 1.25

    # 4. stats
    stats = await vulcan_block_model(
        action="stats", model="deposit_block_model.bmf", variable="CU", cutoff=0.5
    )
    assert stats["variable"] == "CU"
    assert stats["mean"] == 0.78


@pytest.mark.asyncio
async def test_tool_triangulation(mock_vulcan):
    tris = await vulcan_triangulation(action="list")
    assert "triangulations" in tris
    assert "orebody_solid.00t" in tris["triangulations"]

    info = await vulcan_triangulation(action="info", name="orebody_solid.00t")
    assert info["is_solid"] is True
    assert info["triangle_count"] == 8420


@pytest.mark.asyncio
async def test_tool_design(mock_vulcan):
    layers = await vulcan_design(action="list_layers", dgd="pit_design.dgd.isis")
    assert "pit_crest" in layers["layers"]

    pts = [[474000.0, 4479000.0, 700.0], [474100.0, 4479100.0, 700.0]]
    res = await vulcan_design(
        action="create_polyline",
        layer="test_layer",
        points=pts,
        closed=False,
    )
    assert res["points_saved"] == 2


@pytest.mark.asyncio
async def test_tool_drillholes(mock_vulcan):
    holes = await vulcan_drillholes(action="list_dbs")
    assert "exploration.dhd.isis" in holes["drillhole_dbs"]

    hole_data = await vulcan_drillholes(action="hole", db="exploration.dhd.isis", hole="DH001")
    assert hole_data["hole"] == "DH001"
    assert hole_data["collar"]["PROFUNDIDAD"] == 250.0


@pytest.mark.asyncio
async def test_tool_legend(mock_vulcan):
    legend = await vulcan_legend(action="inspect", scd="copper_grades.scd")
    assert "DRILL_COLOUR" in legend["schemes"]

    updated = await vulcan_legend(
        action="update",
        scd="copper_grades.scd",
        scheme="DRILL_COLOUR",
        table="COBRE",
        colours=["144", "33"],
    )
    assert updated["intervals_updated"] == 2


@pytest.mark.asyncio
async def test_tool_canvas_and_screenshot(mock_vulcan):
    canvas_res = await vulcan_canvas(action="macro", macro="refresh_all")
    assert canvas_res["success"] is True

    shot = await vulcan_screenshot(max_width=800, quality=75)
    assert isinstance(shot, ImageContent)
    assert shot.type == "image"
    assert shot.mime_type == "image/jpeg"
    assert len(shot.data) > 0


@pytest.mark.asyncio
async def test_tool_execute_code_success_and_failure(mock_vulcan):
    code_res = await vulcan_execute_code(code="print('mining execution')\nresult={'status':'done'}")
    assert code_res["executed"] is True

    # Register error handler on mock server to simulate failure
    mock_vulcan.register_handler(
        "execute_code",
        lambda params: {
            "status": "success",
            "executed": False,
            "traceback": "NameError: name 'invalid_var' is not defined",
            "stdout": "",
        },
    )
    with pytest.raises(ToolError, match="Vulcan script failed"):
        await vulcan_execute_code(code="invalid_var.run()")


@pytest.mark.asyncio
async def test_tool_handles_server_error_envelope(mock_vulcan):
    # Simulate Vulcan reporting an internal domain error
    mock_vulcan.register_handler(
        "block_model",
        lambda params: {
            "status": "error",
            "message": "Block model file not found or corrupted",
        },
    )

    with pytest.raises(ToolError, match="Block model file not found or corrupted"):
        await vulcan_block_model(action="info", model="non_existent.bmf")

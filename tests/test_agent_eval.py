"""Agent Evaluation Harness: Mining Geologist workflow scenarios.

Evaluates multi-step agent scenarios to guarantee reliable execution of:
- Project inventory audits and block model discovery
- Cutoff grade filtering and resource volume estimation
- Drillhole high-grade intercept discovery with 3D display safeguard (<= 300 segments)
- Legend scheme inspection and interval color updates
"""

import pytest

from vulcan_mcp.server import (
    vulcan_block_model,
    vulcan_drillholes,
    vulcan_legend,
    vulcan_system,
    vulcan_triangulation,
)

pytestmark = pytest.mark.anyio


@pytest.mark.asyncio
async def test_scenario_deposit_audit_and_discovery(mock_vulcan):
    """Scenario 1: Agent performs project exploration and discovers assets."""
    # Step 1: Project inventory audit
    inv = await vulcan_system(action="project_info")
    assert inv["connected"] is True
    bm_list = inv["inventory"]["block_models"]["files"]
    tri_list = inv["inventory"]["triangulations"]["files"]
    assert len(bm_list) >= 1
    assert "deposit_block_model.bmf" in bm_list

    # Step 2: Block model variable discovery
    model_name = bm_list[0]
    bm_info = await vulcan_block_model(action="info", model=model_name)
    var_names = [v["name"] for v in bm_info["variables"]]
    assert "CU" in var_names
    assert "DENSITY" in var_names

    # Step 3: Triangulation validation
    tri_name = tri_list[1]  # orebody_solid.00t
    tri_info = await vulcan_triangulation(action="info", name=tri_name)
    assert tri_info["is_solid"] is True
    assert tri_info["extents"]["min_z"] >= bm_info["origin"]["z"]


@pytest.mark.asyncio
async def test_scenario_cutoff_grade_and_resource_reconciliation(mock_vulcan):
    """Scenario 2: Agent calculates resources above cutoff and reconciles with orebody solid."""
    # Step 1: Query Cu grade stats with economic cutoff of 0.8% Cu
    stats = await vulcan_block_model(
        action="stats",
        model="deposit_block_model.bmf",
        variable="CU",
        cutoff=0.8,
    )
    assert stats["blocks_above_cutoff"] > 0
    assert stats["mean"] >= 0.78

    # Step 2: Triangulation solid volume calculation
    vol_res = await vulcan_triangulation(
        action="calculate_volume",
        name="orebody_solid.00t",
    )
    ore_volume = vol_res["volume"]
    assert ore_volume > 0

    # Step 3: Resource tonnage calculation (assuming standard rock density 2.7 t/m^3)
    standard_density = 2.7
    tonnage = ore_volume * standard_density
    assert tonnage == 6615000.0


@pytest.mark.asyncio
async def test_scenario_drillhole_intercepts_and_graphic_safeguard(mock_vulcan):
    """Scenario 3: Agent queries high-grade intercepts and displays 3D traces safely."""
    # Step 1: Query high-grade intercepts (> 1.0% Cu)
    high_grade = await vulcan_drillholes(
        action="high_grade",
        db="exploration.dhd.isis",
        table="LEYES",
        field="CU",
        min_value=1.0,
    )
    intercepts = high_grade["high_grade_intervals"]
    assert len(intercepts) >= 1
    best_intercept = intercepts[0]
    assert best_intercept["value"] >= 1.0

    # Step 2: Query collar and survey coordinates for the top hole
    hole_id = best_intercept["hole"]
    hole_detail = await vulcan_drillholes(
        action="hole",
        db="exploration.dhd.isis",
        hole=hole_id,
    )
    assert hole_detail["collar"]["PROFUNDIDAD"] > 0

    # Step 3: 3D Display with graphic safeguard (max_segments <= 300)
    # Ensuring that the agent passes a prudent limit to protect Vulcan OpenGL thread
    display_res = await vulcan_drillholes(
        action="display",
        db="exploration.dhd.isis",
        holes=[hole_id],
        table="LEYES",
        field="CU",
        max_segments=300,
    )
    assert display_res["displayed_holes"] == 1
    assert display_res["segments_created"] <= 300


@pytest.mark.asyncio
async def test_scenario_legend_calibration_and_colour_update(mock_vulcan):
    """Scenario 4: Agent calibrates Envisage color legend for grade bins."""
    # Step 1: Inspect active legend
    legend_scd = "copper_grades.scd"
    scd_data = await vulcan_legend(action="inspect", scd=legend_scd)
    assert "DRILL_COLOUR" in scd_data["schemes"]

    # Step 2: Update grade bin intervals
    update_res = await vulcan_legend(
        action="update",
        scd=legend_scd,
        scheme="DRILL_COLOUR",
        table="COBRE",
        colours=["144", "33"],  # Vulcan colors: 144 (blue/low), 33 (red/high)
    )
    assert update_res["intervals_updated"] == 2

"""FastMCP Server for Maptek Vulcan 12 Desktop (Master Compound Tools Mode)."""
import asyncio
from typing import Literal

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.exceptions import ToolError
except ImportError:
    from mcp.server.mcpserver import MCPServer as FastMCP
    from mcp.server.mcpserver.exceptions import ToolError

from mcp.types import ImageContent, ToolAnnotations

from vulcan_mcp.client import VulcanMCPClient
from vulcan_mcp.protocol import TIMEOUT_DEFAULT, TIMEOUT_LONG

mcp = FastMCP("Maptek Vulcan MCP")
_client = VulcanMCPClient()


async def _send(command: str, params: dict, timeout: float = TIMEOUT_DEFAULT) -> dict:
    clean = {k: v for k, v in params.items() if v is not None}
    try:
        return await asyncio.to_thread(_client.send_command, command, clean, timeout)
    except Exception as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(
    title="Vulcan System & Project Inventory",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def vulcan_system(
    action: Literal["ping", "project_info", "capabilities"] = "project_info",
) -> dict:
    """Master tool for Vulcan connectivity, active mine project inventory, and SDK capabilities.

    Actions:
    - ping: Check live connection to Maptek Vulcan Desktop.
    - project_info: List all block models (.bmf), triangulations (.00t/.tri), design DBs (.dgd.isis),
      drillhole DBs (.dhd.isis), specifications (.dsf), and legends (.scd) in the active project.
    - capabilities: Inspect available Python modules inside Vulcan (pandas, PIL, win32gui).
    """
    return await _send("system", {"action": action})


@mcp.tool(
    title="Vulcan Block Model Operations (.bmf)",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def vulcan_block_model(
    action: Literal["list", "info", "query_xyz", "stats"],
    model: str | None = None,
    x: float | None = None,
    y: float | None = None,
    z: float | None = None,
    variables: list[str] | None = None,
    variable: str | None = None,
    cutoff: float | None = None,
    density: float | None = None,
    select: str | None = None,
) -> dict:
    """Master tool for inspecting and querying Vulcan block models (.bmf).

    Actions:
    - list: List all .bmf files in the project.
    - info: Get block model origin, extent, block sizes, total blocks, and variable definitions (requires `model`).
    - query_xyz: Read block grades/attributes at world coordinates (`model`, `x`, `y`, `z`, optional `variables`).
    - stats: Compute grade-tonnage statistics, volume-weighted mean, and cutoff summary (`model`, `variable`,
      optional `cutoff`, `density`, `select`).
    """
    return await _send(
        "block_model",
        {
            "action": action,
            "model": model,
            "x": x,
            "y": y,
            "z": z,
            "variables": variables,
            "variable": variable,
            "cutoff": cutoff,
            "density": density,
            "select": select,
        },
        timeout=TIMEOUT_LONG,
    )


@mcp.tool(
    title="Vulcan Triangulations & Surfaces (.00t / .tri)",
    annotations=ToolAnnotations(idempotentHint=True),
)
async def vulcan_triangulation(
    action: Literal["list", "info", "elevation", "point_inside", "load", "unload"],
    name: str | None = None,
    points: list[list[float]] | None = None,
) -> dict:
    """Master tool for 3D triangulations, topography surfaces, and pit shells (.00t / .tri).

    Actions:
    - list: List all triangulation files in the project.
    - info: Return node count, face count, 3D bounding box extent, closure/consistency/crossing state, centroid, and volume (`name`).
    - elevation: Query surface Z elevation at [[x, y], ...] coordinates (`name`, `points`).
    - point_inside: Check whether 3D coordinates [[x, y, z], ...] lie inside a closed triangulation solid (`name`, `points`).
    - load: Display triangulation on Vulcan's 3D graphics screen (`name`).
    - unload: Remove triangulation from Vulcan's 3D graphics screen (`name`).
    """
    return await _send("triangulation", {"action": action, "name": name, "points": points})


@mcp.tool(
    title="Vulcan CAD Design Databases (.dgd.isis)",
)
async def vulcan_design(
    action: Literal["list_dbs", "list_layers", "layer_info", "load_layer", "clear_temp", "create_polyline"],
    dgd: str | None = None,
    layer: str | None = None,
    load_method: Literal["LOAD_IF_EXISTS", "CLEAR_IF_EXISTS", "ACTIVE_IF_EXISTS"] | None = None,
    use_temp_objects: bool | None = None,
    points: list[list[float]] | None = None,
    closed: bool | None = None,
    colour: int | None = None,
    name: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict:
    """Master tool for Vulcan Design Databases (.dgd.isis), layers, and 3D CAD polylines.

    Actions:
    - list_dbs: List all .dgd.isis databases in the project.
    - list_layers: List all layers and object counts inside a DGD (`dgd`).
    - layer_info: Inspect objects inside a layer with pagination (`dgd`, `layer`, optional `limit`, `offset`).
    - load_layer: Render a design layer onto the 3D screen (`dgd`, `layer`, optional `use_temp_objects`, `load_method`).
    - clear_temp: Remove temporary CAD objects displayed on the 3D screen.
    - create_polyline: Create a 3D polyline or closed polygon in a layer (`dgd`, `layer`, `points`,
      optional `closed`, `colour`, `name`).
    """
    return await _send(
        "design",
        {
            "action": action,
            "dgd": dgd,
            "layer": layer,
            "load_method": load_method,
            "use_temp_objects": use_temp_objects,
            "points": points,
            "closed": closed,
            "colour": colour,
            "name": name,
            "limit": limit,
            "offset": offset,
        },
    )


@mcp.tool(
    title="Vulcan Drillhole Databases (.dhd.isis) & 3D Display",
)
async def vulcan_drillholes(
    action: Literal["list_dbs", "schema", "holes", "hole", "high_grade", "display", "clear_display"],
    db: str | None = None,
    hole: str | None = None,
    holes: list[str] | None = None,
    table: str | None = None,
    field: str | None = None,
    min_value: float | None = None,
    mode: Literal["isis", "dgd"] | None = None,
    save_layer: str | None = None,
    max_segments: int | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict:
    """Master tool for ISIS Drillhole Databases (.dhd.isis): collars, surveys, assays, lithology, and 3D display.

    Actions:
    - list_dbs: List all drillhole databases in the project.
    - schema: Return tables (e.g. COLLARES, DIRECCIONES, LEYES, LITOLOGIA), fields, string_fields, and total hole count (`db`).
    - holes: Paginated list of drillhole IDs (`db`, optional `limit`, `offset`).
    - hole: Get collar, survey, assay, and lithology records for a single hole (`db`, `hole`, optional `table`).
    - high_grade: Scan an interval table for the highest-grade intercepts (`db`, `table`, `field`, `min_value`, `limit`).
    - display: Render 3D drillholes in Vulcan's 3D viewport colour-coded by grade (`db`, optional `holes`, `table`, `field`,
      `limit`, `max_segments`, `mode`, `save_layer`).
    - clear_display: Remove rendered 3D drillholes from Vulcan's 3D viewport.
    """
    return await _send(
        "drillholes",
        {
            "action": action,
            "db": db,
            "hole": hole,
            "holes": holes,
            "table": table,
            "field": field,
            "min_value": min_value,
            "mode": mode,
            "save_layer": save_layer,
            "max_segments": max_segments,
            "limit": limit,
            "offset": offset,
        },
        timeout=TIMEOUT_LONG,
    )


@mcp.tool(
    title="Vulcan Envisage Colour Legends (.scd)",
)
async def vulcan_legend(
    action: Literal["list", "inspect", "update", "restore"],
    scd: str | None = None,
    scheme: str | None = None,
    table: str | None = None,
    preset: Literal["high_contrast_mining", "classic_blue_to_red", "traffic_light", "hot_metal"] | None = None,
    colours: list[str] | None = None,
) -> dict:
    """Master tool for reading and updating Maptek Envisage colour legends (.scd).

    Actions:
    - list: List .scd legend files and available colour presets.
    - inspect: Parse all schemes (BLOCK_COLOUR, DRILL_COLOUR, SAMPLES_COLOUR) in a legend (`scd`).
    - update: Update interval colours of a legend table (`scd`, `scheme`, `table`, and `preset` or `colours`).
      Automatically creates a `.scd.bak` backup.
    - restore: Restore a legend from its `.scd.bak` backup (`scd`).
    """
    return await _send(
        "legend",
        {
            "action": action,
            "scd": scd,
            "scheme": scheme,
            "table": table,
            "preset": preset,
            "colours": colours,
        },
    )


@mcp.tool(
    title="Vulcan Viewport Screenshot (Token-Optimised)",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def vulcan_screenshot(
    max_width: int = 800,
    quality: int = 70,
) -> ImageContent:
    """Capture the Maptek Vulcan 3D window as a compressed JPEG image.

    Downscales to `max_width` (default 800px) and encodes as JPEG (`quality=70`)
    to minimise token consumption while preserving clear visual context of the 3D scene.
    """
    res = await _send("canvas", {"action": "screenshot", "max_width": max_width, "quality": quality})
    return ImageContent(type="image", data=res["data"], mimeType=res["mime_type"])


@mcp.tool(
    title="Vulcan GUI & Report Window",
)
async def vulcan_canvas(
    action: Literal["macro", "report"],
    macro: str | None = None,
    text: str | None = None,
) -> dict:
    """Run a Vulcan Workbench macro command or print a message to Vulcan's Report Window."""
    return await _send("canvas", {"action": action, "macro": macro, "text": text})


@mcp.tool(
    title="Execute Python Code in Vulcan",
    annotations=ToolAnnotations(destructiveHint=True),
)
async def vulcan_execute_code(code: str) -> dict:
    """Execute custom Python code inside Vulcan's active session (`vulcan` and `vulcan_gui` preloaded).

    Assign to `result` inside your snippet to return structured JSON values alongside stdout/stderr.
    """
    res = await _send("execute_code", {"code": code}, timeout=TIMEOUT_LONG)
    if not res.get("executed", False):
        raise ToolError(f"Vulcan script failed:\n{res.get('traceback')}\nOutput:\n{res.get('stdout')}")
    return res


def main():
    mcp.run()


if __name__ == "__main__":
    main()

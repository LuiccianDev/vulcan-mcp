---
name: vulcan-tools-catalog
description: Comprehensive technical reference and action catalog for the 9 Vulcan MCP Master Compound Tools (signatures, parameter types, defaults, return schemas, error handling, and invocation recipes).
---

# Vulcan MCP Master Tools Catalog

The **Vulcan MCP** server exposes **9 Master Compound Tools** to Model Context Protocol clients (Google Antigravity, Claude Desktop, Cursor, VS Code). Each tool consolidates related mining operations under an `action` selector, minimising schema overhead and ensuring predictable, high-speed execution against Maptek Vulcan 12 Desktop.

---

## Tool Overview Matrix

| # | MCP Tool Name | Domain / Subsystem | Primary Operations (`action=`) | Timeout |
| :-: | :--- | :--- | :--- | :---: |
| 1 | `vulcan_system` | Connection & Project Inventory | `ping`, `project_info`, `capabilities` | `30s` |
| 2 | `vulcan_block_model` | Block Models (`.bmf`) | `list`, `info`, `query_xyz`, `stats` | `120s` |
| 3 | `vulcan_triangulation` | 3D Surfaces & Solids (`.00t`/`.tri`) | `list`, `info`, `elevation`, `point_inside`, `load`, `unload` | `30s` |
| 4 | `vulcan_design` | 3D CAD Design DBs (`.dgd.isis`) | `list_dbs`, `list_layers`, `layer_info`, `load_layer`, `clear_temp`, `create_polyline` | `30s` |
| 5 | `vulcan_drillholes` | ISIS Drillhole DBs (`.dhd.isis`) | `list_dbs`, `schema`, `holes`, `hole`, `high_grade`, `display`, `clear_display` | `120s` |
| 6 | `vulcan_legend` | Envisage Legends (`.scd`) | `list`, `inspect`, `update`, `restore` | `30s` |
| 7 | `vulcan_screenshot` | Viewport Visual Inspection | Direct parameters (`max_width`, `quality`) | `30s` |
| 8 | `vulcan_canvas` | UI & Reporting | `macro`, `report` | `30s` |
| 9 | `vulcan_execute_code` | PyVulcan Python 3.5 Automation | Direct parameter (`code`) | `120s` |

---

## Detailed Tool Specifications

### 1. `vulcan_system` — Connection & Project Inventory
* **Purpose**: Verify live TCP communication with Vulcan Desktop, inventory mining project files, and detect installed Python SDK modules.
* **Parameters**:
  * `action` (`str`, optional, default: `"project_info"`): One of `"ping"`, `"project_info"`, `"capabilities"`.
* **Actions & Return Schemas**:
  * `action="ping"`:
    ```json
    {
      "connected": true,
      "app": "Maptek Vulcan",
      "python": "3.5.2",
      "vulcan_api": true,
      "project_dir": "C:\\MiningProjects\\Deposit_A"
    }
    ```
  * `action="project_info"`:
    ```json
    {
      "project_dir": "C:\\MiningProjects\\Deposit_A",
      "block_models": ["deposit_bmf.bmf"],
      "triangulations": ["topo.00t", "pit_design.00t"],
      "design_dbs": ["pit_cad.dgd.isis"],
      "drillhole_dbs": ["resource_drilling.dhd.isis"],
      "legends": ["grade_cut.scd"]
    }
    ```
  * `action="capabilities"`:
    ```json
    {
      "maptek.vulcan": true,
      "maptek.vulcan_gui": true,
      "pandas": true,
      "PIL": true,
      "win32gui": true
    }
    ```

---

### 2. `vulcan_block_model` — Block Models (`.bmf`)
* **Purpose**: Inspect spatial extents, variable schemas, point coordinate queries, and volume-weighted resource calculations on regular or sub-blocked `.bmf` models.
* **Parameters**:
  * `action` (`str`, required): `"list"`, `"info"`, `"query_xyz"`, or `"stats"`.
  * `model` (`str`, optional): Block model filename (e.g. `"copper_deposit.bmf"`). Required for `info`, `query_xyz`, `stats`.
  * `x`, `y`, `z` (`float`, optional): World coordinates. Required for `action="query_xyz"`.
  * `variables` (`list[str]`, optional): Specific block variable names to retrieve in `query_xyz`.
  * `variable` (`str`, optional): Target numeric variable (e.g. `"CU"`, `"AU"`, `"DENS"`) for `action="stats"`.
  * `cutoff` (`float`, optional): Minimum cut-off threshold for `action="stats"`.
  * `density` (`float`, optional): Fallback specific gravity / density if not modeled in the block model.
  * `select` (`str`, optional): Selection expression (e.g. `"ROCK == 'SULF'"`).
* **Actions & Return Schemas**:
  * `action="info"`: Returns bounding box, block counts, origin, rotation, and schema variables with types and descriptions.
  * `action="query_xyz"`: Returns the properties and grade attributes of the block enclosing $(X, Y, Z)$.
  * `action="stats"`:
    ```json
    {
      "variable": "CU",
      "total_blocks": 150000,
      "filtered_blocks": 42100,
      "min": 0.01,
      "max": 4.52,
      "mean": 0.65,
      "volume_weighted_mean": 0.72,
      "total_volume_m3": 10525000.0,
      "total_tonnage": 28417500.0,
      "cutoff": 0.4,
      "tonnage_above_cutoff": 19540000.0,
      "grade_above_cutoff": 0.95
    }
    ```

---

### 3. `vulcan_triangulation` — 3D Surfaces & Solids (`.00t` / `.tri`)
* **Purpose**: Query topographic surfaces, check solid closure and consistency, calculate volume, sample $Z$ elevations, and perform 3D point-in-solid checks.
* **Parameters**:
  * `action` (`str`, required): `"list"`, `"info"`, `"elevation"`, `"point_inside"`, `"load"`, `"unload"`.
  * `name` (`str`, optional): Triangulation filename (e.g. `"topo.00t"`, `"orebody.00t"`).
  * `points` (`list[list[float]]`, optional): Coordinate points array:
    * For `action="elevation"`: `[[x1, y1], [x2, y2], ...]`.
    * For `action="point_inside"`: `[[x1, y1, z1], [x2, y2, z2], ...]`.
* **Actions & Return Schemas**:
  * `action="info"`:
    ```json
    {
      "name": "orebody.00t",
      "nodes": 4520,
      "faces": 9036,
      "closed": true,
      "consistent": true,
      "crossing": false,
      "volume": 2541000.0,
      "centroid": [15240.5, 22100.8, 1450.2]
    }
    ```
  * `action="elevation"`: Interpolates exact $Z$ elevations on the triangulation surface for given $(X, Y)$ pairs.
  * `action="point_inside"`: Returns boolean containment status (`inside: true/false`) for each 3D point.
  * `action="load"` / `"unload"`: Displays or hides the triangulation in Envisage's 3D graphics view.

---

### 4. `vulcan_design` — 3D CAD Design Databases (`.dgd.isis`)
* **Purpose**: Manage CAD layers, audit bench crests/toes, digitize polylines/polygons, and calculate planar surface areas ($m^2$).
* **Parameters**:
  * `action` (`str`, required): `"list_dbs"`, `"list_layers"`, `"layer_info"`, `"load_layer"`, `"clear_temp"`, `"create_polyline"`.
  * `dgd` (`str`, optional): Design database filename (e.g. `"pit_mine.dgd.isis"`).
  * `layer` (`str`, optional): Target layer name (e.g. `"BENCH_2100"`).
  * `load_method` (`str`, optional): `"LOAD_IF_EXISTS"`, `"CLEAR_IF_EXISTS"`, or `"ACTIVE_IF_EXISTS"`.
  * `use_temp_objects` (`bool`, optional): If true, renders without saving permanently to the layer.
  * `points` (`list[list[float]]`, optional): 3D coordinates `[[x, y, z], ...]`.
  * `closed` (`bool`, optional): True for closed polygon, false for open string.
  * `colour` (`int`, optional): Vulcan palette color index (e.g. `1` for red, `2` for green).
  * `name` (`str`, optional): Name tag for the polyline or polygon object.
  * `limit`, `offset` (`int`, optional): Pagination for `action="layer_info"`.
* **Actions & Return Schemas**:
  * `action="layer_info"`:
    ```json
    {
      "layer": "BENCH_2100",
      "object_count": 12,
      "objects": [
        {
          "name": "TOE_NORTH",
          "points": 45,
          "length": 420.5,
          "closed": true,
          "planar_area_m2": 15200.0,
          "centroid": [14200.0, 18500.0, 2100.0]
        }
      ]
    }
    ```

---

### 5. `vulcan_drillholes` — ISIS Drillhole Databases (`.dhd.isis`)
* **Purpose**: Inspect drilling database structures, collars, surveys, assays, scan for high-grade intercepts, and render 3D desurveyed drill traces.
* **Parameters**:
  * `action` (`str`, required): `"list_dbs"`, `"schema"`, `"holes"`, `"hole"`, `"high_grade"`, `"display"`, `"clear_display"`.
  * `db` (`str`, optional): Drillhole database name (e.g. `"drilling.dhd.isis"`).
  * `hole` (`str`, optional): Single hole ID (e.g. `"DH_101"`).
  * `holes` (`list[str]`, optional): Array of hole IDs to display.
  * `table` (`str`, optional): Table name (supports bilingual: `"ASSAYS"` or `"LEYES"`).
  * `field` (`str`, optional): Target assay field (e.g. `"CU"`, `"AU"`).
  * `min_value` (`float`, optional): Minimum threshold for `high_grade` intercept filtering.
  * `mode` (`str`, optional): `"isis"` (default) or `"dgd"`.
  * `save_layer` (`str`, optional): Layer name if persisting traces into a design database.
  * `max_segments` (`int`, optional, default: `300`): Maximum temporary graphics segments allowed ($\le 300$ safeguard).
  * `limit`, `offset` (`int`, optional): Pagination control.
* **Bilingual Mapping Support**:
  * Automatically handles English and Spanish ISIS column names (`COLLARS`/`COLLARES`, `SURVEY`/`BUZAMIENTO`/`DIRECCIONES`, `ASSAYS`/`LEYES`, `DIP`/`BUZ`, `FROM`/`DESDE`, `TO`/`HASTA`).

---

### 6. `vulcan_legend` — Envisage Colour Legends (`.scd`)
* **Purpose**: Inspect and update color scheme ranges for block models and drillhole displays with automatic backup.
* **Parameters**:
  * `action` (`str`, required): `"list"`, `"inspect"`, `"update"`, `"restore"`.
  * `scd` (`str`, optional): Legend filename (e.g. `"grades.scd"`).
  * `scheme` (`str`, optional): Scheme category (e.g. `"BLOCK_COLOUR"`, `"DRILL_COLOUR"`).
  * `table` (`str`, optional): Scheme subtable (e.g. `"CU_GRADES"`).
  * `preset` (`str`, optional): Predefined palette (`"high_contrast_mining"`, `"classic_blue_to_red"`, `"traffic_light"`, `"hot_metal"`).
  * `colours` (`list[str]`, optional): Custom list of color names or hex strings.
* **Automatic Safety**:
  * Every update creates an automatic `.scd.bak` backup file, restorable via `action="restore"`.

---

### 7. `vulcan_screenshot` — Token-Optimised 3D Viewport Capture
* **Purpose**: Capture the active Envisage 3D window for multimodal inspection (visual confirmation of digitizing, drillholes, stopes, and camera angles).
* **Parameters**:
  * `max_width` (`int`, optional, default: `800`): Maximum horizontal image width in pixels.
  * `quality` (`int`, optional, default: `70`): JPEG compression quality (1-100).
* **Return**: Direct MCP `ImageContent` object (`mime_type="image/jpeg"`), minimising token overhead while preserving clarity.

---

### 8. `vulcan_canvas` — Macros & Report Window
* **Purpose**: Trigger Envisage Workbench macros or post messages into Vulcan's integrated Report Window.
* **Parameters**:
  * `action` (`str`, required): `"macro"` or `"report"`.
  * `macro` (`str`, optional): Macro command string to run inside Envisage.
  * `text` (`str`, optional): Message string to print into Vulcan's report log.

---

### 9. `vulcan_execute_code` — Direct PyVulcan Scripting
* **Purpose**: Execute arbitrary Python automation snippets inside Maptek Vulcan's embedded Python 3.5 interpreter.
* **Parameters**:
  * `code` (`str`, required): Python 3.5 compatible script.
* **Runtime Constraints**:
  * **Strict Python 3.5.2**: Do NOT use f-strings (`f"..."`) or variable type annotations. Use `.format()`.
  * **Pre-injected Variables**: `vulcan` (`maptek.vulcan`), `vulcan_gui` (`maptek.vulcan_gui`), `project_dir` (absolute path string).
  * **Return Variable**: Assign output to `result = ...` to return structured JSON data.
  * **Main Thread Execution**: Scripts execute synchronously on the main GUI thread to maintain Envisage OpenGL context stability.

---

## Error Handling & Troubleshooting Guide

| Error Type | Probable Cause | Corrective Action |
| :--- | :--- | :--- |
| `ConnectionError` | The internal listener is not running inside Maptek Vulcan. | Start the listener inside Vulcan Desktop: `File > Python Script > vulcan_listener/server.py` (checking *"Run in shell window"*). |
| `CommandTimeout` | Vulcan Desktop has a blocking modal dialog open on screen. | Advise the user to inspect Vulcan Desktop and click OK or Cancel to unblock the main thread. |
| `ToolError` | Invalid parameter, missing mandatory argument, or Python syntax error in `vulcan_execute_code`. | Check tool parameters, ensure Python 3.5 syntax, and inspect the traceback returned in the error payload. |
| `AuthenticationError` | Non-loopback binding without valid token or mismatched `VULCAN_MCP_TOKEN`. | Verify `VULCAN_MCP_TOKEN` matches across both the listener and the AI client environment. |

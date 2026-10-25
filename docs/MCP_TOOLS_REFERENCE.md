# Complete MCP Tools Reference (Master Tools Catalog)

Detailed technical reference for the **9 Master Compound Tools** exposed by **Vulcan MCP** to Model Context Protocol clients (Google Antigravity, Claude Desktop, Cursor, VS Code).

---

## Executive Summary of Tools

| # | MCP Tool | Mining Domain | Available Actions (`action=`) | Timeout |
| :-: | :--- | :--- | :--- | :---: |
| 1 | **`vulcan_system`** | System & Inventory | `ping`, `project_info`, `capabilities` | `30s` |
| 2 | **`vulcan_block_model`** | Block Models (`.bmf`) | `list`, `info`, `query_xyz`, `stats` | `120s` |
| 3 | **`vulcan_triangulation`** | Surfaces & Solids (`.00t`/`.tri`) | `list`, `info`, `elevation`, `point_inside`, `load`, `unload` | `30s` |
| 4 | **`vulcan_design`** | 3D CAD Design (`.dgd.isis`) | `list_dbs`, `list_layers`, `layer_info`, `load_layer`, `clear_temp`, `create_polyline` | `30s` |
| 5 | **`vulcan_drillholes`** | ISIS Drillholes (`.dhd.isis`) | `list_dbs`, `schema`, `holes`, `hole`, `high_grade`, `display`, `clear_display` | `120s` |
| 6 | **`vulcan_legend`** | Envisage Legends (`.scd`) | `list`, `inspect`, `update`, `restore` | `30s` |
| 7 | **`vulcan_screenshot`** | 3D Viewport Capture | *(Direct: `max_width`, `quality`)* | `30s` |
| 8 | **`vulcan_canvas`** | Interface & Macros | `macro`, `report` | `30s` |
| 9 | **`vulcan_execute_code`** | PyVulcan Scripting | *(Direct: `code`)* | `120s` |

---

## 1. `vulcan_system` — Connectivity, Inventory & Capabilities

Verifies the status of the Vulcan listener socket (`127.0.0.1:9877`) and inventories all mining files in the active project directory.

### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :---: | :--- |
| `action` | `"ping" \| "project_info" \| "capabilities"` | Yes | `"project_info"` | System operation to execute. |

### Response Examples
* **`action="ping"`**:
  ```json
  {
    "connected": true,
    "app": "Maptek Vulcan",
    "python": "3.5.2",
    "vulcan_api": true,
    "project_dir": "C:\\MiningProjects\\CopperDeposit_Project"
  }
  ```
* **`action="capabilities"`**:
  ```json
  {
    "maptek.vulcan": true,
    "maptek.vulcan_gui": true,
    "pandas": true,
    "PIL": true,
    "win32gui": true,
    "gfx": false
  }
  ```

---

## 2. `vulcan_block_model` — Block Models (`.bmf`)

Geometric inspection, spatial queries $(X, Y, Z)$, and volume-weighted statistical resource estimation over `.bmf` files.

### Parameters
| Parameter | Type | Required In | Description |
| :--- | :--- | :--- | :--- |
| `action` | `"list" \| "info" \| "query_xyz" \| "stats"` | All | Action to execute on block models. |
| `model` | `str` | `info`, `query_xyz`, `stats` | Name of the `.bmf` file (e.g., `"bmw_ml_30_30_30.bmf"`). |
| `x`, `y`, `z` | `float` | `query_xyz` | World coordinates $(X, Y, Z)$ to sample. |
| `variables` | `list[str]` | Optional in `query_xyz` | List of variables to read (if omitted, reads all). |
| `variable` | `str` | `stats` | Numeric variable to estimate (e.g., `"CUT"`). |
| `cutoff` | `float` | Optional in `stats` | Cutoff grade to filter `variable >= cutoff`. |
| `density` | `float` | Optional in `stats` | Mean density ($t/m^3$) to calculate tonnage (`tonnes = volume * density`). |
| `select` | `str` | Optional in `stats` | Vulcan selection filter expression. |

### Response Example (`action="stats"`)
```json
{
  "variable": "CUT",
  "select": "",
  "excluded_default": -99.0,
  "summary": {
    "blocks": 14520,
    "min": 0.01,
    "max": 4.85,
    "mean": 0.62,
    "volume_weighted_mean": 0.64,
    "volume": 392040000.0,
    "tonnes": 1058508000.0
  },
  "above_cutoff": {
    "cutoff": 0.5,
    "blocks": 7840,
    "min": 0.5,
    "max": 4.85,
    "mean": 0.98,
    "volume_weighted_mean": 1.01,
    "volume": 211680000.0,
    "tonnes": 571536000.0
  }
}
```

---

## 3. `vulcan_triangulation` — 3D Surfaces & Solids (`.00t` / `.tri`)

Geometric analysis, topological closure validation, $Z$ elevation interpolation, point-in-solid testing, and 3D display.

### Parameters
| Parameter | Type | Required In | Description |
| :--- | :--- | :--- | :--- |
| `action` | `"list" \| "info" \| "elevation" \| "point_inside" \| "load" \| "unload"` | All | Triangulation operation to execute. |
| `name` | `str` | All except `list` | Name of the `.00t` or `.tri` file (e.g., `"topography_1.00t"`). |
| `points` | `list[list[float]]` | `elevation`, `point_inside` | In `elevation`: `[[x, y], ...]`. In `point_inside`: `[[x, y, z], ...]`. |

### Response Example (`action="info"`)
```json
{
  "name": "topography_1.00t",
  "nodes": 2201,
  "faces": 4224,
  "extent": [[474025.37, 4479261.5, 546.97], [475294.53, 4480530.66, 673.17]],
  "closed": false,
  "consistent": true,
  "crossing": false,
  "ok": true,
  "centroid": [474665.49, 4479896.76, 634.80]
}
```

---

## 4. `vulcan_design` — 3D CAD Design Databases (`.dgd.isis`)

Exploration, planar area computation, and creation of 3D polylines/polygons in `.dgd.isis` design databases.

### Parameters
| Parameter | Type | Required In | Description |
| :--- | :--- | :--- | :--- |
| `action` | `"list_dbs" \| "list_layers" \| "layer_info" \| "load_layer" \| "clear_temp" \| "create_polyline"` | All | CAD action to execute. |
| `dgd` | `str` | `list_layers`, `layer_info`, `load_layer`, `create_polyline` | `.dgd.isis` database file. |
| `layer` | `str` | `layer_info`, `load_layer`, `create_polyline` | Name of the design layer (e.g., `"PIT_BENCH_100"`). |
| `points` | `list[list[float]]` | `create_polyline` | List of 3D vertices `[[x, y, z], ...]` (minimum 2 points). |
| `closed` | `bool` | Optional in `create_polyline` | If `True`, closes polyline as a polygon. |
| `colour` | `int` | Optional in `create_polyline` | Vulcan palette color index (`1`=Red, `2`=Green, etc.). |
| `name` | `str` | Optional in `create_polyline` | Identifying name for the CAD object. |
| `use_temp_objects` | `bool` | Optional in `load_layer` | Defaults to `True` (renders via `vg.temp_object` without locking). |
| `limit`, `offset` | `int` | Optional in `layer_info` | Object pagination (default `limit=20`, `offset=0`). |

---

## 5. `vulcan_drillholes` — ISIS Drillholes (`.dhd.isis`) & 3D Desurvey

Relational queries on drilling databases, high-grade intercept discovery, and grade-colored 3D desurveyed display.

### Parameters
| Parameter | Type | Required In | Description |
| :--- | :--- | :--- | :--- |
| `action` | `"list_dbs" \| "schema" \| "holes" \| "hole" \| "high_grade" \| "display" \| "clear_display"` | All | Action on drillhole database. |
| `db` | `str` | `schema`, `holes`, `hole`, `high_grade`, `display` | `.dhd.isis` database file. |
| `hole` | `str` | `hole` | Single drillhole ID (e.g., `"DH001"`). |
| `holes` | `list[str]` | Optional in `display` | Specific drillhole IDs to render. |
| `table` | `str` | `high_grade` (optional in `hole`, `display`) | ISIS table (e.g., `"ASSAYS"`, `"COLLARS"`, `"SURVEY"`). |
| `field` | `str` | `high_grade` (optional in `display`) | Numeric grade field (e.g., `"CU"`). |
| `min_value` | `float` | `high_grade` | Minimum cutoff value to filter high-grade intervals. |
| `limit` | `int` | Optional | Maximum number of records, holes, or top intercepts. |
| `max_segments` | `int` | Optional in `display` | 3D segment limit in Envisage (default `300`). |
| `save_layer` | `str` | Optional in `display` | Save generated 3D traces into a `.dgd.isis` CAD layer. |

---

## 6. `vulcan_legend` — Envisage Color Legends (`.scd`)

Inspection and modification of `.scd` color schemes with automated `.scd.bak` backup.

### Parameters
| Parameter | Type | Required In | Description |
| :--- | :--- | :--- | :--- |
| `action` | `"list" \| "inspect" \| "update" \| "restore"` | All | Action on legend file. |
| `scd` | `str` | `inspect`, `update`, `restore` | `.scd` file name. |
| `scheme` | `str` | `update` | Scheme inside `.scd` (e.g., `"DRILL_COLOUR"`, `"BLOCK_COLOUR"`). |
| `table` | `str` | `update` | Table inside scheme (e.g., `"COPPER"`, `"ASSAYS"`). |
| `preset` | `"high_contrast_mining" \| "classic_blue_to_red" \| "traffic_light" \| "hot_metal"` | `update` (or `colours`) | Predefined mining color palette. |
| `colours` | `list[str]` | `update` (or `preset`) | Custom list of Vulcan color codes. |

---

## 7. `vulcan_screenshot` — Optimized 3D Viewport Capture

Locates the active Maptek Vulcan window via `win32gui`, captures the 3D canvas, resizes maintaining aspect ratio, and compresses to JPEG.

* **`max_width`** (`int`, default `800`): Maximum width in pixels.
* **`quality`** (`int`, default `70`): JPEG compression quality (`1-95`).
* **Return**: `ImageContent` object (`mimeType="image/jpeg"`) for LLM multimodal vision.

---

## 8. `vulcan_canvas` — Macros & Report Console

* **`action="macro"`** (`macro: str`): Executes an Envisage Workbench macro command (`vg.workbench_macro`).
* **`action="report"`** (`text: str`): Prints a message to Vulcan's report window (`vg.print_message`).

---

## 9. `vulcan_execute_code` — Direct PyVulcan Scripting

Executes Python routines directly inside Vulcan's embedded Python 3.5.2 interpreter.
* **Pre-injected variables**: `vulcan` (`maptek.vulcan`), `vulcan_gui` (`maptek.vulcan_gui`), `project_dir` (active project path).
* **Return data**: Assign any dictionary, list, or scalar to the `result` variable.
* **Important constraint**: Write **Python 3.5 compatible code** (use `.format()` instead of *f-strings*).

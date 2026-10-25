---
name: vulcan-tools-catalog
description: Complete catalog and quick guide for the 9 Vulcan MCP Master Tools (actions, required/optional parameters, and return schemas).
---

# The 9 Master Tools Catalog (Vulcan MCP)

Use this reference to select the exact tool and parameters for every operation on Maptek Vulcan 12 Desktop.

---

## 1. `vulcan_system` — Connectivity & Project Inventory
* **Actions (`action=`)**:
  * `"ping"`: Check live TCP connection to Vulcan (`connected`, `python`, `project_dir`).
  * `"project_info"`: Inventory all mining assets in the active directory (`block_models`, `triangulations`, `design_dbs`, `drillhole_dbs`, `legends`).
  * `"capabilities"`: Check available Python modules in Vulcan's environment (`pandas`, `PIL`, `win32gui`).

---

## 2. `vulcan_block_model` — Block Models (`.bmf`)
* **Actions (`action=`)**:
  * `"list"`: List `.bmf` files.
  * `"info"`: Requires `model`. Returns `n_blocks`, `origin`, `orientation`, `world_extent`, `schemas`, and `variables` list (type, default value, description).
  * `"query_xyz"`: Requires `model`, `x`, `y`, `z` (optional `variables`). Returns grades and dimensions of the block at that coordinate.
  * `"stats"`: Requires `model`, `variable` (optional `cutoff`, `density`, `select`). Calculates block counts, min, max, arithmetic mean, **volume-weighted mean**, volume ($m^3$), and total and cutoff **tonnage**.

---

## 3. `vulcan_triangulation` — 3D Surfaces & Solids (`.00t` / `.tri`)
* **Actions (`action=`)**:
  * `"list"`: List `.00t` and `.tri` files.
  * `"info"`: Requires `name`. Returns `nodes`, `faces`, `extent`, `closed`, `consistent`, `crossing`, `ok`, `centroid` $[X, Y, Z]$, and `volume` (if closed).
  * `"elevation"`: Requires `name` and `points=[[x, y], ...]`. Returns interpolated $Z$ elevations on the surface.
  * `"point_inside"`: Requires `name` and `points=[[x, y, z], ...]`. Returns `inside: True/False` for each 3D point.
  * `"load"` / `"unload"`: Requires `name`. Loads or unloads the triangulation in Envisage's 3D viewport.

---

## 4. `vulcan_design` — 3D CAD Design Databases (`.dgd.isis`)
* **Actions (`action=`)**:
  * `"list_dbs"`: List `.dgd.isis` design databases.
  * `"list_layers"`: Requires `dgd`. Lists all layers and their object counts.
  * `"layer_info"`: Requires `dgd`, `layer` (optional `limit`, `offset`). Returns objects with `name`, `points`, `length`, `closed`, `planar_area` ($m^2$), and `centroid` $[X, Y, Z]$.
  * `"load_layer"`: Requires `dgd`, `layer` (optional `use_temp_objects=True`, `load_method`). Renders the layer in the 3D window.
  * `"clear_temp"`: Clears temporary CAD objects from the 3D viewport.
  * `"create_polyline"`: Requires `dgd`, `layer`, `points=[[x, y, z], ...]` (optional `closed`, `colour`, `name`). Creates and saves a 3D polyline or polygon.

---

## 5. `vulcan_drillholes` — ISIS Drillhole Databases (`.dhd.isis`)
* **Actions (`action=`)**:
  * `"list_dbs"`: List `.dhd.isis` drillhole databases.
  * `"schema"`: Requires `db`. Returns drillhole counts (`holes`), tables (`COLLARS`, `SURVEY`, `ASSAYS`, `LITHOLOGY`), and fields.
  * `"holes"`: Requires `db` (optional `limit`, `offset`). Paginated list of `HOLE_ID` keys.
  * `"hole"`: Requires `db`, `hole` (optional `table`, `limit`). Extracts records for a single drillhole.
  * `"high_grade"`: Requires `db`, `table`, `field`, `min_value` (optional `limit`). Scans the database for top mineral intercepts.
  * `"display"`: Requires `db` (optional `holes`, `table="ASSAYS"`, `field="CUT"`, `limit=5`, `max_segments=300`, `save_layer`). Computes 3D desurvey and renders grade-colored intervals in Envisage.
  * `"clear_display"`: Clears temporary drillhole traces from the 3D display.

---

## 6. `vulcan_legend` — Envisage Color Legends (`.scd`)
* **Actions (`action=`)**:
  * `"list"`: Lists `.scd` files and presets (`high_contrast_mining`, `classic_blue_to_red`, `traffic_light`, `hot_metal`).
  * `"inspect"`: Requires `scd`. Displays schemes (`BLOCK_COLOUR`, `DRILL_COLOUR`) and intervals.
  * `"update"`: Requires `scd`, `scheme`, `table`, and `preset` (or `colours`). Updates colors and creates automatic `.scd.bak` backup.
  * `"restore"`: Requires `scd`. Restores the file from `.scd.bak`.

---

## 7. `vulcan_screenshot` — Optimized 3D Viewport Capture
* **Parameters**: `max_width=800`, `quality=70`.
* **Return**: Compressed JPEG image of Maptek Vulcan's 3D window for low token-overhead visual inspection.

---

## 8. `vulcan_canvas` — Macros & Report Window
* **Actions (`action=`)**:
  * `"macro"`: Requires `macro`. Executes an Envisage Workbench macro command.
  * `"report"`: Requires `text`. Prints a message into Vulcan's report window.

---

## 9. `vulcan_execute_code` — Direct PyVulcan Scripting
* **Parameters**: `code` (Python 3.5 compatible code string; assign output to `result = ...`).
* **Return**: `executed`, `result`, `stdout`, `stderr`. Has `vulcan`, `vulcan_gui`, and `project_dir` pre-injected.

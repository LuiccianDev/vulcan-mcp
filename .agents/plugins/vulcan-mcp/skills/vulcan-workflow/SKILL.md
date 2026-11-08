---
name: vulcan-workflow
description: Guided mining workflows for interacting with Maptek Vulcan 12 Desktop via Vulcan MCP (project audits, block model estimation, drillholes, and 3D screenshots).
---

# Mining Workflows with Vulcan MCP

This skill provides step-by-step procedures to interact safely, dynamically, and efficiently with Maptek Vulcan 12 Desktop.

---

## 0. Connectivity Diagnostics & Dynamic Port Handling

Prior to running complex workflows or when encountering a `ConnectionError` / `CommandTimeout`:

1. **Verify Socket Connection**:
   * Call `vulcan_system` with `action="ping"`.
2. **If Connection Fails (`ConnectionError`)**:
   * **Cause 1 (Execution Order)**: Confirm that `vulcan_listener/server.py` was started inside Vulcan Desktop first (**File > Python Script > vulcan_listener/server.py**, checking *"Run in shell window"*).
   * **Cause 2 (Port Conflict)**: If port `9877` is in use by another process or multiple Vulcan instances, configure a dynamic port via `"env": {"VULCAN_MCP_PORT": "9878"}` in the AI client's MCP configuration (`claude_desktop_config.json`, `.cursor/mcp.json`, etc.).
3. **If Connection Times Out (`CommandTimeout`)**:
   * **Cause (Modal Popup)**: Vulcan Desktop likely has a blocking modal dialog on screen (e.g., *"No design database is currently open"*). Advise the user to click OK or Cancel in Vulcan Desktop to release the Python main thread.

---

## 1. Rapid Mining Project Audit

When the user asks for general project health or an inventory of available assets:

1. **Verify Connection and Active Project**:
   * Call `vulcan_system` with `action="ping"`.
   * Call `vulcan_system` with `action="project_info"`.
2. **List Models, Triangulations, and Databases**:
   * Call `vulcan_block_model` with `action="list"`.
   * Call `vulcan_triangulation` with `action="list"`.
   * Call `vulcan_drillholes` with `action="list_dbs"`.
3. **Report a Concise Summary**: Detail the working directory, available `.bmf` block models, key `.00t` surfaces/solids, and `.dhd.isis` drillhole databases.

---

## 2. Block Model Analysis & Resource Estimation

To answer questions regarding volume, tonnage, grades, or cutoffs:

1. **Retrieve Model Metadata**:
   * Call `vulcan_block_model` with `action="info"`, specifying the `.bmf` filename.
   * Identify available variables (e.g., `CUT`, `DENS`, `AU`, `ROCK`).
2. **Compute Grade-Tonnage Statistics**:
   * Call `vulcan_block_model` with `action="stats"`, `variable="CUT"`, and cutoff if applicable (`cutoff=0.5`).
   * Report total volume, tonnage, arithmetic mean, volume-weighted mean, and material above cutoff.
3. **Point Coordinate Queries**:
   * Call `vulcan_block_model` with `action="query_xyz"`, specifying `model`, `x`, `y`, `z` to sample individual block grades and rock codes.

---

## 3. Drillhole Exploration & High-Grade Intercepts (Bilingual)

1. **Inspect Drillhole Database Schema**:
   * Call `vulcan_drillholes` with `action="schema"`, `db="database_name.dhd.isis"`.
   * Identify bilingual table mappings (`COLLARS` or `COLLARES`, `ASSAYS` or `LEYES`, `SURVEY` or `BUZAMIENTO`).
2. **Identify Mineralized Intercepts**:
   * Call `vulcan_drillholes` with `action="high_grade"`, `db="..."`, `table="ASSAYS"` (or `LEYES`), `field="CUT"`, `min_value=1.0`.
3. **3D Viewport Display**:
   * Call `vulcan_drillholes` with `action="display"`, `limit=10` (strictly limit objects $\le 300$ segments to keep Envisage rendering fluid).
   * Capture a 3D screenshot with `vulcan_screenshot` to confirm visual representation.

---

## 4. CAD Bench Design & 3D Visual Validation

1. **Inspect Design Layers**:
   * Call `vulcan_design` with `action="list_layers"` and `action="get_polygons"` to audit bench toes, crests, and haul roads.
2. **Calculate Planar Areas**:
   * Call `vulcan_design` with `action="polygon_area"` to determine surface area ($m^2$) and 2D centroids.
3. **Multimodal Visual Validation**:
   * Call `vulcan_screenshot` with `quality=90` to capture a full-resolution JPEG of the active Envisage 3D viewport, confirming camera orientation and digitized strings.

---

## 5. Safe Vulcan Python SDK Scripting & Hot-Reload

When executing custom automation code via `vulcan_execute_code`:

1. **Python 3.5.2 Compatibility**:
   * Never use f-strings or type annotations in scripts passed to Vulcan.
2. **Dynamic Handler Hot-Reload**:
   * Handlers in `vulcan_listener/handlers/` can be refreshed on the fly without restarting Vulcan:
     ```python
     import importlib
     import handlers.block_models

     importlib.reload(handlers.block_models)
     ```
3. **Graphics Context Protection**:
   * Execute scripts synchronously on Vulcan's main thread to preserve Envisage OpenGL stability.


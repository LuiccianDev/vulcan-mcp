---
name: vulcan-workflow
description: Guided mining workflows for interacting with Maptek Vulcan 12 Desktop via Vulcan MCP (project audits, block model estimation, drillholes, and 3D screenshots).
---

# Mining Workflows with Vulcan MCP

This skill provides step-by-step procedures to interact safely and efficiently with Maptek Vulcan 12 Desktop.

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

---

## 3. Drillhole Exploration & High-Grade Intercepts

1. **Inspect Drillhole Database Schema**:
   * Call `vulcan_drillholes` with `action="schema"`, `db="database_name.dhd.isis"`.
2. **Identify Mineralized Intercepts**:
   * Call `vulcan_drillholes` with `action="high_grade"`, `db="..."`, `table="ASSAYS"`, `field="CUT"`, `min_value=1.0`.
3. **3D Viewport Display**:
   * Call `vulcan_drillholes` with `action="display"`, `limit=10` (keeps rendering fluid and prevents freezing Envisage).
   * Capture a 3D screenshot with `vulcan_screenshot` to confirm the visual representation.

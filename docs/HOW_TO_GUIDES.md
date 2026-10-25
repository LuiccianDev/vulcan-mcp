# Vulcan MCP How-To Guides

> **Diátaxis Focus:** This section contains practical recipes designed to solve specific operational, geological, and mining engineering tasks using **Maptek Vulcan 12 Desktop**.

---

## Recipe Index

1. [How to audit a block model and calculate tonnage by cutoff](#1-how-to-audit-a-block-model-and-calculate-tonnage-by-cutoff)
2. [How to search high-grade intercepts and display them in 3D without freezing Envisage](#2-how-to-search-high-grade-intercepts-and-display-them-in-3d-without-freezing-envisage)
3. [How to validate topological consistency and sample elevations on 3D triangulations](#3-how-to-validate-topological-consistency-and-sample-elevations-on-3d-triangulations)
4. [How to calculate planar bench areas and create CAD polylines](#4-how-to-calculate-planar-bench-areas-and-create-cad-polylines)
5. [How to run Python scripts and hot-reload handlers inside Vulcan](#5-how-to-run-python-scripts-and-hot-reload-handlers-inside-vulcan)
6. [How to diagnose and resolve modal dialog freezes in Vulcan Desktop](#6-how-to-diagnose-and-resolve-modal-dialog-freezes-in-vulcan-desktop)

---

## 1. How to audit a block model and calculate tonnage by cutoff

### Problem
You need to quickly calculate estimated volume, tonnage, and volume-weighted mean grade for an element (e.g., Copper `CUT` or Gold `AU`) in a `.bmf` block model, applying a specified cutoff grade and rock density.

### Solution

#### Step 1: Inspect the block model schema
Identify the estimated variables and dimensions:

```text
"Show me the variables, dimensions, and origin of the block model deposit_model.bmf"
```

MCP Call:
```json
{
  "tool": "vulcan_block_model",
  "arguments": {
    "action": "info",
    "name": "deposit_model.bmf"
  }
}
```

#### Step 2: Run grade-tonnage estimation with cutoff
Specify the target variable, cutoff grade, and default density:

```text
"Calculate statistics for deposit_model.bmf for variable CUT with cutoff >= 0.50 and density of 2.7 t/m3"
```

MCP Call:
```json
{
  "tool": "vulcan_block_model",
  "arguments": {
    "action": "stats",
    "name": "deposit_model.bmf",
    "variable": "CUT",
    "cutoff": 0.5,
    "default_density": 2.7
  }
}
```

#### Expected Output:
```json
{
  "total_blocks": 250000,
  "blocks_above_cutoff": 48210,
  "total_volume": 3856800.0,
  "tonnage": 10413360.0,
  "mean_grade": 0.842,
  "variable": "CUT",
  "cutoff": 0.5
}
```

---

## 2. How to search high-grade intercepts and display them in 3D without freezing Envisage

### Problem
You have an ISIS drillhole database (`.dhd.isis`) and want to identify intervals with the highest mineral grades and visualize them in Envisage's 3D viewport without overloading the graphics thread.

> [!WARNING]
> **Graphics Performance Safeguard ($\le 300$ segments):**  
> To prevent freezing Envisage's OpenGL pipeline, always keep the `limit` parameter moderate ($\le 300$).

### Solution

#### Step 1: Find the top intercepts
```text
"Identify the 10 highest grade intervals in the ASSAYS table of exploration.dhd.isis"
```

MCP Call:
```json
{
  "tool": "vulcan_drillholes",
  "arguments": {
    "action": "high_grade",
    "name": "exploration.dhd.isis",
    "table": "ASSAYS",
    "field": "CU",
    "top_n": 10
  }
}
```

#### Step 2: Render drillhole segments colored by grade in 3D
```text
"Display the first 50 drillhole intervals in 3D in Envisage colored by copper grade"
```

MCP Call:
```json
{
  "tool": "vulcan_drillholes",
  "arguments": {
    "action": "display",
    "name": "exploration.dhd.isis",
    "legend": "copper_colors.scd",
    "limit": 50
  }
}
```

#### Step 3: Clear temporary objects from the viewport
Once visual inspection is complete:
```json
{
  "tool": "vulcan_drillholes",
  "arguments": {
    "action": "clear_display"
  }
}
```

---

## 3. How to validate topological consistency and sample elevations on 3D triangulations

### Problem
Before using a surface or solid `.00t` in volumetric estimations, you must confirm that it has no self-intersections or open holes, and sample the exact $Z$ elevation at specific design coordinates $(X, Y)$.

### Solution

#### Step 1: Topological solid audit
```text
"Check if final_pit.00t is a closed and consistent solid, and report its total volume"
```

MCP Call:
```json
{
  "tool": "vulcan_triangulation",
  "arguments": {
    "action": "info",
    "name": "final_pit.00t"
  }
}
```

Sample Response:
```json
{
  "name": "final_pit.00t",
  "nodes": 12450,
  "faces": 24896,
  "is_solid": true,
  "is_consistent": true,
  "volume": 15420380.25,
  "surface_area": 845210.12,
  "centroid": [475200.0, 4480100.0, 2410.5]
}
```

#### Step 2: Query Z elevation at specific coordinates
```text
"What is the Z elevation of topo.00t at coordinates X=474500, Y=4479900?"
```

MCP Call:
```json
{
  "tool": "vulcan_triangulation",
  "arguments": {
    "action": "elevation",
    "name": "topo.00t",
    "x": 474500.0,
    "y": 4479900.0
  }
}
```

---

## 4. How to calculate planar bench areas and create CAD polylines

### Problem
You need to verify the horizontal planar area in $m^2$ of a blast pattern or mine bench outline in a `.dgd.isis` CAD layer, or digitize a new boundary polygon.

### Solution

#### Step 1: Inspect layer and calculate polygon area
```text
"Calculate the planar area in m² and centroid of the objects in layer BENCH_2400 in mine_design.dgd.isis"
```

MCP Call:
```json
{
  "tool": "vulcan_design",
  "arguments": {
    "action": "layer_info",
    "db": "mine_design.dgd.isis",
    "layer": "BENCH_2400"
  }
}
```

Response:
```json
{
  "layer": "BENCH_2400",
  "objects": 1,
  "type": "polygon",
  "area_m2": 45210.85,
  "perimeter_m": 894.20,
  "centroid": [474850.1, 4480020.4, 2400.0]
}
```

#### Step 2: Create a new CAD polyline
```json
{
  "tool": "vulcan_design",
  "arguments": {
    "action": "create_polyline",
    "db": "mine_design.dgd.isis",
    "layer": "BLAST_POLYGONS",
    "points": [
      [474800.0, 4480000.0, 2400.0],
      [474850.0, 4480000.0, 2400.0],
      [474850.0, 4480050.0, 2400.0],
      [474800.0, 4480000.0, 2400.0]
    ],
    "colour": "red"
  }
}
```

---

## 5. How to run Python scripts and hot-reload handlers inside Vulcan

### Problem
You want to test custom `maptek.vulcan` routines or modify the Python modules in `plugin/handlers/` without restarting Vulcan Desktop or the socket listener.

### Solution

#### Step 1: Execute dynamic Python code with `vulcan_execute_code`
```text
"Run a script inside Vulcan that reports the Envisage API version in the report console"
```

MCP Call:
```json
{
  "tool": "vulcan_execute_code",
  "arguments": {
    "code": "import maptek.vulcan as v\nprint('Vulcan API Version:', getattr(v, '__version__', '12.0'))\nresult = {'api_ready': True}"
  }
}
```

#### Step 2: Hot-reload a modified handler module
If you modified `plugin/handlers/block_models.py` in your code editor:
```json
{
  "tool": "vulcan_execute_code",
  "arguments": {
    "code": "import importlib\nimport handlers.block_models\nimportlib.reload(handlers.block_models)\nresult = 'block_models module reloaded successfully'"
  }
}
```

---

## 6. How to diagnose and resolve modal dialog freezes in Vulcan Desktop

### Problem
An MCP tool call sent by your AI client hangs until it hits a **Timeout** (30s or 120s), or the TCP socket does not reply.

### Cause
Maptek Vulcan 12 Desktop uses native Windows MFC dialogs. When an operation triggers a modal dialog popup (e.g. overwrite confirmation, color palette prompt, or file save prompt), **Vulcan's main Python execution thread is completely suspended** until a human clicks OK or Cancel.

### Step-by-Step Resolution:
1. **Look at the Vulcan screen:** Check whether Vulcan/Envisage has a dialog popup open.
2. **Click OK / Cancel:** Once the modal is dismissed, the Python thread resumes instantly.
3. **Retry the command:** Ask your AI assistant to retry the command. It will execute normally.

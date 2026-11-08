---
name: vulcan-file-formats
description: Concise technical reference for Maptek Vulcan file formats (.bmf, .00t, .dgd.isis, .dhd.isis, .scd, .grid) and which MCP tools operate on each.
---

# Maptek Vulcan File Formats

Quick reference guide based on official **Maptek Vulcan Help** documentation to identify and interact with all mining project file types.

---

## 1. Quick Extension & MCP Tool Mapping

| Extension | Official Name | Primary Content | MCP Tool |
| :--- | :--- | :--- | :--- |
| **`.bmf`** | Block Model File | 3D block model (regular or sub-blocked), grades, density, lithology, economics. | `vulcan_block_model` |
| **`.00t`** (`.tri`, `.sft`, `.srt`) | Triangulation | 3D surfaces (topography, faults) and closed solids (orebodies, stopes, pits). | `vulcan_triangulation` |
| **`.dgd.isis`** | Design Database | 3D CAD spatial database: layers, polylines, polygons, points, annotations. | `vulcan_design` |
| **`.dhd.isis`** | Drillhole ISIS DB | Relational ISIS drilling database: collars, surveys, assays, lithology intervals. | `vulcan_drillholes` |
| **`.scd`** | Scheme / Legend File | Envisage color schemes and legends (grade ranges, rock code colors). | `vulcan_legend` |
| **`.dgd.isix` / `.dhd.isix`** | ISIS Index File | Binary fast-access index for `.isis` databases. **Do not delete or edit manually.** | *(Internal SDK)* |
| **`.wrk`** | Work File | Temporary recovery file generated during interactive Envisage sessions. | *(Internal Vulcan)* |
| **`.grid` / `.sfg`** | Grid Surface | 2D/2.5D regular grid surfaces for structural or elevation modeling. | `vulcan_execute_code` (`v.grid`) |

---

## 2. Rules by File Type

### Block Models (`.bmf`)
* Defined by geometric extents (origin $X_0, Y_0, Z_0$, orientation/rotation, and schema block sizes) and block attributes.
* Variables can be **numeric** (`float`/`double`, e.g., `CUT`, `DENS`, `AU`) or **alphanumeric** (`string`, e.g., `ROCK`, `ZONE`).
* Open in read mode (`"r"`) for audits or resource queries (`action="info"`, `action="query_xyz"`, `action="stats"`).

### Triangulations (`.00t`)
* Composed of **nodes** (3D vertices $[X, Y, Z]$) and **faces** (triangle index triplets $[i_1, i_2, i_3]$).
* **Open surface (`closed: false`)**: Topography (`topo*.00t`), water table, or fault plane. Ideal for sampling $Z$ elevations (`action="elevation"`).
* **Closed solid (`closed: true`)**: Orebody, pit shell, or underground stope. Enables volume estimation (`action="info"` -> `volume`).

### CAD Design Databases (`.dgd.isis`)
* Organized into **Layers**, each grouping 3D vector objects (`polyline`).
* Typical layers like `ASSAYS` or `TOPO` contain 3D polylines with names, Vulcan palette colors, and vertex coordinates.
* Use `action="list_layers"` prior to loading (`load_layer`) or inspecting (`layer_info`).

### ISIS Drillhole Databases (`.dhd.isis`)
* Hierarchical structure indexed by drillhole key (`Key` = `HOLE_ID`).
* Typical tables in mining projects (supports bilingual schemas):
  * **Collars**: `COLLARS` / `COLLARES` / `LOCATION` ($X, Y, Z$, total depth).
  * **Surveys**: `SURVEY` / `DIRECCIONES` (`FROM`/`DEPTH`, `AZIMUTH`, `DIP`/`BUZ`).
  * **Assays**: `ASSAYS` / `LEYES` (`FROM`, `TO`, `CUT`, `AU`, `AG`).
  * **Geology**: `LITHOLOGY` / `LITOLOGIA` (`FROM`, `TO`, `RX`, `ALT`).

### Legends and Color Schemes (`.scd`)
* Plain text files structured into scheme blocks (e.g., `DRILL_COLOUR`, `BLOCK_COLOUR`).
* When updating a legend with `vulcan_legend` (`action="update"`), a backup `.scd.bak` is automatically created and can be restored via `action="restore"`.

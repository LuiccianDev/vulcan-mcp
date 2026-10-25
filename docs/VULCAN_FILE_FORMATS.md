# Official Maptek Vulcan File Formats

Technical reference based on **Maptek Vulcan Help** for the file types comprising a geological and mine planning project in Maptek Vulcan Desktop.

---

## Extension Summary Table

| Extension | Official Name | Description | MCP Tool |
| :--- | :--- | :--- | :--- |
| **`.bmf`** | Block Model File | 3D block model (regular or sub-blocked), grades, density, and lithology. | `vulcan_block_model` |
| **`.00t`** (`.tri`, `.sft`, `.srt`) | Triangulation | 3D triangulated meshes: open surfaces (topography, faults) and closed solids. | `vulcan_triangulation` |
| **`.dgd.isis`** | Design Database | 3D CAD spatial database (layers, polylines, polygons, points, and annotations). | `vulcan_design` |
| **`.dhd.isis`** | Drillhole ISIS DB | Relational ISIS drilling database (collars, deviations, assays, lithology). | `vulcan_drillholes` |
| **`.scd`** | Scheme / Legend File | Envisage color schemes and legends (`BLOCK_COLOUR`, `DRILL_COLOUR`). | `vulcan_legend` |
| **`.dsf`** | Design Specification | Design specifications and ISIS database dictionaries. | `vulcan_system` (`project_info`) |
| **`.dgd.isix` / `.dhd.isix`** | ISIS Index File | Binary fast-access indexes for `.isis` databases. **Do not edit manually.** | *(Internal SDK)* |
| **`.wrk`** | Work File | Temporary recovery file generated during interactive Envisage sessions. | *(Internal Vulcan)* |
| **`.grid` / `.sfg`** | Grid Surface | 2D/2.5D regular grid surface for structural or elevation modeling. | `vulcan_execute_code` (`v.grid`) |

---

## 1. Block Models (`.bmf`)
* **Description**: Maptek Vulcan's native binary block model format (*Block Model File*) used for resource estimation, reserve modeling, and mine design.
* **Internal Structure**:
  * **Geometry**: Origin $(X_0, Y_0, Z_0)$, 3D rotation angles, and schemas (`model_n_schemas()`, schema sizes `model_schema_size(k)`, and extents `model_schema_extent(k)`).
  * **Variables**: Stores attributes per block, either numeric (`float`/`double` such as `CUT`, `AU`, `DENS`, `TONS`, with null defaults e.g. `-99.0`) or string (`ROCK`, `DOMAIN`).
* **Implicit Coordinate Variables**:
  * `xworld`, `yworld`, `zworld`: Block centroid in world coordinates.
  * `xlength`, `ylength`, `zlength`: Block dimensions $(dx, dy, dz)$.
* **MCP Tool**: `vulcan_block_model` (`list`, `info`, `query_xyz`, `stats`).

---

## 2. 3D Triangulations (`.00t`, `.tri`, `.sft`, `.srt`)
* **Description**: Standard 3D triangulated mesh format in Vulcan.
  * ⚠️ **Note on `.tri/` directories**: In Vulcan projects, directories named `P1.tri/` or `PitOptimizer.tri/` are common. `Vulcan MCP` automatically filters out directories via `os.path.isfile()` to inventory only valid triangulation files.
* **Structure**:
  * Indexed list of **nodes** (3D vertices $[X, Y, Z]$) and **faces** (triangular facets $[n_1, n_2, n_3]$).
  * **Open surfaces (`closed = False`)**: Topographies (`topography_1.00t`), fault planes, or lithological horizons. Ideal for elevation queries with `elevation`.
  * **Closed solids (`closed = True`)**: Orebodies, underground stopes, tunnels, or pit phases. Enable volume computation ($m^3$) and `point_inside` tests.
* **Topological Quality Validation**:
  * `consistent` (`is_consistent()`): Coherently oriented face normals.
  * `crossing` (`is_crossing()`): Detects self-intersecting triangles (`False` in clean meshes).
  * `ok` (`is_ok()`): Overall mesh validity status.
* **MCP Tool**: `vulcan_triangulation` (`list`, `info`, `elevation`, `point_inside`, `load`, `unload`).

---

## 3. CAD Design Databases (`.dgd.isis`)
* **Description**: 3D spatial CAD drawing database (introduced in Vulcan 7.0+ on top of the ISIS engine).
* **Internal Structure**:
  * Contains **Layers** identified by name (e.g., `TOPO`, `BENCH_100`, `LIMITS`). Internal system layers with `DIG$` prefixes are automatically filtered out.
  * Each layer stores geometric objects (`polyline`), with 3D coordinates, Vulcan palette color, 3D length (`length`), planar area (`planar_area`), and centroid (`centroid`).
* **MCP Tool**: `vulcan_design` (`list_dbs`, `list_layers`, `layer_info`, `load_layer`, `clear_temp`, `create_polyline`).

---

## 4. ISIS Drillhole Databases (`.dhd.isis`)
* **Description**: Vulcan's hierarchical relational database used for exploration drilling and blast hole logging.
* **Internal Structure**:
  * Keyed by primary drillhole ID (`Key` = e.g., `DH001`, `RC104`).
  * **Standard Tables and Fields (Bilingual Support: English / Spanish)**:

| Table | Recognized Table Names | Recognized Field Names |
| :--- | :--- | :--- |
| **Collars** | `COLLARS`, `COLLARES`, `COLLAR`, `LOCATION` | `HOLE_ID`, `X`/`EAST`/`ESTE`, `Y`/`NORTH`/`NORTE`, `Z`/`RL`/`COTA`, `LENGTH`/`LENGHT` |
| **Surveys** | `SURVEY`, `SURVEYS`, `DIRECCIONES`, `DEVIATION` | `FROM`/`DESDE`/`DEPTH`/`PROF`/`AT`, `AZIMUTH`/`AZIMUT`/`BRG`, `DIP`/`BUZ`/`BUZAMIENTO`/`INCL` |
| **Assays** | `ASSAY`, `ASSAYS`, `LEYES` | `FROM`/`DESDE`, `TO`/`HASTA`, `CUT`, `CU`, `AU`, `AG`, `GRADE`, `LEY` |
| **Lithology** | `LITHOLOGY`, `LITOLOGIA` | `FROM`, `TO`, `RX`, `SIMPL`, `ALT` |

* **MCP Tool**: `vulcan_drillholes` (`list_dbs`, `schema`, `holes`, `hole`, `high_grade`, `display`, `clear_display`).

---

## 5. Color Schemes & Legends (`.scd`)
* **Description**: Specification files in `latin1` encoding defining color legends in Envisage.
* **Syntax Structure**:
  ```text
  BEGIN$DEF DRILL_COLOUR
   BEGIN$TAB COPPER
     'CUT'
     '#ASSAYS'
     'FROM'
     'TO'
     ''
     '144'    <-- Vulcan color index
     '0.0'    <-- FROM
     '0.5'    <-- TO
     'GELT'   <-- Comparison rule (Greater or Equal, Less Than)
   END$TAB COPPER
  END$DEF DRILL_COLOUR
  ```
* **Standard Vulcan Display Color Indices**:
  * `1`: Red (High grade $\ge 1.0\%$)
  * `2`: Green (Low grade $0.2\% - 0.5\%$)
  * `3` / `45`: Yellow (Medium grade $0.5\% - 0.8\%$)
  * `4`: Orange (Medium-high grade $0.8\% - 1.0\%$)
  * `5` / `144`: Blue / Cyan (Waste / trace $< 0.2\%$)
  * `6`: Magenta
* **MCP Tool**: `vulcan_legend` (`list`, `inspect`, `update`, `restore`).

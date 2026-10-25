---
name: vulcan-python-sdk
description: Technical reference and practical recipes for Maptek Vulcan Python SDK (maptek.vulcan, maptek.vulcan_gui) and Maptek Python SDK 2.0 (mapteksdk) for scripting with vulcan_execute_code.
---

# Maptek Vulcan Python SDK & Maptek SDK 2.0

Use this skill when authoring or executing custom Python scripts via `vulcan_execute_code` or when using advanced Maptek SDK routines.

---

## 1. Execution Environment in `vulcan_execute_code`

When calling `vulcan_execute_code`, the listener executes within **Python 3.5.2 embedded in Maptek Vulcan 12**:
* **Syntax Restrictions**: Do NOT use *f-strings* (`f"{x}"`) or variable type annotations in code passed to `vulcan_execute_code`. Use `.format()`.
* **Pre-injected Variables**:
  * `vulcan`: `maptek.vulcan` module
  * `vulcan_gui`: `maptek.vulcan_gui` module
  * `project_dir`: absolute path of active working directory
  * Assign any JSON-serializable dictionary or value to the `result` variable to return data back to the client.

---

## 2. Vulcan Native API (`maptek.vulcan`)

### A. Block Models (`vulcan.block_model`)
* **Open & Close**: `bm = vulcan.block_model(path, "r")` (always close with `bm.close()`).
* **Metadata & Schema**:
  * `bm.n_blocks()`: total blocks.
  * `bm.model_origin()`, `bm.model_orientation()`, `bm.model_extent()`.
  * `bm.field_list()`, `bm.field_list_numbers()`, `bm.field_list_strings()`.
* **Search & Cursor Positioning**:
  * `bm.find_world_xyz(x, y, z)` / `bm.find_xyz(x, y, z)`: position cursor at block containing coordinates.
  * `bm.select(expr)`: filter blocks by logical or spatial criteria; iterate with `bm.rewind()`, `bm.eof()`, `bm.next()`.
* **Data Access & Statistics**:
  * `bm.get(var)` / `bm.get_string(var)`: value in active block.
  * `bm.get_multiple(vars_list)`: read multiple numeric variables in a single call.
  * `bm.match_volume()`: volume of active block ($m^3$).
  * `bm.get_pandas()` / `bm.get_pandas_extent(...)`: export block attributes to DataFrame if pandas is available.

### B. Triangulations (`vulcan.triangulation`)
* **Open**: `tri = vulcan.triangulation(path)` (loads into memory; **Note**: Do NOT call `tri.close()` when reading, as `tri.close()` is a geometric mesh stitching operation requiring write mode `"w"`).
* **Geometric Queries**:
  * `tri.n_nodes()`, `tri.n_faces()`, `tri.extent()`, `tri.centroid()`.
  * `tri.is_closed()`, `tri.is_consistent()`, `tri.is_crossing()`, `tri.is_ok()`.
  * `tri.volume()`: enclosed volume for closed solids.
  * `tri.get_elevation(x, y)` / `tri.get_elevations(pts)`: interpolate $Z$ elevation at $(X, Y)$.
  * `tri.point_inside(x, y, z)`: test if 3D point is inside solid.
  * `tri.segment_intersections(p1, p2)`: compute intersections between a 3D line segment (e.g., drillhole trace) and mesh.
* **Editing**: `tri.add_node(x, y, z)`, `tri.add_face(i1, i2, i3)`, `tri.save(path)`.

### C. ISIS Databases & Drillholes (`vulcan.isisdb`)
* **Open**: `db = vulcan.isisdb(path, "r", "")` (always close with `db.close()`).
* **Schema**: `db.table_list()`, `db.field_list(table)`, `db.field_list_numbers(table)`, `db.field_list_strings(table)`, `db.key_list()`.
* **Drillhole Navigation**:
  * `db.find_key(hole_id)`: jump to first record of specified drillhole.
  * `db.next_same_key()` / `db.next()`: advance records within same hole or sequentially.
  * `db.get_table_name()`, `db.get_key()`, `db.get(field)`, `db.get_string(field)`.

### D. 3D CAD Design (`vulcan.dgd`, `vulcan.layer`, `vulcan.polyline`)
* **DGD Database**: `dgd = vulcan.dgd(path, "r")` or `"w"`. Methods: `dgd.list_layers()`, `dgd.is_layer(name)`, `dgd.get_layer(name)`, `dgd.append(layer)`, `dgd.save_layer(layer)`, `dgd.close()`.
* **Layer (`vulcan.layer`)**: `lyr = vulcan.layer(name)`. Methods: `lyr.num_objects()`, `lyr.get_object(i)`, `lyr.append(poly)`.
* **Polyline (`vulcan.polyline`)**:
  * Geometry: `poly.get_coordinates()`, `poly.set_coordinates(pts)`, `poly.num_points()`, `poly.length()`, `poly.planar_area()`, `poly.centroid()`, `poly.point_inside(pt)`.
  * Styling & attributes: `poly.set_name(s)`, `poly.set_colour(c)`, `poly.set_closed(bool)`, `poly.set_connected()`.

---

## 3. Envisage Graphics Interface (`maptek.vulcan_gui`)

* **3D Triangulations**: `vg.load_triangulation(path)`, `vg.remove_triangulations([path])`, `vg.reload_triangulation(path)`.
* **3D CAD Layers**: `vg.add_layer(layer_obj)`.
* **Temporary Objects**: `tobj = vg.temp_object(poly_obj)` (retain in memory to prevent SWIG garbage collection; remove with `tobj.remove()`).
* **Window & Macros**: `vg.macro(cmd)`, `vg.workbench_macro(cmd)`, `vg.get_report_window()`, `vg.set_view(...)`.

---

## 4. Maptek Python SDK 2.0 Mapping (`mapteksdk`)

In external workflows using **Maptek Python SDK 2.0** (`mapteksdk` on Maptek Workbench):

| Mining Concept | Vulcan Embedded SDK (`maptek.vulcan`) | Maptek Python SDK 2.0 (`mapteksdk`) |
| :--- | :--- | :--- |
| Project connection | `os.getcwd()` in Envisage session | `from mapteksdk.project import Project` |
| 3D Surface / Mesh | `vulcan.triangulation("m.00t")` | `mapteksdk.data.Surface` (`.points`, `.facets`) |
| Topographic Grid | `vulcan.grid("g.grid")` | `mapteksdk.data.GridSurface` |
| Point Cloud / 3D Points | `vulcan.polyline` / `point_list` | `mapteksdk.data.PointSet` (`.dataframe()`) |
| Block Model | `vulcan.block_model("b.bmf")` | `DenseBlockModel` / `SubblockedBlockModel` |

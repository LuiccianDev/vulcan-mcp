# Technical Reference: Maptek Vulcan Python SDK & Maptek SDK 2.0

Consolidated technical documentation derived from **Maptek Python SDK Help** and direct introspection of `maptek.vulcan` and `maptek.vulcan_gui` inside **Maptek Vulcan 12 Desktop**.

---

## 1. Architecture: The Two Maptek SDKs

| Feature | `maptek.vulcan` / `maptek.vulcan_gui` | `mapteksdk` (SDK 2.0) |
| :--- | :--- | :--- |
| **Environment** | Embedded inside Maptek Vulcan Desktop (Python 3.5.2 in Vulcan 12) | Modern external package for Maptek Workbench / PointStudio / GeologyCore |
| **Technology** | C++ bindings generated with SWIG | Native object-oriented Python API with NumPy and Pandas integration |
| **Usage in Vulcan MCP** | Direct in socket listener and via `vulcan_execute_code` | For interoperability pipelines across Maptek Workbench platforms |

---

## 2. `maptek.vulcan` Class & Method Catalog

### 2.1 `vulcan.block_model` (`.bmf` Files)
Reads, filters, queries, and updates block models headlessly.

* **Open & Close**:
  * `bm = vulcan.block_model("model.bmf", "r")` (`"r"` read, `"w"` write)
  * `bm.close()`, `bm.is_open()`
* **Geometry & Schema**:
  * `bm.n_blocks()`: Total number of blocks.
  * `bm.model_origin()`, `bm.model_orientation()`, `bm.model_extent()`, `bm.block_extent()`.
  * `bm.model_n_schemas()`, `bm.model_schema_extent(i)`, `bm.model_schema_size(i)`, `bm.model_schema_dimensions(i)`.
  * `bm.to_world(x, y, z)`, `bm.to_model(x, y, z)`: Coordinate transform between world and local model coordinates.
* **Variables (Fields)**:
  * `bm.field_list()`: List all variables in the model.
  * `bm.field_list_numbers()`, `bm.field_list_strings()`: Filter numeric or text variables.
  * `bm.is_field(name)`, `bm.is_number(name)`, `bm.is_string(name)`, `bm.field_type(name)`, `bm.field_default(name)`.
* **Search, Selection & Iteration**:
  * `bm.find_world_xyz(x, y, z)` / `bm.find_xyz(x, y, z)`: Find the block enclosing the coordinates.
  * `bm.select(criteria)`: Apply a block selection condition.
  * `bm.rewind()`, `bm.next()`, `bm.eof()`: Sequential block iteration.
* **Data Access & Statistics**:
  * `bm.get(var)` / `bm.get_string(var)`: Read numeric or string value of the active block.
  * `bm.get_multiple(var_list)` / `bm.get_multiple_string(var_list)`: Fast vectorized read.
  * `bm.match_volume()`: Volume ($m^3$) of the active block.
  * `bm.get_pandas()` / `bm.get_pandas_extent(...)`: Extract variables directly as a DataFrame.
  * `bm.put(var, val)`, `bm.put_string(var, val)`, `bm.write()`: Write in `"w"` mode.

```python
# Quick example in vulcan_execute_code
bm = vulcan.block_model("eblock.bmf", "r")
try:
    bm.find_world_xyz(795500.0, 9125000.0, 3400.0)
    result = {"cut": bm.get("CUT"), "volume": bm.match_volume()}
finally:
    bm.close()
```

---

### 2.2 `vulcan.triangulation` (`.00t` Files)
Manipulates topographic surfaces and closed 3D solids.

* **Open & Save**:
  * `tri = vulcan.triangulation("surface.00t")` (read mode) or `vulcan.triangulation("surface.00t", "w")` (edit mode).
  * `tri.save("output.00t")`
  * ⚠️ **Important Note on `tri.close()`**: Unlike `bm.close()` or `db.close()`, in `vulcan.triangulation` the `tri.close()` method is a **geometric operation** that stitches open boundaries into a closed solid (requires write mode `"w"`). Do NOT call it to close read-only files.
* **Topology & Validation**:
  * `tri.n_nodes()`, `tri.n_faces()`: Node and triangle counts.
  * `tri.is_closed()`, `tri.is_consistent()`, `tri.is_crossing()`, `tri.is_ok()`.
  * `tri.volume()`: Solid volume (requires closed, consistent mesh).
  * `tri.extent()`, `tri.centroid()`.
* **Spatial Queries**:
  * `tri.get_elevation(x, y)` / `tri.get_elevations(points_xy)`: Sample projected $Z$ elevation.
  * `tri.point_inside(x, y, z)`: `True` if point $(x, y, z)$ is enclosed inside the solid.
  * `tri.segment_intersections(p1, p2)`: Intersection points between segment $[p_1, p_2]$ and triangulation.
* **Geometry Modification**:
  * `tri.get_node(i)`, `tri.get_face(i)`, `tri.get_vertices()`, `tri.get_faces()`.
  * `tri.add_node(x, y, z)`, `tri.add_face(n1, n2, n3)`, `tri.colour`, `tri.set_colour(c)`, `tri.set_rgb(r, g, b)`.

---

### 2.3 `vulcan.isisdb` (`.dhd.isis` Databases)
Low-level relational access to ISIS drilling databases (collars, surveys, assays, lithology).

* **Open**:
  * `db = vulcan.isisdb("mine_drilling.dhd.isis", "r", "")`
  * `db.close()`, `db.is_open()`
* **Metadata**:
  * `db.table_list()`: Available tables (e.g., `['COLLARS', 'SURVEY', 'LITHOLOGY', 'ASSAYS']` or Spanish equivalents `['COLLARES', 'DIRECCIONES', 'LEYES']`).
  * `db.field_list(table)`, `db.field_list_numbers(table)`, `db.field_list_strings(table)`.
  * `db.key_list()`: List all `HOLE_ID` values (primary keys).
* **Navigation & Queries**:
  * `db.find_key(hole_id)`: Position cursor at first record of specified drillhole.
  * `db.next_same_key()`: Advance to next record of same drillhole.
  * `db.goto_table(table_name)`: Jump to specific table.
  * `db.rewind()`, `db.next()`, `db.eof()`.
  * `db.get_key()`, `db.get_table_name()`, `db.get(field)`, `db.get_string(field)`.

---

### 2.4 `vulcan.dgd`, `vulcan.layer` & `vulcan.polyline` (`.dgd.isis` CAD)

* **`vulcan.dgd`**:
  * `dgd = vulcan.dgd("mine_design.dgd.isis", "r")` (or `"w"`, `"create"`).
  * `dgd.list_layers()`, `dgd.num_layers()`, `dgd.is_layer(name)`.
  * `dgd.get_layer(name)`, `dgd.append(layer)`, `dgd.save_layer(layer)`, `dgd.delete_layer(name)`, `dgd.close()`.
* **`vulcan.layer`**:
  * `lyr = vulcan.layer("NEW_LAYER")`
  * `lyr.num_objects()`, `lyr.get_object(i)`, `lyr.append(obj)`, `lyr.clear_objects()`, `lyr.get_description()`, `lyr.set_description(desc)`.
* **`vulcan.polyline`**:
  * `poly = vulcan.polyline()`
  * `poly.set_coordinates([[x1, y1, z1], [x2, y2, z2]])`, `poly.get_coordinates()`, `poly.num_points()`.
  * `poly.set_connected()`, `poly.set_closed(True)`, `poly.is_closed()`.
  * `poly.length()`, `poly.planar_area()`, `poly.centroid()`, `poly.point_inside([x, y, z])`.
  * `poly.set_name(name)`, `poly.get_name()`, `poly.set_colour(idx)`, `poly.get_colour()`.

---

## 3. `maptek.vulcan_gui` Catalog (Envisage 3D Viewport Control)

* **Triangulation Display**:
  * `vulcan_gui.load_triangulation(path)` / `vulcan_gui.load_triangulations([paths])`
  * `vulcan_gui.remove_triangulations([paths])`
  * `vulcan_gui.reload_triangulation(path)`
* **Layers & Temporary 3D Objects**:
  * `vulcan_gui.add_layer(layer)`
  * `tobj = vulcan_gui.temp_object(polyline)` (renders temporary 3D geometry in viewport without modifying DGD files).
* **Interaction & Commands**:
  * `vulcan_gui.macro(command_name)` / `vulcan_gui.workbench_macro(cmd)`
  * `vulcan_gui.get_report_window()`
  * `vulcan_gui.set_view(...)`, `vulcan_gui.set_window(...)`
  * `vulcan_gui.selection("Prompt")`, `vulcan_gui.pick_point("Prompt")`, `vulcan_gui.pick_triangulation("Prompt")` *(Note: `pick_*` methods await physical user screen clicks; avoid in unattended automated scripts)*.

---

## 4. Maptek Python SDK 2.0 Summary (`mapteksdk`)

In modern Maptek Workbench environments (`mapteksdk 2.0`), spatial entities are managed via typed data containers in `mapteksdk.data`:

1. **`PointSet`**: 3D point cloud `[X, Y, Z]` supporting `.dataframe()` (direct Pandas integration for `R, G, B, A`, selection, and visibility attributes).
2. **`Surface`**: Triangulated mesh defined by vertex arrays (`surface.points`) and triangular facet indices (`surface.facets = [[0, 1, 2], ...]`).
3. **`GridSurface`**: 2.5D regular grid structured in rows and columns with elevations and cell attributes.
4. **`DenseBlockModel` / `SubblockedBlockModel`**: High-performance regular and sub-blocked model representations within `mapteksdk.data`.

---
name: vulcan-python-sdk
description: Referencia oficial y recetas practicas del SDK de Python de Maptek Vulcan (maptek.vulcan, maptek.vulcan_gui) y Maptek Python SDK 2.0 (mapteksdk) para scripting con vulcan_execute_code.
---

# Maptek Vulcan Python SDK & Maptek SDK 2.0

Usa esta skill cuando necesites escribir o ejecutar scripts personalizados mediante `vulcan_execute_code` o cuando requieras métodos avanzados del SDK de Maptek.

---

## 1. Entorno de Ejecución en `vulcan_execute_code`

Al invocar `vulcan_execute_code`, el listener ejecuta sobre **Python 3.5.2 embebido en Maptek Vulcan 12**:
* **Restricción de sintaxis**: No usar *f-strings* (`f"{x}"`) ni anotaciones de tipos en variables dentro del código enviado a `vulcan_execute_code`. Usa `.format()`.
* **Variables pre-inyectadas**:
  * `vulcan`: módulo `maptek.vulcan`
  * `vulcan_gui`: módulo `maptek.vulcan_gui`
  * `project_dir`: ruta absoluta de la carpeta de trabajo activa
  * Asigna cualquier diccionario o valor serializable a la variable `result` para recibirlo de vuelta en JSON.

---

## 2. API Nativa de Vulcan (`maptek.vulcan`)

### A. Modelos de Bloques (`vulcan.block_model`)
* **Apertura**: `bm = vulcan.block_model(path, "r")` (siempre cerrar con `bm.close()`).
* **Metadatos y Esquema**:
  * `bm.n_blocks()`: total de bloques.
  * `bm.model_origin()`, `bm.model_orientation()`, `bm.model_extent()`.
  * `bm.field_list()`, `bm.field_list_numbers()`, `bm.field_list_strings()`.
* **Búsqueda y Posicionamiento**:
  * `bm.find_world_xyz(x, y, z)` / `bm.find_xyz(x, y, z)`: posiciona el cursor en el bloque que contiene la coordenada.
  * `bm.select(expr)`: filtra bloques según condición lógica o espacial; iterar con `bm.rewind()`, `bm.eof()`, `bm.next()`.
* **Lectura/Escritura de Variables**:
  * `bm.get(var)` / `bm.get_string(var)`: valor en el bloque actual.
  * `bm.get_multiple(vars_list)`: lee múltiples variables numéricas de una sola llamada.
  * `bm.match_volume()`: volumen del bloque actual ($m^3$).
  * `bm.get_pandas()` / `bm.get_pandas_extent(...)`: exporta datos de bloques a DataFrame si pandas está disponible.

### B. Triangulaciones (`vulcan.triangulation`)
* **Apertura**: `tri = vulcan.triangulation(path)` (carga en memoria; **Nota**: NO llamar a `tri.close()` al leer, ya que `tri.close()` es una operación geométrica para cerrar huecos de la malla y exige modo escritura `"w"`).
* **Consultas Geométricas**:
  * `tri.n_nodes()`, `tri.n_faces()`, `tri.extent()`, `tri.centroid()`.
  * `tri.is_closed()`, `tri.is_consistent()`, `tri.is_crossing()`, `tri.is_ok()`.
  * `tri.volume()`: volumen encerrado si es un sólido cerrado.
  * `tri.get_elevation(x, y)` / `tri.get_elevations(pts)`: interpola cota $Z$ en $(X, Y)$.
  * `tri.point_inside(x, y, z)`: verifica si un punto 3D está dentro del sólido.
  * `tri.segment_intersections(p1, p2)`: calcula intersecciones de un segmento 3D (ej. un sondaje) con la malla.
* **Edición**: `tri.add_node(x, y, z)`, `tri.add_face(i1, i2, i3)`, `tri.save(path)`.

### C. Bases de Datos ISIS / Sondajes (`vulcan.isisdb`)
* **Apertura**: `db = vulcan.isisdb(path, "r", "")` (cerrar siempre con `db.close()`).
* **Esquema**: `db.table_list()`, `db.field_list(table)`, `db.field_list_numbers(table)`, `db.field_list_strings(table)`, `db.key_list()`.
* **Navegación por Taladro**:
  * `db.find_key(hole_id)`: salta al primer registro del taladro.
  * `db.next_same_key()` / `db.next()`: avanza de registro manteniendo la clave o secuencialmente.
  * `db.get_table_name()`, `db.get_key()`, `db.get(field)`, `db.get_string(field)`.

### D. Diseño CAD 3D (`vulcan.dgd`, `vulcan.layer`, `vulcan.polyline`)
* **Base DGD**: `dgd = vulcan.dgd(path, "r")` o `"w"`. Métodos: `dgd.list_layers()`, `dgd.is_layer(name)`, `dgd.get_layer(name)`, `dgd.append(layer)`, `dgd.save_layer(layer)`, `dgd.close()`.
* **Capa (`vulcan.layer`)**: `lyr = vulcan.layer(name)`. Métodos: `lyr.num_objects()`, `lyr.get_object(i)`, `lyr.append(poly)`.
* **Polilínea (`vulcan.polyline`)**:
  * Geometría: `poly.get_coordinates()`, `poly.set_coordinates(pts)`, `poly.num_points()`, `poly.length()`, `poly.planar_area()`, `poly.centroid()`, `poly.point_inside(pt)`.
  * Estilo y metadatos: `poly.set_name(s)`, `poly.set_colour(c)`, `poly.set_closed(bool)`, `poly.set_connected()`.

---

## 3. Interfaz Gráfica Envisage (`maptek.vulcan_gui`)

* **Triangulaciones en 3D**: `vg.load_triangulation(path)`, `vg.remove_triangulations([path])`, `vg.reload_triangulation(path)`.
* **Capas CAD en 3D**: `vg.add_layer(layer_obj)`.
* **Objetos Temporales**: `tobj = vg.temp_object(poly_obj)` (mantener referencia en memoria para evitar recolección de basura de SWIG; quitar con `tobj.remove()`).
* **Ventana y Macros**: `vg.macro(cmd)`, `vg.workbench_macro(cmd)`, `vg.get_report_window()`, `vg.set_view(...)`.

---

## 4. Equivalencia con Maptek Python SDK 2.0 (`mapteksdk`)

En flujos externos que utilicen **Maptek Python SDK 2.0** (`mapteksdk` sobre Maptek Workbench):

| Concepto Minero | Vulcan Embedded SDK (`maptek.vulcan`) | Maptek Python SDK 2.0 (`mapteksdk`) |
| :--- | :--- | :--- |
| Conexión al proyecto | `os.getcwd()` en sesión Envisage | `from mapteksdk.project import Project` |
| Superficie / Malla 3D | `vulcan.triangulation("m.00t")` | `mapteksdk.data.Surface` (`.points`, `.facets`) |
| Grilla Topográfica | `vulcan.grid("g.grid")` | `mapteksdk.data.GridSurface` |
| Nube / Puntos 3D | `vulcan.polyline` / `point_list` | `mapteksdk.data.PointSet` (`.dataframe()`) |
| Modelo de Bloques | `vulcan.block_model("b.bmf")` | `DenseBlockModel` / `SubblockedBlockModel` |

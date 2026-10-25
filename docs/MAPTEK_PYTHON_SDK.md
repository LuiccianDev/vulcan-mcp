# Referencia Técnica: Maptek Vulcan Python SDK & Maptek SDK 2.0

Documentación consolidada a partir de **Maptek Python SDK Help** y la introspección directa de las librerías `maptek.vulcan` y `maptek.vulcan_gui` en **Maptek Vulcan 12 Desktop**.

---

## 1. Arquitectura de los Dos SDKs de Maptek

| Característica | `maptek.vulcan` / `maptek.vulcan_gui` | `mapteksdk` (SDK 2.0) |
| :--- | :--- | :--- |
| **Entorno** | Embebido dentro de Maptek Vulcan Desktop (Python 3.5.2 en Vulcan 12) | Paquete externo moderno para Maptek Workbench / PointStudio / GeologyCore |
| **Tecnología** | Bindings C++ generados con SWIG | API nativa orientada a objetos con soporte NumPy y Pandas |
| **Acceso en Vulcan MCP** | Directo en el listener y vía `vulcan_execute_code` | Para flujos de interoperabilidad con plataformas Maptek Workbench |

---

## 2. Catálogo de Clases y Métodos de `maptek.vulcan`

### 2.1 `vulcan.block_model` (Archivos `.bmf`)
Permite leer, filtrar, consultar y modificar modelos de bloques sin cargar la interfaz gráfica.

* **Apertura y Cierre**:
  * `bm = vulcan.block_model("modelo.bmf", "r")` (`"r"` lectura, `"w"` escritura)
  * `bm.close()`, `bm.is_open()`
* **Geometría y Esquema**:
  * `bm.n_blocks()`: Número total de bloques.
  * `bm.model_origin()`, `bm.model_orientation()`, `bm.model_extent()`, `bm.block_extent()`.
  * `bm.model_n_schemas()`, `bm.model_schema_extent(i)`, `bm.model_schema_size(i)`, `bm.model_schema_dimensions(i)`.
  * `bm.to_world(x, y, z)`, `bm.to_model(x, y, z)`: Conversión entre coordenadas de mundo y coordenadas locales del modelo.
* **Variables (Campos)**:
  * `bm.field_list()`: Lista todas las variables del modelo.
  * `bm.field_list_numbers()`, `bm.field_list_strings()`: Filtra variables numéricas o de texto.
  * `bm.is_field(name)`, `bm.is_number(name)`, `bm.is_string(name)`, `bm.field_type(name)`, `bm.field_default(name)`.
* **Búsqueda, Selección e Iteración**:
  * `bm.find_world_xyz(x, y, z)` / `bm.find_xyz(x, y, z)`: Ubica el bloque en las coordenadas dadas.
  * `bm.select(criteria)`: Aplica un filtro de selección de bloques.
  * `bm.rewind()`, `bm.next()`, `bm.eof()`: Recorrido secuencial de bloques.
* **Lectura y Escritura de Datos**:
  * `bm.get(var)` / `bm.get_string(var)`: Obtiene el valor numérico o string del bloque actual.
  * `bm.get_multiple(var_list)` / `bm.get_multiple_string(var_list)`: Lectura vectorial rápida.
  * `bm.match_volume()`: Volumen ($m^3$) del bloque actual.
  * `bm.get_pandas()` / `bm.get_pandas_extent(...)`: Extrae variables directamente como DataFrame.
  * `bm.put(var, val)`, `bm.put_string(var, val)`, `bm.write()`: Escritura en modo `"w"`.

```python
# Ejemplo rápido en vulcan_execute_code
bm = vulcan.block_model("eblock.bmf", "r")
try:
    bm.find_world_xyz(795500.0, 9125000.0, 3400.0)
    result = {
        "cut": bm.get("CUT"),
        "volume": bm.match_volume()
    }
finally:
    bm.close()
```

---

### 2.2 `vulcan.triangulation` (Archivos `.00t`)
Maneja superficies topográficas y sólidos 3D cerrados.

* **Apertura y Guardado**:
  * `tri = vulcan.triangulation("superficie.00t")` (para lectura en memoria) o `vulcan.triangulation("superficie.00t", "w")` (para edición).
  * `tri.save("salida.00t")`
  * ⚠️ **Importante sobre `tri.close()`**: A diferencia de `bm.close()` o `db.close()`, en `vulcan.triangulation` el método `tri.close()` es una **operación geométrica** que cierra los bordes abiertos de una superficie para convertirla en sólido (requiere modo `"w"`). No debe llamarse para cerrar archivos en modo lectura.
* **Topología y Validación**:
  * `tri.n_nodes()`, `tri.n_faces()`: Conteo de vértices y triángulos.
  * `tri.is_closed()`, `tri.is_consistent()`, `tri.is_crossing()`, `tri.is_ok()`.
  * `tri.volume()`: Volumen del sólido (requiere malla cerrada y consistente).
  * `tri.extent()`, `tri.centroid()`.
* **Consultas Espaciales**:
  * `tri.get_elevation(x, y)` / `tri.get_elevations(points_xy)`: Cota $Z$ proyectada sobre la superficie.
  * `tri.point_inside(x, y, z)`: `True` si el punto 3D $(x, y, z)$ está dentro del sólido.
  * `tri.segment_intersections(p1, p2)`: Puntos de corte entre un segmento $[p_1, p_2]$ y la triangulación.
* **Geometría**:
  * `tri.get_node(i)`, `tri.get_face(i)`, `tri.get_vertices()`, `tri.get_faces()`.
  * `tri.add_node(x, y, z)`, `tri.add_face(n1, n2, n3)`, `tri.colour`, `tri.set_colour(c)`, `tri.set_rgb(r, g, b)`.

---

### 2.3 `vulcan.isisdb` (Bases de Datos `.dhd.isis`)
Acceso de bajo nivel a bases de datos relacionales ISIS (sondajes, litología, leyes).

* **Apertura**:
  * `db = vulcan.isisdb("bmw_sondajes.dhd.isis", "r", "")`
  * `db.close()`, `db.is_open()`
* **Metadatos**:
  * `db.table_list()`: Tablas disponibles (ej. `['COLLARES', 'DIRECCIONES', 'LITOLOGIA', 'LEYES']`).
  * `db.field_list(table)`, `db.field_list_numbers(table)`, `db.field_list_strings(table)`.
  * `db.key_list()`: Lista todos los `HOLE_ID` (claves primarias).
* **Navegación y Lectura**:
  * `db.find_key(hole_id)`: Posiciona el cursor en el primer registro del sondaje.
  * `db.next_same_key()`: Avanza al siguiente registro perteneciente al mismo sondaje.
  * `db.goto_table(table_name)`: Salta a una tabla específica.
  * `db.rewind()`, `db.next()`, `db.eof()`.
  * `db.get_key()`, `db.get_table_name()`, `db.get(field)`, `db.get_string(field)`.

---

### 2.4 `vulcan.dgd`, `vulcan.layer` y `vulcan.polyline` (Diseño CAD `.dgd.isis`)

* **`vulcan.dgd`**:
  * `dgd = vulcan.dgd("diseño.dgd.isis", "r")` (o `"w"`, `"create"`).
  * `dgd.list_layers()`, `dgd.num_layers()`, `dgd.is_layer(name)`.
  * `dgd.get_layer(name)`, `dgd.append(layer)`, `dgd.save_layer(layer)`, `dgd.delete_layer(name)`, `dgd.close()`.
* **`vulcan.layer`**:
  * `lyr = vulcan.layer("NUEVA_CAPA")`
  * `lyr.num_objects()`, `lyr.get_object(i)`, `lyr.append(obj)`, `lyr.clear_objects()`, `lyr.get_description()`, `lyr.set_description(desc)`.
* **`vulcan.polyline`**:
  * `poly = vulcan.polyline()`
  * `poly.set_coordinates([[x1, y1, z1], [x2, y2, z2]])`, `poly.get_coordinates()`, `poly.num_points()`.
  * `poly.set_connected()`, `poly.set_closed(True)`, `poly.is_closed()`.
  * `poly.length()`, `poly.planar_area()`, `poly.centroid()`, `poly.point_inside([x, y, z])`.
  * `poly.set_name(name)`, `poly.get_name()`, `poly.set_colour(idx)`, `poly.get_colour()`.

---

## 3. Catálogo de `maptek.vulcan_gui` (Control de Envisage 3D)

* **Visualización de Triangulaciones**:
  * `vulcan_gui.load_triangulation(path)` / `vulcan_gui.load_triangulations([paths])`
  * `vulcan_gui.remove_triangulations([paths])`
  * `vulcan_gui.reload_triangulation(path)`
* **Capas y Objetos Temporales 3D**:
  * `vulcan_gui.add_layer(layer)`
  * `tobj = vulcan_gui.temp_object(polyline)` (renderiza geometría temporal en el viewport 3D sin modificar archivos DGD).
* **Interacción y Comandos**:
  * `vulcan_gui.macro(command_name)` / `vulcan_gui.workbench_macro(cmd)`
  * `vulcan_gui.get_report_window()`
  * `vulcan_gui.set_view(...)`, `vulcan_gui.set_window(...)`
  * `vulcan_gui.selection("Mensaje")`, `vulcan_gui.pick_point("Mensaje")`, `vulcan_gui.pick_triangulation("Mensaje")` *(Nota: los métodos `pick_*` y `selection` esperan clic del usuario en pantalla; no usarlos en automatizaciones desatendidas)*.

---

## 4. Resumen de Maptek Python SDK 2.0 (`mapteksdk`)

En entornos modernos de Maptek Workbench (`mapteksdk 2.0`), los datos espaciales se gestionan mediante contenedores tipados en `mapteksdk.data`:

1. **`PointSet`**: Conjunto de puntos 3D `[X, Y, Z]` con soporte para `.dataframe()` (integración directa con Pandas para atributos `R, G, B, A`, selección y visibilidad).
2. **`Surface`**: Superficie triangulada definida por arrays de vértices (`surface.points`) y facetas triangulares (`surface.facets = [[0, 1, 2], ...]`).
3. **`GridSurface`**: Malla regular 2.5D estructurada en filas y columnas con elevaciones y atributos por celda/nodo.
4. **`DenseBlockModel` / `SubblockedBlockModel`**: Representación de modelos de bloques densos o sub-bloqueados dentro del ecosistema `mapteksdk.data`.

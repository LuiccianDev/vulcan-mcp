# Referencia Completa de Herramientas MCP (Master Tools Catalog)

Documentación técnica detallada de las **9 herramientas maestras** expuestas por **Vulcan MCP** hacia clientes compatibles con el *Model Context Protocol* (Google Antigravity, Claude Desktop, Cursor, VS Code).

---

## Resumen Ejecutivo de Herramientas

| # | Herramienta MCP | Dominio Minero | Acciones Disponibles (`action=`) | Timeout |
| :-: | :--- | :--- | :--- | :---: |
| 1 | **`vulcan_system`** | Sistema e Inventario | `ping`, `project_info`, `capabilities` | `30s` |
| 2 | **`vulcan_block_model`** | Modelos de Bloques (`.bmf`) | `list`, `info`, `query_xyz`, `stats` | `120s` |
| 3 | **`vulcan_triangulation`** | Superficies y Sólidos (`.00t`/`.tri`) | `list`, `info`, `elevation`, `point_inside`, `load`, `unload` | `30s` |
| 4 | **`vulcan_design`** | Diseño CAD 3D (`.dgd.isis`) | `list_dbs`, `list_layers`, `layer_info`, `load_layer`, `clear_temp`, `create_polyline` | `30s` |
| 5 | **`vulcan_drillholes`** | Sondajes ISIS (`.dhd.isis`) | `list_dbs`, `schema`, `holes`, `hole`, `high_grade`, `display`, `clear_display` | `120s` |
| 6 | **`vulcan_legend`** | Leyendas Envisage (`.scd`) | `list`, `inspect`, `update`, `restore` | `30s` |
| 7 | **`vulcan_screenshot`** | Captura Viewport 3D | *(Directa: `max_width`, `quality`)* | `30s` |
| 8 | **`vulcan_canvas`** | Interfaz y Macros | `macro`, `report` | `30s` |
| 9 | **`vulcan_execute_code`** | Scripting PyVulcan | *(Directa: `code`)* | `120s` |

---

## 1. `vulcan_system` — Conectividad, Inventario y Capacidades

Verifica la salud del listener en Vulcan (`127.0.0.1:9877`) e inventaría todos los archivos mineros del directorio de trabajo activo.

### Parámetros
| Parámetro | Tipo | Requerido | Por Defecto | Descripción |
| :--- | :--- | :---: | :---: | :--- |
| `action` | `"ping" \| "project_info" \| "capabilities"` | Sí | `"project_info"` | Operación de sistema a ejecutar. |

### Ejemplos de Respuesta
* **`action="ping"`**:
  ```json
  {
    "connected": true,
    "app": "Maptek Vulcan",
    "python": "3.5.2",
    "vulcan_api": true,
    "project_dir": "C:\\Users\\DAVID\\Desktop\\vulcanProyects\\Practica_Completa_Final"
  }
  ```
* **`action="capabilities"`**:
  ```json
  {
    "maptek.vulcan": true,
    "maptek.vulcan_gui": true,
    "pandas": true,
    "PIL": true,
    "win32gui": true,
    "gfx": false
  }
  ```

---

## 2. `vulcan_block_model` — Modelos de Bloques (`.bmf`)

Inspección geométrica, consulta espacial $(X, Y, Z)$ y cubicación estadística ponderada por volumen sobre archivos `.bmf`.

### Parámetros
| Parámetro | Tipo | Requerido en | Descripción |
| :--- | :--- | :--- | :--- |
| `action` | `"list" \| "info" \| "query_xyz" \| "stats"` | Todas | Acción a ejecutar sobre modelos de bloques. |
| `model` | `str` | `info`, `query_xyz`, `stats` | Nombre del archivo `.bmf` (ej. `"bmw_ml_30_30_30.bmf"`). |
| `x`, `y`, `z` | `float` | `query_xyz` | Coordenadas de mundo $(X, Y, Z)$ a consultar. |
| `variables` | `list[str]` | Opcional en `query_xyz` | Lista de variables a leer (si se omite, lee todas). |
| `variable` | `str` | `stats` | Variable numérica a cubicar (ej. `"CUT"`). |
| `cutoff` | `float` | Opcional en `stats` | Ley de corte para calcular estadísticas sobre `variable >= cutoff`. |
| `density` | `float` | Opcional en `stats` | Densidad media ($t/m^3$) para reportar tonelaje (`tonnes = volume * density`). |
| `select` | `str` | Opcional en `stats` | Expresión de filtro de Vulcan para seleccionar bloques específicos. |

### Ejemplo de Respuesta (`action="stats"`)
```json
{
  "variable": "CUT",
  "select": "",
  "excluded_default": -99.0,
  "summary": {
    "blocks": 14520,
    "min": 0.01,
    "max": 4.85,
    "mean": 0.62,
    "volume_weighted_mean": 0.64,
    "volume": 392040000.0,
    "tonnes": 1058508000.0
  },
  "above_cutoff": {
    "cutoff": 0.5,
    "blocks": 7840,
    "min": 0.5,
    "max": 4.85,
    "mean": 0.98,
    "volume_weighted_mean": 1.01,
    "volume": 211680000.0,
    "tonnes": 571536000.0
  }
}
```

---

## 3. `vulcan_triangulation` — Superficies y Sólidos 3D (`.00t` / `.tri`)

Análisis geométrico, validación topológica, interpolación de cotas $Z$, evaluación de puntos dentro de sólidos y visualización 3D.

### Parámetros
| Parámetro | Tipo | Requerido en | Descripción |
| :--- | :--- | :--- | :--- |
| `action` | `"list" \| "info" \| "elevation" \| "point_inside" \| "load" \| "unload"` | Todas | Acción a ejecutar. |
| `name` | `str` | Todas excepto `list` | Nombre del archivo `.00t` o `.tri` (ej. `"topografia_1.00t"`). |
| `points` | `list[list[float]]` | `elevation`, `point_inside` | En `elevation`: `[[x, y], ...]`. En `point_inside`: `[[x, y, z], ...]`. |

### Ejemplo de Respuesta (`action="info"`)
```json
{
  "name": "topografia_1.00t",
  "nodes": 2201,
  "faces": 4224,
  "extent": [[474025.37, 4479261.5, 546.97], [475294.53, 4480530.66, 673.17]],
  "closed": false,
  "consistent": true,
  "crossing": false,
  "ok": true,
  "centroid": [474665.49, 4479896.76, 634.80]
}
```

---

## 4. `vulcan_design` — Bases de Diseño CAD 3D (`.dgd.isis`)

Exploración, visualización y creación de capas y polilíneas/polígonos 3D en bases de diseño `.dgd.isis`.

### Parámetros
| Parámetro | Tipo | Requerido en | Descripción |
| :--- | :--- | :--- | :--- |
| `action` | `"list_dbs" \| "list_layers" \| "layer_info" \| "load_layer" \| "clear_temp" \| "create_polyline"` | Todas | Acción CAD a ejecutar. |
| `dgd` | `str` | `list_layers`, `layer_info`, `load_layer`, `create_polyline` | Archivo `.dgd.isis` (ej. `"baisusxier.dgd.isis"`). |
| `layer` | `str` | `layer_info`, `load_layer`, `create_polyline` | Nombre de la capa (ej. `"SONDAJE_LEYES"`, `"TOPO"`). |
| `points` | `list[list[float]]` | `create_polyline` | Lista de vértices 3D `[[x, y, z], ...]` (mínimo 2 puntos). |
| `closed` | `bool` | Opcional en `create_polyline` | Si es `True`, cierra la polilínea como polígono. |
| `colour` | `int` | Opcional en `create_polyline` | Índice de color de la paleta de Vulcan (`1`=Rojo, `2`=Verde, etc.). |
| `name` | `str` | Opcional en `create_polyline` | Nombre identificador del objeto CAD. |
| `use_temp_objects` | `bool` | Opcional en `load_layer` | Por defecto `True` (renderiza vía `vg.temp_object` sin bloquear edición). |
| `limit`, `offset` | `int` | Opcional en `layer_info` | Paginación de objetos (por defecto `limit=20`, `offset=0`). |

---

## 5. `vulcan_drillholes` — Sondajes ISIS (`.dhd.isis`) y Desurvey 3D

Consultas relacionales sobre bases de perforación ISIS, detección de interceptos de alta ley y visualización 3D coloreada por ley.

### Parámetros
| Parámetro | Tipo | Requerido en | Descripción |
| :--- | :--- | :--- | :--- |
| `action` | `"list_dbs" \| "schema" \| "holes" \| "hole" \| "high_grade" \| "display" \| "clear_display"` | Todas | Acción sobre sondajes. |
| `db` | `str` | `schema`, `holes`, `hole`, `high_grade`, `display` | Archivo `.dhd.isis` (ej. `"bmw_sondajes.dhd.isis"`). |
| `hole` | `str` | `hole` | Identificador de un sondaje (ej. `"SOP25"`). |
| `holes` | `list[str]` | Opcional en `display` | Lista de taladros específicos a renderizar. |
| `table` | `str` | `high_grade` (opcional en `hole`, `display`) | Tabla ISIS (ej. `"LEYES"`, `"COLLARES"`, `"DIRECCIONES"`). |
| `field` | `str` | `high_grade` (opcional en `display`) | Campo numérico de ley (ej. `"CUT"`). |
| `min_value` | `float` | `high_grade` | Valor mínimo de corte para filtrar intervalos de alta ley. |
| `limit` | `int` | Opcional | Límite de registros, taladros o top interceptos. |
| `max_segments` | `int` | Opcional en `display` | Límite de segmentos 3D en Envisage (por defecto `300`). |
| `save_layer` | `str` | Opcional en `display` | Guarda las trazas 3D generadas en una capa del archivo `.dgd.isis`. |

---

## 6. `vulcan_legend` — Leyendas de Colores Envisage (`.scd`)

Inspección y actualización de esquemas de colores `.scd` con copia de seguridad automática `.scd.bak`.

### Parámetros
| Parámetro | Tipo | Requerido en | Descripción |
| :--- | :--- | :--- | :--- |
| `action` | `"list" \| "inspect" \| "update" \| "restore"` | Todas | Acción sobre leyendas. |
| `scd` | `str` | `inspect`, `update`, `restore` | Archivo `.scd` (ej. `"bai.scd"`). |
| `scheme` | `str` | `update` | Esquema dentro del `.scd` (ej. `"DRILL_COLOUR"`, `"BLOCK_COLOUR"`). |
| `table` | `str` | `update` | Tabla dentro del esquema (ej. `"COBRE"`, `"LEYES"`). |
| `preset` | `"high_contrast_mining" \| "classic_blue_to_red" \| "traffic_light" \| "hot_metal"` | `update` (o `colours`) | Paleta minera predefinida. |
| `colours` | `list[str]` | `update` (o `preset`) | Lista personalizada de códigos de color de Vulcan. |

---

## 7. `vulcan_screenshot` — Captura Visual 3D Optimizada

Localiza automáticamente la ventana visible de Maptek Vulcan mediante `win32gui`, captura el lienzo 3D, lo redimensiona manteniendo proporción y lo comprime en JPEG.

* **`max_width`** (`int`, por defecto `800`): Ancho máximo en píxeles.
* **`quality`** (`int`, por defecto `70`): Calidad de compresión JPEG (`1-95`).
* **Retorno**: Objeto `ImageContent` (`mimeType="image/jpeg"`) listo para visión multimodal del LLM.

---

## 8. `vulcan_canvas` — Macros y Consola de Reportes

* **`action="macro"`** (`macro: str`): Ejecuta un comando de macro en Envisage Workbench (`vg.workbench_macro`).
* **`action="report"`** (`text: str`): Imprime texto en la ventana de reportes de Maptek Vulcan (`vg.print_message`).

---

## 9. `vulcan_execute_code` — Scripting Directo en PyVulcan

Permite ejecutar cualquier rutina avanzada sobre el intérprete Python 3.5.2 embebido en Vulcan.
* **Variables pre-inyectadas**: `vulcan` (`maptek.vulcan`), `vulcan_gui` (`maptek.vulcan_gui`), `project_dir` (ruta del proyecto).
* **Retorno de datos**: Asigna cualquier diccionario, lista o escalar a la variable `result`.
* **Restricción importante**: Escribir código compatible con **Python 3.5** (usar `.format()` en lugar de *f-strings*).

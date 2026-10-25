---
name: vulcan-tools-catalog
description: Catalogo completo y guia rapida de las 9 herramientas maestras de Vulcan MCP (acciones, parametros obligatorios/opcionales y valores de retorno).
---

# Catálogo de las 9 Herramientas Maestras (Vulcan MCP)

Usa esta referencia para seleccionar la herramienta exacta y los parámetros requeridos en cada operación sobre Maptek Vulcan 12 Desktop.

---

## 1. `vulcan_system` — Conectividad e Inventario del Proyecto
* **Acciones (`action=`)**:
  * `"ping"`: Verifica conexión TCP en vivo con Vulcan (`connected`, `python`, `project_dir`).
  * `"project_info"`: Lista todos los archivos mineros del directorio activo (`block_models`, `triangulations`, `design_dbs`, `drillhole_dbs`, `legends`).
  * `"capabilities"`: Verifica librerías disponibles dentro del Python de Vulcan (`pandas`, `PIL`, `win32gui`).

---

## 2. `vulcan_block_model` — Modelos de Bloques (`.bmf`)
* **Acciones (`action=`)**:
  * `"list"`: Lista archivos `.bmf`.
  * `"info"`: Requiere `model`. Devuelve `n_blocks`, `origin`, `orientation`, `world_extent`, `schemas` y lista de `variables` (tipo, valor por defecto y descripción).
  * `"query_xyz"`: Requiere `model`, `x`, `y`, `z` (opcional `variables`). Devuelve leyes y dimensiones del bloque en esa coordenada espacial.
  * `"stats"`: Requiere `model`, `variable` (opcionales `cutoff`, `density`, `select`). Calcula bloques válidos, mínimo, máximo, media aritmética, **media ponderada por volumen**, volumen ($m^3$) y **tonelaje** total y sobre ley de corte.

---

## 3. `vulcan_triangulation` — Superficies y Sólidos 3D (`.00t` / `.tri`)
* **Acciones (`action=`)**:
  * `"list"`: Lista archivos `.00t` y `.tri`.
  * `"info"`: Requiere `name`. Devuelve `nodes`, `faces`, `extent`, `closed`, `consistent`, `crossing`, `ok`, `centroid` $[X, Y, Z]$ y `volume` (si es cerrado).
  * `"elevation"`: Requiere `name` y `points=[[x, y], ...]`. Devuelve la cota $Z$ interpolada sobre la superficie.
  * `"point_inside"`: Requiere `name` y `points=[[x, y, z], ...]`. Devuelve `inside: True/False` para cada coordenada 3D respecto al sólido.
  * `"load"` / `"unload"`: Requiere `name`. Carga o descarga la triangulación en el viewport 3D de Envisage.

---

## 4. `vulcan_design` — Bases de Diseño CAD 3D (`.dgd.isis`)
* **Acciones (`action=`)**:
  * `"list_dbs"`: Lista bases de diseño `.dgd.isis`.
  * `"list_layers"`: Requiere `dgd`. Lista todas las capas y su conteo de objetos.
  * `"layer_info"`: Requiere `dgd`, `layer` (opcionales `limit`, `offset`). Devuelve objetos con `name`, `points`, `length`, `closed`, `planar_area` ($m^2$) y `centroid` $[X, Y, Z]$.
  * `"load_layer"`: Requiere `dgd`, `layer` (opcionales `use_temp_objects=True`, `load_method`). Renderiza la capa en la ventana 3D.
  * `"clear_temp"`: Limpia los objetos CAD temporales del viewport 3D.
  * `"create_polyline"`: Requiere `dgd`, `layer`, `points=[[x, y, z], ...]` (opcionales `closed`, `colour`, `name`). Crea y guarda una polilínea o polígono 3D.

---

## 5. `vulcan_drillholes` — Bases de Sondajes ISIS (`.dhd.isis`)
* **Acciones (`action=`)**:
  * `"list_dbs"`: Lista bases de sondajes `.dhd.isis`.
  * `"schema"`: Requiere `db`. Devuelve conteo de taladros (`holes`), tablas (`COLLARES`, `DIRECCIONES`, `LEYES`, `LITOLOGIA`) y campos.
  * `"holes"`: Requiere `db` (opcionales `limit`, `offset`). Lista paginada de `HOLE_ID`.
  * `"hole"`: Requiere `db`, `hole` (opcionales `table`, `limit`). Extrae los registros del taladro.
  * `"high_grade"`: Requiere `db`, `table`, `field`, `min_value` (opcional `limit`). Escanea toda la base buscando los mejores interceptos minerales.
  * `"display"`: Requiere `db` (opcionales `holes`, `table="LEYES"`, `field="CUT"`, `limit=5`, `max_segments=300`, `save_layer`). Calcula el *desurvey* 3D y pinta los sondajes coloreados por ley en Envisage.
  * `"clear_display"`: Limpia los sondajes temporales de la pantalla 3D.

---

## 6. `vulcan_legend` — Leyendas de Colores Envisage (`.scd`)
* **Acciones (`action=`)**:
  * `"list"`: Lista archivos `.scd` y paletas predefinidas (`high_contrast_mining`, `classic_blue_to_red`, `traffic_light`, `hot_metal`).
  * `"inspect"`: Requiere `scd`. Muestra esquemas (`BLOCK_COLOUR`, `DRILL_COLOUR`) y sus rangos.
  * `"update"`: Requiere `scd`, `scheme`, `table` y `preset` (o `colours`). Actualiza colores creando respaldo automático `.scd.bak`.
  * `"restore"`: Requiere `scd`. Restaura el archivo desde su `.scd.bak`.

---

## 7. `vulcan_screenshot` — Captura Visual 3D Optimizada
* **Parámetros**: `max_width=800`, `quality=70`.
* **Retorno**: Imagen JPEG comprimida de la ventana 3D de Maptek Vulcan para inspección visual con bajo consumo de tokens.

---

## 8. `vulcan_canvas` — Macros y Consola de Reportes
* **Acciones (`action=`)**:
  * `"macro"`: Requiere `macro`. Ejecuta un comando o macro de Envisage Workbench.
  * `"report"`: Requiere `text`. Imprime un mensaje en la ventana de reportes de Vulcan.

---

## 9. `vulcan_execute_code` — Scripting Directo en PyVulcan
* **Parámetros**: `code` (string de código compatible con Python 3.5; asignar resultado a `result = ...`).
* **Retorno**: `executed`, `result`, `stdout`, `stderr`. Tiene `vulcan`, `vulcan_gui` y `project_dir` precargados.

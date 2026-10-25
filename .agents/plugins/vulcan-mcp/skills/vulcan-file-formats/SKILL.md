---
name: vulcan-file-formats
description: Referencia oficial y concisa de los formatos de archivo de Maptek Vulcan (.bmf, .00t, .dgd.isis, .dhd.isis, .scd, .grid) y que herramienta MCP usar para cada uno.
---

# Formatos de Archivo de Maptek Vulcan

Guía rápida basada en la documentación oficial de **Maptek Vulcan Help** para identificar y operar cada tipo de archivo del proyecto minero.

---

## 1. Mapa Rápido de Extensiones y Herramientas MCP

| Extensión | Nombre Oficial | Contenido Principal | Herramienta MCP |
| :--- | :--- | :--- | :--- |
| **`.bmf`** | Block Model File | Modelo de bloques 3D (regular o sub-bloqueado), leyes, densidad, litología, economía. | `vulcan_block_model` |
| **`.00t`** (`.tri`, `.sft`, `.srt`) | Triangulation | Superficies 3D (topografía, fallas) y sólidos cerrados (cuerpos mineralizados, labores, pits). | `vulcan_triangulation` |
| **`.dgd.isis`** | Design Database | Base de datos espacial CAD 3D (post-v7.0): capas (`layers`), polilíneas, polígonos, puntos y textos. | `vulcan_design` |
| **`.dhd.isis`** | Drillhole ISIS DB | Base de datos relacional ISIS de sondajes: collares, desviaciones (`survey`), leyes e intervalos. | `vulcan_drillholes` |
| **`.scd`** | Scheme / Legend File | Esquemas de colores y leyendas de Envisage (mapeo de rangos de ley o códigos de roca a colores). | `vulcan_legend` |
| **`.dgd.isix` / `.dhd.isix`** | ISIS Index File | Índice binario de acceso rápido para bases `.isis`. **No editar ni borrar manualmente.** | *(Interno del SDK)* |
| **`.wrk`** | Work File | Archivo temporal de recuperación durante edición activa en Envisage. | *(Interno de Vulcan)* |
| **`.grid` / `.sfg`** | Grid Surface | Mallas regulares 2D/2.5D de elevación o interpolación estructural. | `vulcan_execute_code` (`v.grid`) |

---

## 2. Reglas por Tipo de Archivo

### Modelos de Bloques (`.bmf`)
* Contienen una definición geométrica (origen $X_0, Y_0, Z_0$, orientación/rotación y esquemas de tamaño de bloque) y variables por bloque.
* Las variables pueden ser **numéricas** (`float`/`double`, ej. `CUT`, `DENS`, `AU`) o **alfanuméricas** (`string`, ej. `ROCK`, `ZONE`).
* Siempre abre en modo lectura (`"r"`) para consultas o cubicaciones (`action="info"`, `action="query_xyz"`, `action="stats"`).

### Triangulaciones (`.00t`)
* Compuestas por **nodos** (vértices $[X, Y, Z]$) y **caras** (triángulos de 3 índices $[i_1, i_2, i_3]$).
* **Superficie abierta (`closed: false`)**: Topografía (`topo*.00t`), nivel freático o fallas. Útil para proyectar cotas $Z$ (`action="elevation"`).
* **Sólido cerrado (`closed: true`)**: Orebody, tajo o caserón. Permite calcular volumen real (`action="info"` -> `volume`).

### Bases de Diseño CAD (`.dgd.isis`)
* Organizadas en **Capas (`Layers`)**, donde cada capa agrupa objetos vectoriales (`polyline`).
* Una capa típica como `SONDAJE_LEYES` o `TOPO` contiene polilíneas 3D con nombre, color de paleta Vulcan y coordenadas.
* Usa `action="list_layers"` antes de cargar (`load_layer`) o inspeccionar (`layer_info`).

### Bases de Sondajes ISIS (`.dhd.isis`)
* Estructura jerárquica indexada por clave de taladro (`Key` = `HOLE_ID`).
* Tablas típicas en proyectos en español/inglés:
  * **Collares**: `COLLARES` / `COLLAR` / `LOCATION` ($X, Y, Z$, longitud total).
  * **Desviaciones**: `DIRECCIONES` / `SURVEY` (`FROM`/`DEPTH`, `AZIMUTH`, `BUZ`/`DIP`).
  * **Ensayes**: `LEYES` / `ASSAY` (`FROM`, `TO`, `CUT`, `AU`, `AG`).
  * **Geología**: `LITOLOGIA` / `LITHOLOGY` (`FROM`, `TO`, `RX`, `ALT`).

### Leyendas y Esquemas de Color (`.scd`)
* Archivos de texto estructurados por bloques de esquema (ej. `DRILL_COLOUR`, `BLOCK_COLOUR`).
* Al actualizar una leyenda con `vulcan_legend` (`action="update"`), se genera automáticamente un respaldo `.scd.bak` restaurable con `action="restore"`.

# Formatos de Archivo Oficiales de Maptek Vulcan

Referencia técnica basada en **Maptek Vulcan Help** para los archivos que conforman un proyecto geológico y minero en Maptek Vulcan Desktop.

---

## Tabla Resumen de Extensiones

| Extensión | Nombre Oficial | Descripción | Herramienta MCP |
| :--- | :--- | :--- | :--- |
| **`.bmf`** | Block Model File | Modelo de bloques 3D (regular o sub-bloqueado), leyes, densidad y litología. | `vulcan_block_model` |
| **`.00t`** (`.tri`, `.sft`, `.srt`) | Triangulation | Mallas 3D trianguladas: superficies abiertas (topografía, fallas) y sólidos cerrados. | `vulcan_triangulation` |
| **`.dgd.isis`** | Design Database | Base de datos espacial CAD 3D (capas, polilíneas, polígonos, puntos y textos). | `vulcan_design` |
| **`.dhd.isis`** | Drillhole ISIS DB | Base de datos relacional ISIS de sondajes (collares, desviaciones, leyes, litología). | `vulcan_drillholes` |
| **`.scd`** | Scheme / Legend File | Esquemas de colores y leyendas de Envisage (`BLOCK_COLOUR`, `DRILL_COLOUR`). | `vulcan_legend` |
| **`.dsf`** | Design Specification | Especificaciones de diseño y diccionarios de bases de datos ISIS. | `vulcan_system` (`project_info`) |
| **`.dgd.isix` / `.dhd.isix`** | ISIS Index File | Índices binarios de acceso rápido para bases `.isis`. **No editar manualmente.** | *(Interno del SDK)* |
| **`.wrk`** | Work File | Archivo temporal de recuperación generado durante sesiones de edición en Envisage. | *(Interno de Vulcan)* |
| **`.grid` / `.sfg`** | Grid Surface | Mallas regulares 2D/2.5D de elevación o interpolación estructural. | `vulcan_execute_code` (`v.grid`) |

---

## 1. Modelos de Bloques (`.bmf`)
* **Descripción**: Formato binario nativo de Maptek Vulcan (*Block Model File*) para estimación de recursos, reservas y planificación minera.
* **Estructura**:
  * **Geometría**: Origen $(X_0, Y_0, Z_0)$, orientación en 3D (ángulos de rotación) y esquemas de celdas (`model_n_schemas()`, tamaños `model_schema_size(k)` y extensiones `model_schema_extent(k)`).
  * **Variables**: Almacena atributos por bloque de tipo numérico (`float`/`double` como `CUT`, `AU`, `DENS`, `TONS`, con valor nulo por defecto ej. `-99.0`) o texto (`string` como `ROCK`, `DOMAIN`).
* **Variables Implícitas de Coordenadas**:
  * `xworld`, `yworld`, `zworld`: Centroide del bloque en coordenadas de mundo.
  * `xlength`, `ylength`, `zlength`: Dimensiones $(dx, dy, dz)$ del bloque actual.
* **Herramienta MCP**: `vulcan_block_model` (`list`, `info`, `query_xyz`, `stats`).

---

## 2. Triangulaciones 3D (`.00t`, `.tri`, `.sft`, `.srt`)
* **Descripción**: Formato estándar para mallas trianguladas 3D en Vulcan.
  * ⚠️ **Nota sobre carpetas `.tri/`**: En proyectos de Vulcan, es común encontrar directorios llamados `P1.tri/` o `PitOptimizer.tri/`. `Vulcan MCP` filtra automáticamente directorios mediante `os.path.isfile()` para listar únicamente archivos de triangulación válidos.
* **Estructura**:
  * Lista indexada de **nodos** (vértices 3D $[X, Y, Z]$) y **caras** (facetas triangulares $[n_1, n_2, n_3]$).
  * **Superficies abiertas (`closed = False`)**: Topografías (`topografia_1.00t`), superficies de falla o contactos litológicos. Ideales para consultar cotas con `elevation`.
  * **Sólidos cerrados (`closed = True`)**: Cuerpos mineralizados (*orebodies*), labores subterráneas, caserones (*stopes*) o fases de tajo. Permiten cálculo directo de volumen ($m^3$) y validación `point_inside`.
* **Validación de Calidad Topológica**:
  * `consistent` (`is_consistent()`): Normales de caras orientadas coherentemente.
  * `crossing` (`is_crossing()`): Indica si existen auto-intersecciones entre triángulos (`False` en mallas limpias).
  * `ok` (`is_ok()`): Estado general de integridad de la malla.
* **Herramienta MCP**: `vulcan_triangulation` (`list`, `info`, `elevation`, `point_inside`, `load`, `unload`).

---

## 3. Bases de Datos de Diseño CAD (`.dgd.isis`)
* **Descripción**: Formato espacial de diseño y dibujo CAD 3D (introducido desde Vulcan 7.0+ sobre motor ISIS).
* **Estructura Interna**:
  * Contiene **Capas (`Layers`)** identificadas por nombre (ej. `TOPO`, `SONDAJE_LEYES`, `LIMITES_MG`). Las capas internas del sistema con prefijo `DIG$` se omiten automáticamente.
  * Cada capa almacena objetos geométricos (`polyline`), con atributos de coordenadas 3D, color de paleta Vulcan, longitud 3D (`length`), área planar (`planar_area`) y centroide (`centroid`).
* **Herramienta MCP**: `vulcan_design` (`list_dbs`, `list_layers`, `layer_info`, `load_layer`, `clear_temp`, `create_polyline`).

---

## 4. Bases de Datos ISIS de Sondajes (`.dhd.isis`)
* **Descripción**: Base de datos relacional jerárquica de Vulcan utilizada para almacenar perforaciones y taladros (*drillholes*).
* **Estructura Interna**:
  * Organizada por una clave primaria por sondaje (`Key` = identificador del taladro, ej. `SOP25`, `SK08`).
  * **Tablas y Campos Estándar (Soporte Bilingüe Español / Inglés)**:

| Tabla | Nombres Reconocidos | Campos Clave Reconocidos |
| :--- | :--- | :--- |
| **Collares** | `COLLARES`, `COLLAR`, `LOCATION` | `HOLE_ID`, `X`/`EAST`/`ESTE`, `Y`/`NORTH`/`NORTE`, `Z`/`RL`/`COTA`, `LENGTH`/`LENGHT` |
| **Desviaciones** | `DIRECCIONES`, `SURVEY`, `SURVEYS`, `DEVIATION` | `FROM`/`DESDE`/`DEPTH`/`PROF`/`AT`, `AZIMUTH`/`AZIMUT`/`BRG`, `BUZ`/`BUZAMIENTO`/`DIP`/`INCL` |
| **Ensayes** | `LEYES`, `ASSAY`, `ASSAYS` | `FROM`/`DESDE`, `TO`/`HASTA`, `CUT`, `CU`, `AU`, `AG`, `GRADE`, `LEY` |
| **Litología** | `LITOLOGIA`, `LITHOLOGY` | `FROM`, `TO`, `RX`, `SIMPL`, `ALT` |

* **Herramienta MCP**: `vulcan_drillholes` (`list_dbs`, `schema`, `holes`, `hole`, `high_grade`, `display`, `clear_display`).

---

## 5. Esquemas de Color y Leyendas (`.scd`)
* **Descripción**: Archivos de especificación en codificación `latin1` que definen leyendas visuales en Envisage.
* **Estructura Sintáctica**:
  ```text
  BEGIN$DEF DRILL_COLOUR
   BEGIN$TAB COBRE
     'CUT'
     '#LEYES'
     'FROM'
     'TO'
     ''
     '144'    <-- Índice de color Vulcan
     '0.0'    <-- Desde (FROM)
     '0.5'    <-- Hasta (TO)
     'GELT'   <-- Regla de comparación (Greater or Equal, Less Than)
   END$TAB COBRE
  END$DEF DRILL_COLOUR
  ```
* **Paleta de Colores Estándar en Vulcan (Display Colours)**:
  * `1`: Rojo (Alta ley $\ge 1.0\%$)
  * `2`: Verde (Ley baja $0.2\% - 0.5\%$)
  * `3` / `45`: Amarillo (Ley media $0.5\% - 0.8\%$)
  * `4`: Naranja (Ley media-alta $0.8\% - 1.0\%$)
  * `5` / `144`: Azul / Cian (Estéril o traza $< 0.2\%$)
  * `6`: Magenta
* **Herramienta MCP**: `vulcan_legend` (`list`, `inspect`, `update`, `restore`).

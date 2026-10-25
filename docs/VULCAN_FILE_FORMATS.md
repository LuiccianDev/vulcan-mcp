# Formatos de Archivo Oficiales de Maptek Vulcan

Referencia técnica basada en **Maptek Vulcan Help** para los archivos que conforman un proyecto geológico y minero en Vulcan.

---

## 1. Modelos de Bloques (`.bmf`)
* **Descripción**: Formato binario nativo de Maptek Vulcan (*Block Model File*) para estimación de recursos, reservas y planificación minera.
* **Estructura**:
  * **Geometría**: Origen $(X_0, Y_0, Z_0)$, orientación en 3D (ángulos de rotación) y esquemas de celdas (bloques regulares o sub-bloqueados).
  * **Variables**: Almacena atributos por bloque de tipo numérico (`float`/`double` como `CUT`, `AU`, `DENS`, `TONS`) o texto (`string` como `ROCK`, `DOMAIN`).
* **Herramienta MCP**: `vulcan_block_model` (`list`, `info`, `query_xyz`, `stats`).

---

## 2. Triangulaciones 3D (`.00t`, `.tri`, `.sft`, `.srt`)
* **Descripción**: Formato estándar para mallas trianguladas 3D en Vulcan.
* **Estructura**:
  * Lista indexada de **nodos** (vértices 3D $[X, Y, Z]$) y **caras** (facetas triangulares $[n_1, n_2, n_3]$).
  * **Superficies abiertas (`closed = False`)**: Topografías (`topo*.00t`), superficies de falla, niveles freáticos o contactos litológicos.
  * **Sólidos cerrados (`closed = True`)**: Cuerpos mineralizados (*orebodies*), labores subterráneas, caserones (*stopes*) o fases de tajo. Permiten cálculo directo de volumen ($m^3$).
* **Herramienta MCP**: `vulcan_triangulation` (`list`, `info`, `elevation`, `load`, `unload`).

---

## 3. Bases de Datos de Diseño CAD (`.dgd.isis`)
* **Descripción**: Formato espacial de diseño y dibujo CAD 3D (introducido desde Vulcan 7.0+ sobre motor ISIS).
* **Archivos Asociados**:
  * `.dgd.isis`: Archivo principal de datos vectoriales.
  * `.dgd.isix`: Archivo de índice espacial/binario de alta velocidad.
  * `.wrk`: Archivo de trabajo temporal creado mientras una sesión de Envisage edita diseños (para recuperación ante cierres inesperados).
* **Estructura Interna**:
  * Contiene **Capas (`Layers`)** identificadas por nombre (ej. `TOPO`, `SONDAJE_LEYES`, `RAMPAS`).
  * Cada capa almacena objetos geométricos (`polyline`), con atributos de coordenadas 3D, color de paleta Vulcan, tipo de línea, grupo y conectividad (abierta o polígono cerrado).
* **Herramienta MCP**: `vulcan_design` (`list_dbs`, `list_layers`, `layer_info`, `load_layer`, `create_polyline`).

---

## 4. Bases de Datos ISIS de Sondajes (`.dhd.isis`)
* **Descripción**: Base de datos relacional jerárquica de Vulcan utilizada para almacenar perforaciones y taladros (*drillholes*).
* **Archivos Asociados**: `.dhd.isis` (datos) y `.dhd.isix` (índice).
* **Estructura Interna**:
  * Organizada por una clave primaria por sondaje (`Key` = identificador del taladro, ej. `SOP25`).
  * **Tablas estándar** (nombres habituales en proyectos en español e inglés):
    * **Collares** (`COLLARES` / `COLLAR` / `LOCATION`): Coordenadas de boca de pozo (`X`, `Y`, `Z`) y profundidad total (`LENGTH` / `LENGHT`).
    * **Desviaciones** (`DIRECCIONES` / `SURVEY`): Mediciones de trayectoria con profundidad (`FROM` / `DEPTH` / `AT`), azimut (`AZIMUTH` / `AZ`) e inclinación/buzamiento (`BUZ` / `DIP`).
    * **Ensayes** (`LEYES` / `ASSAY`): Tramos muestreados (`FROM`, `TO`) y leyes minerales (`CUT`, `AU`, `AG`, `MO`).
    * **Litología** (`LITOLOGIA` / `LITHOLOGY`): Tramos geológicos (`FROM`, `TO`, `RX`, `ALT`).
* **Herramienta MCP**: `vulcan_drillholes` (`list_dbs`, `schema`, `holes`, `hole`, `high_grade`, `display`, `clear_display`).

---

## 5. Esquemas de Color y Leyendas (`.scd`)
* **Descripción**: Archivos de especificación (*Specification / Scheme Data*) que definen leyendas visuales y mapeos de colores en Envisage.
* **Estructura Interna**:
  * Define esquemas nombrados como `DRILL_COLOUR`, `BLOCK_COLOUR`, etc.
  * Asocia intervalos numéricos (`FROM` -> `TO`) o códigos discretos a índices de color de la paleta de Vulcan.
* **Herramienta MCP**: `vulcan_legend` (`list`, `inspect`, `update`, `restore`).

---

## 6. Mallas y Grillas (`.grid`, `.sfg`)
* **Descripción**: Superficies grilladas regulares organizadas en filas y columnas para modelos de elevación digital o contornos estructurales.
* **Operación**: A través de `vulcan_execute_code` utilizando `vulcan.grid`.

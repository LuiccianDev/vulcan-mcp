# Documentación Técnica: Maptek Vulcan & Python SDK

Esta carpeta concentra toda la referencia técnica de **Vulcan MCP**, extraída de la documentación oficial de **Maptek Vulcan Help**, **Maptek Python SDK 2.0** y la introspección directa del SDK embebido en **Maptek Vulcan 12 Desktop**.

---

## Índice de Documentos

1. **[Arquitectura Interna, Protocolo TCP y Seguridad (`ARCHITECTURE_AND_SECURITY.md`)](./ARCHITECTURE_AND_SECURITY.md)**
   * Diseño en dos procesos (Python 3.12+ externo $\leftrightarrow$ Python 3.5.2 embebido en Vulcan).
   * Protocolo binario `uint32` big-endian, retención de memoria SWIG/OpenGL, seguridad por token (`.env` / `os.getenv`) y recarga en caliente (*hot-reload*).

2. **[Referencia de las 9 Herramientas MCP (`MCP_TOOLS_REFERENCE.md`)](./MCP_TOOLS_REFERENCE.md)**
   * Catálogo completo de las 9 herramientas maestras (`vulcan_system`, `vulcan_block_model`, `vulcan_triangulation`, `vulcan_design`, `vulcan_drillholes`, `vulcan_legend`, `vulcan_screenshot`, `vulcan_canvas`, `vulcan_execute_code`), tablas de parámetros y ejemplos reales de salida JSON.

3. **[Formatos de Archivo de Vulcan (`VULCAN_FILE_FORMATS.md`)](./VULCAN_FILE_FORMATS.md)**
   * Especificación de archivos `.bmf`, `.00t`, `.dgd.isis`, `.dhd.isis`, `.scd`, `.grid`, `.isix` y `.wrk`.
   * Estructura interna de tablas ISIS en español/inglés y paleta de colores de Envisage.

4. **[Referencia de Maptek Python SDK (`MAPTEK_PYTHON_SDK.md`)](./MAPTEK_PYTHON_SDK.md)**
   * Catálogo completo de clases y métodos de `maptek.vulcan` y `maptek.vulcan_gui` (Python 3.5.2 embebido).
   * Comparativa y equivalencias con **Maptek Python SDK 2.0** (`mapteksdk.project`, `mapteksdk.data`).
   * Ejemplos cortos y certeros de código listos para usar con `vulcan_execute_code`.

---

## Fuentes Oficiales de Referencia
* [Maptek Vulcan Online Help](https://help.maptek.com/vulcan/2026.1/topics/Master/index.htm)
* [Maptek Python SDK 2.0 Help](https://help.maptek.com/mapteksdk/2.0/topics/home.htm)

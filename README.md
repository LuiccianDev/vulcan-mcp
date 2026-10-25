# Vulcan MCP (Maptek Vulcan 12 Desktop)

Conecta **Maptek Vulcan 12 Desktop** con asistentes de Inteligencia Artificial (Claude Desktop, Cursor, VS Code, Claude Code, etc.) mediante el **Model Context Protocol (MCP)**.

Inspirado en la arquitectura modular de `qgis-mcp`, pero diseñado como **proyecto independiente** y adaptado a las particularidades reales del SDK de Maptek Vulcan 12 (`maptek.vulcan` y `maptek.vulcan_gui` sobre Python 3.5.2).

---

## Arquitectura

```text
Agente IA (Claude / Cursor)
   ↕ Protocolo MCP (9 Herramientas Maestras + Imágenes JPEG optimizadas)
Servidor Externo (src/vulcan_mcp/server.py — Python 3.11+ / FastMCP)
   ↕ Socket TCP (127.0.0.1:9877, Framing uint32 + Token opcional)
Listener Interno en Vulcan (vulcan_listener/server.py — Python 3.5 compatible)
   ↕ Maptek Vulcan SDK (block_model, triangulation, dgd, isisdb, vulcan_gui)
```

---

## Catálogo de Herramientas Maestras (Master Tools)

| Herramienta MCP | Dominio | Acciones Incluidas (`action=`) |
| :--- | :--- | :--- |
| **`vulcan_system`** | Sistema y Proyecto | `ping`, `project_info`, `capabilities` |
| **`vulcan_block_model`** | Modelos de Bloques (`.bmf`) | `list`, `info`, `query_xyz`, `stats` (ley media, tonelaje, cutoff) |
| **`vulcan_triangulation`** | Superficies y Sólidos (`.00t`/`.tri`) | `list`, `info` (volumen, caras, nodos), `elevation`, `load`, `unload` |
| **`vulcan_design`** | Diseño CAD 3D (`.dgd.isis`) | `list_dbs`, `list_layers`, `layer_info`, `load_layer`, `create_polyline` |
| **`vulcan_drillholes`** | Sondajes ISIS (`.dhd.isis`) | `list_dbs`, `schema`, `holes`, `hole`, `high_grade` |
| **`vulcan_legend`** | Leyendas Envisage (`.scd`) | `list`, `inspect`, `update` (con backup `.bak`), `restore` |
| **`vulcan_screenshot`** | Captura Visual 3D | Captura JPEG redimensionada (`max_width=800`, `quality=70`) para bajo consumo de tokens |
| **`vulcan_canvas`** | Interfaz y Macros | `macro`, `report` |
| **`vulcan_execute_code`** | Scripting PyVulcan | Ejecución de código Python directo con `vulcan` y `vulcan_gui` precargados |

---

## Uso Rápido

### 1. Iniciar el Listener dentro de Maptek Vulcan 12
1. Abre tu proyecto minero en **Maptek Vulcan 12 Desktop**.
2. Ve a **File > Python Script**.
3. Selecciona:
   `C:\Users\DAVID\Desktop\WorksSpacesCoding\vulcan-mcp\vulcan_listener\server.py`
4. Marca **"Run in shell window"** y haz clic en **OK**.

### 2. Configurar tu Cliente MCP (Claude / Cursor / VS Code)

```json
{
  "mcpServers": {
    "vulcan": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\Users\\DAVID\\Desktop\\WorksSpacesCoding\\vulcan-mcp",
        "vulcan-mcp-server"
      ]
    }
  }
}
```

### 3. Seguridad por Token (Opcional)
Configura la variable de entorno de usuario en Windows una sola vez:
```powershell
[Environment]::SetEnvironmentVariable("VULCAN_MCP_TOKEN", "tu-clave-secreta", "User")
```
Tanto Vulcan como el servidor MCP la leerán automáticamente sin necesidad de poner contraseñas en archivos `.json`.

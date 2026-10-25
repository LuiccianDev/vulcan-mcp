# Guía Operativa y Reglas de Desarrollo: Vulcan MCP

Este repositorio implementa el Model Context Protocol (MCP) para conectar Maptek Vulcan 12 Desktop con agentes de Inteligencia Artificial.

## 1. Arquitectura y Entorno en Dos Procesos
- **Plugin Interno (`plugin/`)**: Corre dentro del proceso de Maptek Vulcan 12 en su intérprete embebido de **Python 3.5.2**.
  - **Prohibido usar f-strings (`f"..."`) ni type annotations** dentro de `plugin/` (Python 3.5 no las soporta).
  - Los scripts se ejecutan de forma síncrona en el hilo principal de Vulcan para preservar la seguridad del contexto gráfico OpenGL de Envisage.
- **Servidor MCP Externo (`src/vulcan_mcp/`)**: Corre fuera de Vulcan en **Python 3.11+** (`FastMCP` + Pydantic v2).
- **Transporte**: Socket TCP local en `127.0.0.1:9877` con framing binario `uint32` (big-endian).

## 2. Orden Estricto de Ejecución
1. **PASO 1 (Siempre primero)**: Iniciar el plugin en Maptek Vulcan:
   `File > Python Script > plugin/server.py` (marcando *"Run in shell window"*).
2. **PASO 2 (Después)**: Iniciar o conectar el cliente de IA (Claude Desktop, Cursor, Antigravity) con `uvx` o `uv run`.

## 3. Seguridad y Filosofía Cero `.env`
- **Sin archivos `.env`**: No crear archivos `.env` en el repositorio para evitar exponer contraseñas en Git y asegurar compatibilidad directa con `uvx`.
- **Token Opcional en Localhost / Obligatorio en No-Loopback**:
  - En `127.0.0.1` el token es opcional (modo abierto por defecto).
  - Si `VULCAN_MCP_HOST` no es loopback (`!= 127.0.0.1`), el servidor **se niega a iniciar sin token**.
- **Gestión en Windows**:
  - Guardar permanentemente: `[System.Environment]::SetEnvironmentVariable('VULCAN_MCP_TOKEN', $token, 'User')`
  - Eliminar / Revocar: `[System.Environment]::SetEnvironmentVariable('VULCAN_MCP_TOKEN', $null, 'User')`

## 4. Ejecución de Pruebas y uv
- **Cero gestión manual de venvs**: Usar siempre `uv`.
- **Bandera `--no-sync` en Windows**: Al ejecutar pruebas (`uv run --no-sync pytest tests/test_vulcan_mcp.py -v`), usar `--no-sync` para evitar errores de archivo bloqueado en Windows (`vulcan-mcp-server.exe`) si el servidor MCP está activo.
- **Pruebas en Vivo**: `tests/test_live.py` requiere `BypassSandbox: true` para acceder al puerto `127.0.0.1:9877`.

## 5. Manejo del SDK de Vulcan (`maptek.vulcan`)
- **Diálogos Modales**: Si un comando se detiene por timeout, verificar si Vulcan Desktop tiene una ventana emergente abierta en pantalla (estas bloquean el hilo de Python hasta que el usuario hace clic en OK).
- **Límite Gráfico 3D**: Al mostrar sondajes o polilíneas temporales (`vg.temp_object`), restringir la cantidad a un máximo prudente ($\le 300$ segmentos).
- **Sondajes Bilingües**: En bases de datos ISIS (`.dhd.isis`), contemplar campos en español (`COLLARES`, `LEYES`, `BUZ`, `BUZAMIENTO`, `FROM`, `DESDE`).
- **Hot-Reload**: Los módulos en `plugin/handlers/` pueden recargarse en caliente en Vulcan mediante `vulcan_execute_code` con `importlib.reload(modulo)`.

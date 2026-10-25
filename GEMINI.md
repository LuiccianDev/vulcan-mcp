# Pautas de Desarrollo y Operación: Vulcan MCP

Consulta las reglas maestras completas del workspace en [AGENTS.md](./AGENTS.md).

## 1. Gestión de Entornos y Dependencias (uv)
- **Cero gestión manual de venvs**: Nunca crear ni activar entornos virtuales manualmente con `python -m venv` o `activate`.
- **Instalación/Sincronización**: Usar `uv sync`.
- **Ejecución de herramientas y scripts**: Usar siempre `uv run <comando>` (ej: `uv run --no-sync pytest tests/test_vulcan_mcp.py -v`). Usar `--no-sync` en Windows si el servidor MCP está corriendo para evitar error de archivo bloqueado.

## 2. Conectividad en Vivo con Maptek Vulcan 12
- **Socket TCP local**: El plugin interno de Vulcan escucha en `127.0.0.1:9877` corriendo desde `plugin/server.py`.
- **Sandbox en Windows**: Para comunicarse con el proceso de escritorio de Vulcan, ejecutar los comandos de prueba con `BypassSandbox: true` para permitir acceso al puerto de red local.
- **Diálogos Modales**: Si un comando se detiene por timeout, verificar si la interfaz de Vulcan Desktop tiene una ventana emergente abierta (estas bloquean el hilo principal de Python de Vulcan).
- **Orden de Inicio**: Paso 1: Levantar siempre primero `plugin/server.py` en Vulcan. Paso 2: Conectar el cliente de IA.

## 3. Manejo de Datos Mineros y SDK de Vulcan
- **Bases de datos ISIS en español**: Los campos de inclinación/survey admiten `BUZ` y `BUZAMIENTO`; profundidad admite `FROM` y `DESDE`.
- **Límite de visualización 3D**: Limitar siempre la cantidad de segmentos gráficos temporales generados en el viewport de Envisage (`vg.temp_object`) a un máximo prudente (ej. <= 300) para no sobrecargar el hilo gráfico de Vulcan.
- **Hot-Reload**: Los handlers pueden recargarse en caliente en el intérprete de Vulcan usando `execute_code` con `importlib.reload(modulo)` sin reiniciar el servidor en Vulcan.

## 4. Pruebas y Verificación
- **Pruebas unitarias**: `uv run --no-sync pytest tests/test_vulcan_mcp.py -v`
- **Pruebas de integración en vivo**: `uv run --no-sync pytest tests/test_live.py -v` (con Vulcan y listener activos).

# Reglas del Plugin Vulcan MCP

## Interacción con Maptek Vulcan 12 Desktop
- **Gestión con `uv`**: Todas las invocaciones de Python y tests del servidor deben realizarse a través de `uv run`.
- **Modales en Vulcan**: Si una llamada a una herramienta MCP se detiene por timeout, verificar si la interfaz de Maptek Vulcan Desktop muestra un cuadro de diálogo modal emergente (estos bloquean el hilo principal de Python de Vulcan hasta que el usuario hace clic en OK).
- **Límite de visualización 3D**: Al invocar `vulcan_drillholes` con la acción `display`, restringir la cantidad de elementos o usar `limit` moderado (<= 300 segmentos) para evitar congelar el hilo gráfico OpenGL de Envisage.
- **Sondajes en español**: En bases de datos ISIS (`.dhd.isis`), las tablas y columnas comúnmente están en español (`BUZ`, `BUZAMIENTO`, `FROM`, `DESDE`, `LEYES`, `COLLARES`, `DIRECCIONES`).
- **Capturas de pantalla 3D**: Utilizar `vulcan_screenshot` para validar visualmente la escena 3D en Envisage tras cargar capas CAD, triangulaciones o modelos de bloques.

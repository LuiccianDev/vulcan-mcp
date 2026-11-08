# Vulcan MCP Plugin Rules

## Interaction with Maptek Vulcan 12 Desktop
- **Managed with `uv`**: All Python invocations, server commands, and tests must run via `uv run`.
- **Vulcan Modal Dialogs**: If an MCP tool call halts or times out, check whether Maptek Vulcan Desktop has an open modal popup window (these freeze Vulcan's main Python thread until the user clicks OK or Cancel).
- **3D Graphics Limit**: When calling `vulcan_drillholes` with the `display` action, restrict the number of rendered items or use a moderate `limit` ($\le 300$ segments) to avoid freezing Envisage's OpenGL thread.
- **Bilingual Drillholes**: In ISIS databases (`.dhd.isis`), support both English and Spanish table and column names (`COLLARS/COLLARES`, `ASSAYS/LEYES`, `DIP/BUZ/BUZAMIENTO`, `FROM/DESDE`, `TO/HASTA`).
- **3D Screenshots**: Use `vulcan_screenshot` to visually inspect and validate Envisage's 3D scene after loading CAD layers, triangulations, or block models.
- **Dynamic Port & Host Binding**: Socket defaults to `127.0.0.1:9877`. If port 9877 is occupied or multiple Vulcan sessions run concurrently, configure custom ports dynamically via `VULCAN_MCP_PORT` without code modifications.

## Knowledge Graph & Architectural Navigation
- **Graph-First Navigation**: Always consult `graphify-out/wiki/index.md` or Graphify MCP tools (`query_graph`, `shortest_path`, `god_nodes`) before reading large source files across `src/vulcan_mcp/` and `vulcan_listener/handlers/`.
- **Zero-Token Maintenance**: Whenever domain handlers in `vulcan_listener/handlers/` or core server files in `src/vulcan_mcp/` are modified, keep the graph fresh:
  ```powershell
  uvx --from graphifyy graphify update .
  ```

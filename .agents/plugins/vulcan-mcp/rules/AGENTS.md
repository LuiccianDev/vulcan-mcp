# Vulcan MCP Plugin Rules

## Interaction with Maptek Vulcan 12 Desktop
- **Managed with `uv`**: All Python invocations, server commands, and tests must run via `uv run`.
- **Vulcan Modal Dialogs**: If an MCP tool call halts or times out, check whether Maptek Vulcan Desktop has an open modal popup window (these freeze Vulcan's main Python thread until the user clicks OK or Cancel).
- **3D Graphics Limit**: When calling `vulcan_drillholes` with the `display` action, restrict the number of rendered items or use a moderate `limit` ($\le 300$ segments) to avoid freezing Envisage's OpenGL thread.
- **Bilingual Drillholes**: In ISIS databases (`.dhd.isis`), support both English and Spanish table and column names (`COLLARS/COLLARES`, `ASSAYS/LEYES`, `DIP/BUZ/BUZAMIENTO`, `FROM/DESDE`, `TO/HASTA`).
- **3D Screenshots**: Use `vulcan_screenshot` to visually inspect and validate Envisage's 3D scene after loading CAD layers, triangulations, or block models.

## Knowledge Graph & Architectural Navigation
- **Graph-First Navigation**: Always consult `graphify-out/wiki/index.md` or Graphify MCP tools (`query_graph`, `shortest_path`, `god_nodes`) before reading large source files across `src/vulcan_mcp/` and `plugin/handlers/`.
- **Zero-Token Maintenance**: Whenever domain handlers in `plugin/handlers/` or core server files in `src/vulcan_mcp/` are modified, keep the graph fresh:
  ```powershell
  uvx --from graphifyy graphify update .
  ```

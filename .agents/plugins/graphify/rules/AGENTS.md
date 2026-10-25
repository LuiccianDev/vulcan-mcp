# Graphify Knowledge Graph Rules for Vulcan MCP

This project maintains a persistent knowledge graph in `graphify-out/` mapping the two-process architecture between the external FastMCP server (`src/vulcan_mcp/`) and Maptek Vulcan 12 Desktop's embedded handlers (`plugin/handlers/`).

## Assistant Guidelines:

1. **MCP Priority for Architecture Queries**:
   - Before executing recursive file searches or heavy string grepping across the repository, always query the Graphify MCP tools (`query_graph`, `get_node`, `get_neighbors`, `shortest_path`, or `god_nodes`).
   - This provides immediate dependency tracing between FastMCP tools and Vulcan Python 3.5.2 handlers while minimizing LLM token consumption.

2. **Navigation & Exploration**:
   - Consult `graphify-out/wiki/index.md` for a domain-by-domain overview of the codebase before reading entire source files.
   - Use `graphify-out/GRAPH_REPORT.md` to identify central architectural hubs (*God Nodes*) and module clusters.

3. **Maintenance & Deterministic Updates**:
   - When creating or modifying domain handlers in `plugin/handlers/`, core protocol in `src/vulcan_mcp/`, or documentation in `docs/`, update the knowledge graph:
     ```powershell
     uvx --from graphifyy graphify update .
     ```
   - This keeps `graphify-out/graph.json` and `graphify-out/GRAPH_REPORT.md` in sync deterministically with zero API token cost.

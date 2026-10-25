# Graphify Knowledge Graph (`graphify`)

Local integration of the **Graphify MCP Server** for deterministic knowledge graph analysis, dependency mapping, and token-efficient architectural navigation in **Vulcan MCP**.

---

## Package Contents

- **MCP Server Configuration (`mcp_config.json`)**:
  - `graphify`: Serves `graphify-out/graph.json`, exposing `query_graph`, `get_node`, `get_neighbors`, `get_community`, `god_nodes`, `graph_stats`, and `shortest_path`.
- **Operational Rules (`rules/AGENTS.md`)**:
  - Directs AI assistants to query the graph before performing brute-force grepping or recursive file reading.
  - Deterministic maintenance workflow: `uvx --from graphifyy graphify update .` (0 API token cost).
- **Skills (`skills/graphify/`)**:
  - Complete workflow for knowledge graph generation, graph queries, wiki export, and architectural explanations.

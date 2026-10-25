# Development and Operational Guidelines: Vulcan MCP

Refer to the master workspace rules in [AGENTS.md](./AGENTS.md).

## 1. Environment & Dependency Management (uv)
- **Zero manual virtualenv management**: Never create or activate virtual environments manually with `python -m venv` or `activate`.
- **Install/Sync**: Use `uv sync`.
- **Tool execution**: Always run commands through `uv run <command>` (e.g., `uv run --no-sync pytest tests/test_vulcan_mcp.py -v`). Use `--no-sync` on Windows if the MCP server is active to prevent file-lock issues.

## 2. Live Connectivity with Maptek Vulcan 12
- **Local TCP Socket**: The internal Vulcan plugin listens on `127.0.0.1:9877` via `plugin/server.py`.
- **Windows Sandbox**: To communicate with Vulcan Desktop, execute test commands with `BypassSandbox: true` to access the local network port.
- **Modal Dialogs**: If an operation times out, check if Maptek Vulcan Desktop has an active popup dialog (these suspend Vulcan's main Python thread).
- **Start Order**: Step 1: Always launch `plugin/server.py` in Vulcan first. Step 2: Connect the AI client.

## 3. Mining Data & Vulcan SDK
- **Bilingual ISIS Databases**: Support both Spanish and English survey fields (`BUZ`/`DIP`, `BUZAMIENTO`, `FROM`/`DESDE`, `TO`/`HASTA`, `COLLARES`/`COLLARS`, `LEYES`/`ASSAYS`).
- **3D Graphics Limit**: Always restrict temporary graphics segments (`vg.temp_object`) in Envisage to a safe limit ($\le 300$) to avoid graphics lag.
- **Hot-Reload**: Handlers can be hot-reloaded dynamically using `execute_code` with `importlib.reload(module)` without restarting Vulcan.

## 4. Testing & Verification (3 Layers)
- **Layer 1 (Unit & AST)**: `uv run --no-sync pytest tests/test_vulcan_mcp.py -v` (offline, validates Python 3.5 in plugin/)
- **Layer 2 (Mock Harness & Eval)**: `uv run --no-sync pytest tests/test_mcp_tools.py tests/test_agent_eval.py -v` (offline, emulates Vulcan socket)
- **Layer 3 (Live Integration)**: `uv run --no-sync pytest tests/test_live.py -v` (with active Vulcan Desktop and listener)
- **Quality Checks**:
  - `uv run --no-sync ruff check .`
  - `uv run --no-sync ruff format --check .`
  - `uv run --no-sync mypy src/`
  - `uv run --no-sync pytest tests/test_vulcan_mcp.py tests/test_mcp_tools.py tests/test_agent_eval.py -v --cov=src/vulcan_mcp`

## 5. Graphify Knowledge Graph & Token-Saving Protocol
- **Location**: `graphify-out/` (`graph.json`, `wiki/index.md`, `GRAPH_REPORT.md`).
- **When to Use**: Query Graphify MCP tools (`query_graph`, `shortest_path`, `god_nodes`) or consult `graphify-out/wiki/index.md` before broad recursive searches.
- **Maintenance**: Update deterministically via `uvx --from graphifyy graphify update .` after modifying code in `src/vulcan_mcp/` or `plugin/handlers/`.

## 6. Git Commits & Releases (git-release Plugin)
- **No Silent Commits**: Always ask the user before executing `git commit`.
- **Post-Task Prompt**: Present proposed Conventional Commit and await user approval.
- **Autonomous Release**: Inspect Git history against previous tag to recommend SemVer bumps.


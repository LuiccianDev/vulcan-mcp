# Operating Guidelines & Development Rules: Vulcan MCP

This repository implements the Model Context Protocol (MCP) to connect Maptek Vulcan 12 Desktop with Artificial Intelligence agents.

## 1. Two-Process Architecture & Environments
- **Internal Plugin (`plugin/`)**: Runs inside the Maptek Vulcan 12 process in its embedded **Python 3.5.2** interpreter.
  - **Strictly prohibited:** Do NOT use f-strings (`f"..."`) or type annotations inside `plugin/` (Python 3.5 does not support them).
  - Scripts execute synchronously on Vulcan's main thread to preserve the integrity of the Envisage OpenGL graphics context.
- **External MCP Server (`src/vulcan_mcp/`)**: Runs outside Vulcan in **Python 3.11+** (`FastMCP` + Pydantic v2).
- **Transport**: Local TCP socket on `127.0.0.1:9877` with binary `uint32` big-endian framing.

## 2. Strict Execution Order
1. **STEP 1 (Always First)**: Launch the plugin in Maptek Vulcan:
   `File > Python Script > plugin/server.py` (checking *"Run in shell window"*).
2. **STEP 2 (Afterwards)**: Launch or connect the AI client (Claude Desktop, Cursor, Antigravity) with `uvx` or `uv run`.

## 3. Security & Zero `.env` Philosophy
- **No `.env` Files**: Do NOT create `.env` files in the repository to prevent committing plain-text secrets and ensure direct compatibility with `uvx`.
- **Optional Token on Localhost / Mandatory on Non-Loopback**:
  - On `127.0.0.1`, token authentication is optional (open localhost mode by default).
  - If `VULCAN_MCP_HOST` is non-loopback (`!= 127.0.0.1`), the server **strictly refuses to start without a token**.
- **Windows Token Management**:
  - Persist token: `[System.Environment]::SetEnvironmentVariable('VULCAN_MCP_TOKEN', $token, 'User')`
  - Remove / Revoke: `[System.Environment]::SetEnvironmentVariable('VULCAN_MCP_TOKEN', $null, 'User')`

## 4. Test Harness & Code Quality
- **Zero Manual venv Management**: Always use `uv`.
- **`--no-sync` Flag on Windows**: When running test or quality commands (`uv run --no-sync ...`), pass `--no-sync` to avoid Windows file-lock errors on `vulcan-mcp-server.exe` while the MCP server process is active.
- **3-Layer Test Structure**:
  1. **Layer 1: Unit & AST (`tests/test_vulcan_mcp.py`)**:
     Validates strict Python 3.5.2 compatibility (f-string prohibition in `plugin/`), domain registration, SCD parsing, and token isolation.
     `uv run --no-sync pytest tests/test_vulcan_mcp.py -v`
  2. **Layer 2: Mock Test Harness & Agent Evaluation (`tests/test_mcp_tools.py`, `tests/test_agent_eval.py`)**:
     Emulates Vulcan 12's socket listener in-memory using `MockVulcanServer` without requiring Vulcan Desktop open. Validates all 9 FastMCP tools and multi-step geological audit scenarios, cutoffs, and 3D graphics safeguards ($\le 300$ segments).
     `uv run --no-sync pytest tests/test_mcp_tools.py tests/test_agent_eval.py -v`
  3. **Layer 3: Live Integration (`tests/test_live.py`)**:
     Requires Maptek Vulcan 12 Desktop running with `plugin/server.py` active and `BypassSandbox: true` permission to reach local port 9877.
     `uv run --no-sync pytest tests/test_live.py -v -s`
- **Standard Quality & Linting Commands**:
  - Linter: `uv run --no-sync ruff check .`
  - Formatter: `uv run --no-sync ruff format --check .` (or `ruff format .` to format)
  - Type checking: `uv run --no-sync mypy src/`
  - Full offline suite: `uv run --no-sync pytest tests/test_vulcan_mcp.py tests/test_mcp_tools.py tests/test_agent_eval.py -v --cov=src/vulcan_mcp`

## 5. Maptek Vulcan SDK (`maptek.vulcan`) Handling
- **Modal Dialogs**: If an MCP tool call halts on timeout, check whether Maptek Vulcan Desktop has an active popup dialog on screen (modal windows block Vulcan's Python thread until the user clicks OK or Cancel).
- **3D Graphics Limit**: When displaying drillholes or temporary polylines (`vg.temp_object`), always restrict the quantity to a safe limit ($\le 300$ segments).
- **Bilingual Drillhole Databases**: In ISIS databases (`.dhd.isis`), support both English and Spanish field names (`COLLARES/COLLARS`, `LEYES/ASSAYS`, `BUZ/DIP`, `BUZAMIENTO`, `FROM/DESDE`, `TO/HASTA`).
- **Hot-Reload**: Modules in `plugin/handlers/` can be hot-reloaded inside Vulcan via `vulcan_execute_code` with `importlib.reload(module)`.

## 6. Graphify Knowledge Graph & Token-Saving Protocol
The repository maintains a persistent knowledge graph in `graphify-out/` to enable rapid, token-efficient architectural navigation without broad file reading.

### Decision Matrix: When to Use Graphify vs. Standard Tools
| Scenario / User Intent | Primary Action (Token-Efficient) | Avoid / Secondary |
| :--- | :--- | :--- |
| **Architectural / Flow Queries** ("How does X call Y?", "Trace data flow from FastMCP to Envisage") | Use Graphify MCP tools (`query_graph`, `shortest_path`, `get_node`) or inspect `graphify-out/wiki/index.md`. | Do NOT dump full source files or run broad recursive greps. |
| **High-Level System Overview / Hubs** ("What are the main modules and God Nodes?") | Check `graphify-out/GRAPH_REPORT.md` and call `god_nodes`. | Do NOT inspect raw directories file by file. |
| **Targeted Code Modifications** (Editing an identified function or bug fix) | Read ONLY the specific function or line range in the target file. | Do NOT read unrelated sibling files when the graph already provided context. |
| **Post-Edit Maintenance** (After adding/editing handlers in `plugin/` or tools in `src/`) | Run deterministic update: `uvx --from graphifyy graphify update .` (0 token cost). | Do NOT leave `graphify-out/` outdated. |

## 7. Git Commit & Release Protocol (No Silent Commits)
- **Plugin Integration**: Managed via `.agents/plugins/git-release/`.
- **Strict Prohibition**: The assistant MUST NEVER execute `git commit` silently without asking the user.
- **Post-Task Confirmation**: After verifying changes and automated tests, the assistant must always ask:
  *"Would you like me to commit these changes now (`git commit -m '...'`) or keep working?"*
- **Autonomous Release Inspection**: When the user requests a release, inspect `git describe --tags --abbrev=0` and `git diff` against the last tag to recommend `PATCH`, `MINOR`, or `MAJOR` without asking the user to summarize what was done.


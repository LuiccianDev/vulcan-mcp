# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]


---

## [0.5.1] - 2026-11-16
### Fixed
- **Triangulation `cut_fill` & `profile` Sentinel Filtering**: Extracted shared `_sample_elevation()` in `vulcan_listener/handlers/triangulations.py` to skip `None`, `NaN`, `Inf`, and Vulcan `-9999.0` no-data values instead of corrupting cut/fill volumes.
- **Timeout & Tool Annotation Safety**: Set `timeout=TIMEOUT_LONG` on `vulcan_triangulation` for dense `cut_fill` grids and updated `vulcan_system` to `read_only_hint=False` because `reload` mutates live handlers.
- **Metadata & Token Lookup Consolidation**: Centralized `get_listener_meta()` in `vulcan_listener/handlers/common.py`, replaced hardcoded `RELOADABLE_MODULES` with dynamic `sys.modules` discovery in `system.py`, and removed the stale module-level `TOKEN` snapshot in `vulcan_listener/server.py`.

### Changed
- **CLI & Boundary Architecture**: Extracted CLI flags (`build_cli_parser`, `run_health_check`, `main`) into `src/vulcan_mcp/cli.py` and `src/vulcan_mcp/__main__.py` with lazy FastMCP startup, and wired `validate_action_response` + `ListenerEnvelope` into `server._send()`.
- **Drillholes Subpackage**: Split `vulcan_listener/handlers/drillholes.py` into `vulcan_listener/handlers/drillholes/` (`__init__.py`, `_isis.py`, `_display.py`, `_analytics.py`) with Python 3.5.2 compatibility and reload-safe `_ACTIVE_TEMP_OBJECTS`.


---

## [0.5.0] - 2026-11-16
### Added
- **CLI Diagnostics & Shared HMAC Token Auth**:
  - Added `--help`, `--version`, `--check` (live TCP health check comparing `mcp_version` vs. `listener_version`), and `--generate-token` (`~/.vulcan_mcp/token`) in `src/vulcan_mcp/server.py` and `protocol.py`.
  - Added `vulcan_listener/__init__.py`, `listener_version`/`protocol_version`/`domains` in `system.ping`, `system.reload` for in-place handler hot-reloading, and `~/.vulcan_mcp/token` fallback in `vulcan_listener/server.py`.
- **New Mining & Engineering Actions**:
  - `vulcan_drillholes` (`action="stats"`): descriptive and length-weighted interval statistics (`min`, `max`, `mean`, `weighted_mean`, `std_dev`, `p50`, `p90`) with `DrillholeStatsResponse`.
  - `vulcan_triangulation` (`action="cut_fill"`): 2D grid cut/fill/net volume comparison between two surfaces with `CutFillResponse`.

### Changed
- **Minimalist Release Packaging**: Bundled `vulcan_listener.zip` directly in GitHub Releases (`release.yml`), removed `SHA256SUMS.txt`, and updated `README.md` and `skills/vulcan-tools-catalog/SKILL.md`.


---

## [0.4.0] - 2026-11-16
### Added
- **Mining Analytics & QA/QC Actions**:
  - `grade_tonnage_curve` in `vulcan_block_model` for multi-cutoff tonnage and mean grade evaluation.
  - `profile` in `vulcan_triangulation` for longitudinal elevation profile sampling (`ProfilePoint`, `ElevationProfileResponse`).
  - `qaqc_validation` in `vulcan_drillholes` for bilingual `.dhd.isis` interval audits (overlaps, sampling gaps, inverted intervals, out-of-range grades) with `QAQCAnomaly` and `DrillholeQAQCResponse`.
- **Typed Response Contracts & Tooling**:
  - Added Pydantic v2 response schemas in `src/vulcan_mcp/models/`.
  - Established root `skills/` catalog and installed `pstack`, `thermos`, and `cursor-team-kit` plugins.

### Fixed
- **Envisage Screenshot Cropping**: Window-bounded screenshot capture via `ctypes.windll.user32` in `vulcan_listener/handlers/canvas.py`.
- **TCP Listener & Client Resilience**: Added `CLIENT_READ_TIMEOUT`, envelope/params guards before `dispatch`, `OSError` handling in `sock.accept()`, and `ConnectionError` retries in `vulcan_listener/server.py` and `VulcanMCPClient`.

### Security
- Bumped `opentelemetry-api` to `1.45.2` resolving `CVE-2026-126360`.




---

## [0.3.4] - 2026-11-08
### Changed
- **Architectural Renaming to `vulcan_listener`**:
  - Renamed embedded Vulcan Desktop component from ambiguous `plugin/` to descriptive `vulcan_listener/`.
  - Updated launch entry point to `File > Python Script > vulcan_listener/server.py`.
  - Updated all test runners, CI workflows, and documentation paths.
- **Strict `src/` Packaging Boundaries**:
  - Configured `[tool.hatch.build.targets.sdist]` in `pyproject.toml` to exclusively bundle `src/vulcan_mcp/` and core metadata (`README.md`, `LICENSE`, `pyproject.toml`), eliminating unnecessary non-code directories from the source distribution.
  - Updated Ruff exclude paths to include `vulcan_listener`.
- **Agent Plugin & Documentation Cleanup**:
  - Removed obsolete `.agents/plugins/vulcan-mcp/mcp_config.json` and `hooks.json`.
  - Updated Antigravity agent definition (`mining-geologist.md`) and workflows to reference `vulcan_listener/server.py`.
  - Ensured 100% English documentation consistency across all files.

---

## [0.3.3] - 2026-11-07
### Added
- **Dynamic Host, Port & Token Ergonomics**:
  - Aligned `VulcanMCPClient` constructor with `AutoCADGatewayClient` from `autocad-mcp` with full parameter support: `VulcanMCPClient(host=None, port=None, token=None, timeout=TIMEOUT_DEFAULT)`.
  - Added type-safe port casting (`int | str`) and automatic fallback to environment variables (`VULCAN_MCP_HOST`, `VULCAN_MCP_PORT`, `VULCAN_MCP_TOKEN`).
  - Added unit test `test_vulcan_mcp_client_dynamic_configuration` verifying custom parameters and environment variable fallback.

### Changed
- **PyPI Package Documentation Cleanliness**:
  - Removed internal developer CI/CD workflows and release cadence sections from `README.md` to prevent clutter on PyPI.
  - Relocated maintainer release guidelines and version synchronization documentation to `CONTRIBUTING.md`.
  - Added quickstart guidance for configuring custom ports dynamically via `"env": {"VULCAN_MCP_PORT": "9878"}` in AI client JSON configurations when port 9877 is in use.

---

## [0.3.2] - 2026-11-07
### Changed
- **PyPI & Documentation Streamlining**:
  - Removed broken local image reference (`./assets/readme-logo.jpg`) that failed to render on PyPI.
  - Added official PyPI release badge with direct links.
  - Converted relative header links to canonical GitHub URLs to eliminate 404 errors on PyPI.
  - Streamlined `README.md` by eliminating the 33-line ASCII file tree and internal statement coverage table.
  - Updated architecture diagrams to highlight `uvx luiccian-vulcan-mcp`.

---

## [0.3.1] - 2026-11-07
### Added
- **PyPI Distribution Package (`luiccian-vulcan-mcp`)**:
  - Registered official package name `luiccian-vulcan-mcp` for frictionless execution with `uvx luiccian-vulcan-mcp`.
  - Added CLI entry point aliases: `luiccian-vulcan-mcp`, `vulcan-mcp-server`, and `vulcan-mcp`.
  - Maintained internal module namespace as `vulcan_mcp` (`src/vulcan_mcp/`).
- **Coordinated Windows-Only GitHub Actions Workflows**:
  - `ci.yml`: 100% Windows runner (`windows-latest`) test matrix for Python 3.11 & 3.12 with path-based triggering (`src/**`, `plugin/**`, `tests/**`, `pyproject.toml`, `uv.lock`) and concurrency cancellation.
  - `security.yml`: CodeQL static analysis and `pip-audit` vulnerability scanning on frozen production dependencies.
  - `release.yml`: Tag-triggered build, SHA-256 checksum generation, and automated GitHub Release asset publishing with concurrency protection.
  - `publish-pypi.yml`: Decoupled PyPI release workflow using OIDC Trusted Publishing (`id-token: write`) and PEP 740 Cryptographic Build Provenance Attestations (`attestations: write`).
- **Autonomous Multi-Target Version Bumper (`scripts/bump_version.py`)**:
  - Single atomic synchronization across `pyproject.toml`, `src/vulcan_mcp/__init__.py`, `.agents/plugins/vulcan-mcp/plugin.json`, `uv.lock`, and `CHANGELOG.md`.
  - Supports `patch`, `minor`, `major`, explicit version strings, and `--dry-run` inspection.
- **Documentation & Diátaxis Additions**:
  - Added Recipe 7 to `docs/HOW_TO_GUIDES.md`: Step-by-step release management, Git tagging, and PyPI publishing.
  - Added CI/CD and Release Cadence chapters to `README.md`.

### Changed
- **Full Project Localization to English**:
  - Converted all documentation, architectural guides, agent system prompts, and plugin READMEs to English.
  - Maintained bilingual ISIS drillhole database field lookups (`COLLARS/COLLARES`, `ASSAYS/LEYES`, `DIP/BUZ`, `FROM/DESDE`, `TO/HASTA`) for Latin American mining compatibility.

---

## [0.3.0] - 2026-10-25

### Added
- **`git-release` Antigravity Plugin**:
  - `release-manager`: Dedicated AI persona for Conventional Commits and SemVer releases.
  - Lifecycle hook (`hooks.json`): Non-blocking `PreInvocation` working tree status check.
  - Skills: `git-commit` (interactive Conventional Commits) and `versioning-and-release` (SemVer 2.0.0 governance).
  - Strict guardrails: No silent commits, autonomous Git diff inspection without memory overhead.
- **Diátaxis Technical Documentation Architecture**:
  - `docs/TUTORIAL_FIRST_STEPS.md`: 15-minute hands-on tutorial for connecting Vulcan 12 Desktop with AI clients.
  - `docs/HOW_TO_GUIDES.md`: 6 problem-oriented recipes (block cutoffs, drillholes, triangulations, CAD polylines, PyVulcan scripting, and modal dialog freezes).
  - `docs/README.md`: Central Diátaxis navigation map across Tutorials, How-To Guides, Reference, and Explanations.
- **Graphify Knowledge Graph Integration**:
  - Persistent knowledge graph in `graphify-out/` mapping two-process FastMCP $\leftrightarrow$ Vulcan Python 3.5.2 architecture.
  - Integration of Graphify MCP tools (`query_graph`, `shortest_path`, `god_nodes`) to explore architecture with minimal token consumption.
  - Dedicated operational rules in `.agents/plugins/graphify/rules/AGENTS.md`.
- **Enriched Package Metadata**:
  - Added PEP 621 author details (`DAVID (LuiccianDev)`), PyPI classifiers, keywords, and repository URLs in `pyproject.toml`.

### Changed
- **Full Project Localization to English**:
  - Translated all user documentation (`README.md`, `docs/`), workspace operating rules (`AGENTS.md`, `GEMINI.md`), specialist agent prompt (`mining-geologist.md`), and plugin skills.
  - Preserved bilingual database field mappings (`COLLARS/COLLARES`, `ASSAYS/LEYES`, `DIP/BUZ`) in drillhole handlers.
- **Hardened `.gitignore`**:
  - Excluded Vulcan interactive session files (`*.wrk`), binary ISIS indices (`*.isix`), backup dumps (`*.bck`, `*.trn`), and local mining models (`*.bmf`, `*.00t`).
  - Excluded `graphify-out/` build artifacts completely to maintain a lightweight Git repository.

---

## [0.2.0] - 2026-10-24

### Added
- **The 9 Master Compound Tools Mode**:
  - `vulcan_system`: Project connectivity, health check, and mining asset inventory.
  - `vulcan_block_model`: Spatial $(X,Y,Z)$ sampling, tonnage, volume, and volume-weighted cutoff estimations over `.bmf` files.
  - `vulcan_triangulation`: Mesh topology audit, solid closure, volume, $Z$ elevation sampling, and point-in-solid verification.
  - `vulcan_design`: CAD layer inspection, planar area ($m^2$), 3D loading, and polyline generation.
  - `vulcan_drillholes`: Relational ISIS queries, high-grade intercept discovery, and 3D desurveyed colored rendering in Envisage.
  - `vulcan_legend`: `.scd` color scheme inspection and updates with automatic `.scd.bak` backup.
  - `vulcan_screenshot`: Native 3D viewport capture compressed to JPEG for multimodal LLM vision.
  - `vulcan_canvas`: Envisage Workbench macro execution and report console messaging.
  - `vulcan_execute_code`: Headless execution of arbitrary Python routines in Vulcan 12's embedded Python 3.5.2 interpreter.
- **3-Layer Automated Testing Harness**:
  - Layer 1: Unit & AST tests validating Python 3.5 compatibility (no f-strings in `plugin/`).
  - Layer 2: In-memory `MockVulcanServer` testing all 9 FastMCP tools and multi-step agent evaluations without Vulcan Desktop open.
  - Layer 3: Live integration suite for active Envisage sessions.
- **Security & Zero `.env` Philosophy**:
  - Constant-time HMAC authentication (`VULCAN_MCP_TOKEN`).
  - Strict refusal to start on non-loopback network bindings without an active token.

---

## [0.1.0] - 2026-10-20

### Added
- Initial proof-of-concept socket listener on `127.0.0.1:9877` using binary `uint32` big-endian framing.
- Basic C++/SWIG data serializer in `plugin/wire.py`.
- Basic prototype handlers for system ping and block model information.

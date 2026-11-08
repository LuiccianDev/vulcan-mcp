# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]




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

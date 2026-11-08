# Maptek Vulcan MCP Plugin (Google Antigravity)

Native **Google Antigravity** plugin located in `.agents/plugins/vulcan-mcp/` to seamlessly integrate **Maptek Vulcan 12 Desktop** into agentic AI pair-programming and mining engineering workflows.

---

## 1. Plugin Architecture & Structure

```text
.agents/plugins/vulcan-mcp/
├── plugin.json                         # Plugin manifest (v0.3.4)
├── README.md                           # This document
├── agents/
│   └── mining-geologist.md             # Resource Geologist & Mine Planning Specialist Agent
├── rules/
│   └── AGENTS.md                       # Persistent rules active when plugin is enabled
└── skills/
    ├── vulcan-tools-catalog/SKILL.md   # 9 MCP Master Tools Catalog
    ├── vulcan-file-formats/SKILL.md    # Format specifications (.bmf, .00t, .dgd.isis, .dhd.isis, .scd)
    ├── vulcan-python-sdk/SKILL.md      # SDK mapping (maptek.vulcan, maptek.vulcan_gui, mapteksdk 2.0)
    └── vulcan-workflow/SKILL.md        # Guided mining workflows (audits, estimation, drillholes, 3D vision)
```

---

## 2. Included Components

1. **Standard PyPI & Client Integration**:
   * Consumed zero-install via `uvx luiccian-vulcan-mcp` (or locally via workspace execution).
   * Fully configurable dynamically via environment variables (`VULCAN_MCP_HOST`, `VULCAN_MCP_PORT`, `VULCAN_MCP_TOKEN`) with zero hardcoding.
2. **Specialized Custom Agent (`agents/mining-geologist.md`)**:
   * **Identifier**: `mining-geologist` (*Vulcan Mining Specialist*).
   * **Capabilities**: Full access to the 9 Vulcan master compound tools, automated connection diagnostics with `vulcan_listener/server.py`, and the 4 specialized domain skills.
3. **4 Progressive Disclosure Skills (`skills/*/SKILL.md`)**:
   * Loaded on demand only when a task requires deep domain context, minimizing LLM context token consumption:
     - `vulcan-tools-catalog`: Schema for all 9 Master Compound Tools.
     - `vulcan-file-formats`: Binary and database file specs.
     - `vulcan-python-sdk`: Python 3.5.2 embedded SDK guardrails and mappings.
     - `vulcan-workflow`: 6 guided mining workflows (connectivity diagnostics, project audits, block models, drillholes, 3D vision, and custom scripting).
4. **Operational Guardrails (`rules/AGENTS.md`)**:
   * Enforces tool execution via `uv`, safe 3D graphics rendering thresholds ($\le 300$ segments), bilingual ISIS database column support (`COLLARS/COLLARES`, `BUZ/DIP`, `FROM/DESDE`), and modal dialog awareness.



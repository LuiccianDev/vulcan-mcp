# Maptek Vulcan MCP Plugin (Google Antigravity)

Native **Google Antigravity** plugin located in `.agents/plugins/vulcan-mcp/` to integrate **Maptek Vulcan 12 Desktop** directly into agentic AI environments.

---

## Plugin Structure

```text
.agents/plugins/vulcan-mcp/
├── plugin.json                         # Official plugin manifest
├── mcp_config.json                     # Automated MCP server launcher via uv
├── hooks.json                          # PreInvocation hook verifying TCP port 9877
├── README.md                           # This document
├── agents/
│   └── mining-geologist.md             # Resource Geologist & Mine Planning Specialist Agent
├── rules/
│   └── AGENTS.md                       # Persistent rules active when plugin is enabled
└── skills/
    ├── vulcan-tools-catalog/SKILL.md   # 9 MCP Master Tools Catalog
    ├── vulcan-file-formats/SKILL.md    # Format specifications (.bmf, .00t, .dgd.isis, .dhd.isis, .scd)
    ├── vulcan-python-sdk/SKILL.md      # SDK mapping (maptek.vulcan, maptek.vulcan_gui, mapteksdk 2.0)
    └── vulcan-workflow/SKILL.md        # Guided mining workflows (audits, estimation, drillholes)
```

---

## Included Components

1. **MCP Server Configuration (`mcp_config.json`)**:
   * Registers the `vulcan` server executing `uv run --directory ${workspaceFolder} vulcan-mcp-server`.
   * Automatically reads `VULCAN_MCP_TOKEN` from the operating system environment if configured.
2. **Specialized Custom Agent (`agents/mining-geologist.md`)**:
   * **Identifier**: `mining-geologist` (*Vulcan Mining Specialist*).
   * **Capabilities**: Full access to the 9 Vulcan master compound tools and the 4 specialized skills.
3. **4 Progressive Disclosure Skills (`skills/*/SKILL.md`)**:
   * Loaded on demand only when a task requires deep domain context to optimize LLM context window tokens.
4. **Health Check Hook (`hooks.json`)**:
   * Prior to each invocation (`PreInvocation`), performs a non-blocking check to verify whether Maptek Vulcan's TCP socket `127.0.0.1:9877` is `ONLINE` or `OFFLINE`.
5. **Operational Rules (`rules/AGENTS.md`)**:
   * Enforces tool execution via `uv run`, safe 3D graphics rendering thresholds ($\le 300$ segments), bilingual ISIS database column support (`COLLARS/COLLARES`, `BUZ/DIP`, `FROM/DESDE`), and modal dialog awareness.

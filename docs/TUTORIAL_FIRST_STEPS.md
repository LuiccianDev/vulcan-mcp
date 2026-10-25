# Tutorial: First Steps with Vulcan MCP

> **Purpose:** A hands-on guide for resource geologists, mining engineers, and software developers connecting Maptek Vulcan 12 Desktop with an AI client for the first time.  
> **Estimated Time:** 10 - 15 minutes.  
> **Outcome:** Launch the service, verify bidirectional communication, and execute your first geological query and 3D screenshot with AI assistance.

---

## Prerequisites

Before starting, make sure you have:
1. **Maptek Vulcan 12 Desktop** installed on 64-bit Windows with an active Envisage license.
2. A mining project loaded in Vulcan (or a working directory containing at least one triangulation `.00t` or block model `.bmf`).
3. An MCP-compatible AI client installed:
   - **Google Antigravity** (recommended),
   - **Claude Desktop**,
   - **Cursor**, or
   - **Claude Code (CLI)**.

---

## Step 1: Start the Listener Plugin inside Vulcan Desktop

The bridge component is a synchronous socket listener running inside Vulcan's embedded Python interpreter (Python 3.5.2).

1. Open your project in **Maptek Vulcan 12 Desktop**.
2. In the top menu, navigate to:  
   **File > Python Script** (or type `py` in Vulcan's command window).
3. In the file picker, select:  
   `plugin/server.py`
4. **Crucial:** Check the box **"Run in shell window"** and click **OK**.
5. A Windows console window will appear displaying:

```text
==============================================================
[Vulcan MCP] Vulcan MCP Listener started on 127.0.0.1:9877
[Vulcan MCP] Working directory: C:\MiningProjects\Deposit_A
[Vulcan MCP] Registered domains: block_model, canvas, design, drillholes, execute_code, legend, system, triangulation
[Vulcan MCP] Token authentication: DISABLED (localhost open mode)
[Vulcan MCP] Keep this window open while using your AI client. Ctrl+C to stop.
==============================================================
```

> [!TIP]
> **Keep this shell window open.** It maintains the active TCP socket between Vulcan and your AI client.

---

## Step 2: Connect your AI Client

With port `127.0.0.1:9877` listening inside Vulcan, connect your AI assistant.

### Option A: In Google Antigravity
If using Antigravity in this workspace, the plugin is loaded automatically. Simply use the chat window.

### Option B: In Claude Desktop / Cursor
Add the following configuration to `claude_desktop_config.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "vulcan": {
      "command": "uvx",
      "args": [
        "--from",
        "https://github.com/LuiccianDev/vulcan-mcp/archive/refs/heads/master.zip",
        "vulcan-mcp-server"
      ]
    }
  }
}
```

---

## Step 3: First Query — System & Connectivity Check

Send your first message to your AI assistant:

```text
Assistant, please verify if you are connected to Maptek Vulcan and tell me which project directory is open.
```

### Behind the Scenes:
The agent calls the `vulcan_system` tool:
```json
{
  "action": "ping"
}
```

### Expected Response:
```json
{
  "connected": true,
  "app": "Maptek Vulcan",
  "python": "3.5.2",
  "vulcan_api": true,
  "project_dir": "C:\\MiningProjects\\Deposit_A"
}
```
The assistant will confirm that the link is live and ready for mining workflows.

---

## Step 4: Rapid Project Inventory

Ask the assistant to explore available mining assets in the active workspace:

```text
Inventory all project files: block models, triangulations, and drillhole databases.
```

The agent runs `vulcan_system(action="project_info")` and summarizes the files:
- **Block Models (`.bmf`):** names and file sizes.
- **Triangulations (`.00t`):** topographic surfaces and geological solids.
- **Drillhole Databases (`.dhd.isis`):** available ISIS databases.

---

## Step 5: Query a Triangulation or Block Model

Perform an actual geological asset inspection:

```text
Inspect the triangulation "topo_surface.00t" and check if it is consistent, its triangle count, and total volume if closed.
```

The agent calls `vulcan_triangulation`:
```json
{
  "action": "info",
  "name": "topo_surface.00t"
}
```

The agent presents the results:
- Node and triangle counts.
- Topological status: whether the mesh is watertight (closed solid) or an open surface.
- 3D centroid $(X, Y, Z)$ and volume in $m^3$.

---

## Step 6: Capture the 3D Viewport in Envisage

To visually confirm what is shown in Vulcan's viewport:

```text
Take a screenshot of Vulcan's 3D viewport to inspect the current camera view.
```

The agent executes `vulcan_screenshot` and embeds the JPEG image directly into the chat conversation.

---

## Summary & Next Steps

🎉 **Congratulations!** You have completed the core lifecycle:
1. Launched the Vulcan 12 listener plugin.
2. Connected your AI client via MCP.
3. Conducted diagnostics, asset audits, and visual inspections in real time.

### Recommended Next Steps:
- For practical recipes (cutoffs, drillhole desurvey, CAD design), read the **[How-To Guides](./HOW_TO_GUIDES.md)**.
- To view parameter specifications for all 9 tools, consult the **[MCP Tools Reference](./MCP_TOOLS_REFERENCE.md)**.
- For protocol and architecture details, explore **[Architecture & Security](./ARCHITECTURE_AND_SECURITY.md)**.

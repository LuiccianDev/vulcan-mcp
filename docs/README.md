# Technical Documentation Center: Vulcan MCP

Welcome to the official documentation for **Vulcan MCP**. This collection is structured according to the **[Diátaxis Framework](https://diataxis.fr/)**, organizing technical information into four distinct quadrants based on user needs:

---

## 🧭 Diátaxis Navigation Map

```text
               PRACTICAL (Learning by Doing)   THEORETICAL (Understanding)
                       │                              │
STEP-BY-STEP           ▼                              ▼
(Learning-oriented)┌─────────────────────────┐    ┌─────────────────────────┐
                   │    🎓 TUTORIALS         │    │    💡 EXPLANATION       │
                   │                         │    │                         │
                   │ First Steps             │    │ Architecture, SWIG      │
                   │ From 0 to 1st analysis  │    │ Memory & Zero .env      │
                   └─────────────────────────┘    └─────────────────────────┘
                       │                              │
WORK & MACHINERY       ▼                              ▼
(Task-oriented)    ┌─────────────────────────┐    ┌─────────────────────────┐
                   │  🛠️ HOW-TO GUIDES       │    │   📖 REFERENCE          │
                   │                         │    │                         │
                   │ Mining Recipes: Blocks, │    │ MCP Tools Catalog,      │
                   │ Drillholes, CAD & Dialog│    │ Vulcan SDK & File Types │
                   └─────────────────────────┘    └─────────────────────────┘
```

---

## 1. 🎓 Tutorials
*Learning-oriented, practical step-by-step guides for newcomers.*

* **[Tutorial: First Steps with Vulcan MCP](./TUTORIAL_FIRST_STEPS.md)**  
  A 15-minute hands-on lesson: starting the listener plugin inside Vulcan 12 Desktop, connecting the AI client, auditing project assets, and capturing the first 3D screenshot in Envisage.

---

## 2. 🛠️ How-To Guides
*Problem-oriented recipes for solving specific mining, geological, and operational tasks.*

* **[Vulcan MCP How-To Guides](./HOW_TO_GUIDES.md)**  
  Step-by-step practical recipes:
  1. *Calculate tonnage and mean grade with cutoff on block models (`.bmf`).*
  2. *Discover high-grade intercepts and display drillholes in 3D without freezing Envisage ($\le 300$ segments).*
  3. *Validate topological consistency, solid closure, and sample $Z$ elevations on triangulations (`.00t`).*
  4. *Measure planar bench areas and digitize CAD polylines (`.dgd.isis`).*
  5. *Execute Python automation scripts and hot-reload handlers (`vulcan_execute_code`).*
  6. *Diagnose and resolve freezes caused by modal dialog popups in Vulcan Desktop.*

---

## 3. 📖 Technical Reference
*Information-oriented technical descriptions, parameter catalogs, and data specifications.*

* **[Master MCP Tools Reference (`MCP_TOOLS_REFERENCE.md`)](./MCP_TOOLS_REFERENCE.md)**  
  Exhaustive catalog with input parameters, defaults, error structures, and real JSON output schemas for all 9 Master Tools.

* **[Maptek Vulcan Python SDK Reference (`MAPTEK_PYTHON_SDK.md`)](./MAPTEK_PYTHON_SDK.md)**  
  Classes and methods in `maptek.vulcan` and `maptek.vulcan_gui` for embedded Python 3.5.2, including mapping tables to **Maptek Python SDK 2.0**.

* **[Vulcan File Formats Specification (`VULCAN_FILE_FORMATS.md`)](./VULCAN_FILE_FORMATS.md)**  
  Structure and specifications of binary `.bmf`, `.00t`, relational ISIS databases (`.dhd.isis`, `.dgd.isis`), `.scd` color legends, and palette mappings.

---

## 4. 💡 Explanation & Architecture
*Understanding-oriented concepts, design decisions, security model, and network protocol.*

* **[Internal Architecture, TCP Protocol & Security (`ARCHITECTURE_AND_SECURITY.md`)](./ARCHITECTURE_AND_SECURITY.md)**  
  Why the two-process architecture exists (Python 3.11+ $\leftrightarrow$ Python 3.5.2), binary `uint32` big-endian framing, C++/SWIG pointer lifecycle, and token security with zero `.env` files.

---

## Official Maptek Resources
* [Maptek Vulcan Online Help](https://help.maptek.com/vulcan/2026.1/topics/Master/index.htm)
* [Maptek Python SDK 2.0 Help](https://help.maptek.com/mapteksdk/2.0/topics/home.htm)

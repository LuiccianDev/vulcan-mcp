---
name: versioning-and-release
description: Standard operating procedure for Semantic Versioning (SemVer 2.0.0), multi-file version synchronization, CHANGELOG.md maintenance, and release tagging in Vulcan MCP.
---

# Versioning & Release Management Skill

Use this skill whenever you are preparing a new release, bumping version numbers, categorizing changes in `CHANGELOG.md`, or verifying multi-file version consistency across **Vulcan MCP**.

---

## 1. Semantic Versioning Specification (SemVer 2.0.0)

Given a version number `MAJOR.MINOR.PATCH`:

1. **`PATCH` (e.g. `0.3.0` $\rightarrow$ `0.3.1`)**:
   - Backward-compatible bug fixes.
   - Internal performance refactors.
   - Documentation typos and small clarifications.
   - Test harness improvements without API changes.

2. **`MINOR` (e.g. `0.3.0` $\rightarrow$ `0.4.0`)**:
   - Adding new FastMCP tools or new actions to existing tools (`vulcan_block_model`, `vulcan_drillholes`, etc.).
   - Adding new mining domain handlers or expanding SDK coverage.
   - Introducing new skills, agent plugins, or major documentation quadrants (Diátaxis).
   - Any backward-compatible feature addition.

3. **`MAJOR` (e.g. `0.3.0` $\rightarrow$ `1.0.0`)**:
   - First official production release with stable public API.
   - Breaking changes in tool argument names, required parameters, or return formats.
   - Incompatible changes to the TCP binary framing protocol (`wire.py` / `protocol.py`).
   - Removal or replacement of existing tools.

---

## 2. Multi-File Version Synchronization Checklist

When bumping the version, **all three files below must be updated simultaneously** to prevent version drift:

| Target File | Setting / Variable | Example |
| :--- | :--- | :--- |
| **`pyproject.toml`** | `[project] version = "..."` | `version = "0.3.0"` |
| **`src/vulcan_mcp/__init__.py`** | `__version__ = "..."` | `__version__ = "0.3.0"` |
| **`.agents/plugins/vulcan-mcp/plugin.json`** | `"version": "..."` | `"version": "0.3.0"` |

---

## 3. `CHANGELOG.md` Maintenance (Keep a Changelog)

Always maintain `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/):

1. Keep an `## [Unreleased]` section at the top for ongoing work.
2. Group changes under standard subheadings:
   - `### Added`: for new features, tools, or skills.
   - `### Changed`: for changes in existing functionality or docs.
   - `### Deprecated`: for soon-to-be removed features.
   - `### Removed`: for now removed features.
   - `### Fixed`: for any bug fixes.
   - `### Security`: in case of vulnerabilities or auth changes.
3. When releasing, rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD` and create a fresh `[Unreleased]` block.

---

## 4. Autonomous Release Inspection Protocol (Git History)

When the user asks to prepare a release:
1. Run `git describe --tags --abbrev=0` to locate the previous tag.
2. Run `git log <last-tag>..HEAD --oneline` and `git diff <last-tag>..HEAD --stat`.
3. Categorize changes automatically and suggest the appropriate bump (`PATCH`, `MINOR`, or `MAJOR`).
4. Present the draft changelog entry and wait for user confirmation.

---

## 5. Git Tagging & Release Command

Once changes are committed:

```powershell
# Create annotated tag
git tag -a v0.3.0 -m "Release v0.3.0: Diátaxis docs, Graphify, test harness, and git-release plugin"

# Push commit and tags to GitHub
git push origin master --tags
```

---

## 6. GitHub CLI (`gh`) Release Operations

To publish an official Release on GitHub with formatted notes and assets without opening the browser:

### Step 1: Pre-Flight Authentication Check
Always verify GitHub CLI authentication before attempting to publish:
```powershell
gh auth status
```
If credentials have expired or need renewal:
```powershell
"github_pat_..." | gh auth login --with-token
gh auth setup-git
```

### Step 2: Extract Scoped Release Notes
Extract only the targeted version section from `CHANGELOG.md` (e.g. `[X.Y.Z]`) to a temporary scratch file or inline string to avoid dumping the entire changelog history into a single release description.

### Step 3: Publish GitHub Release
```powershell
gh release create v0.3.0 `
  --title "Vulcan MCP v0.3.0 - Diátaxis Docs, Graphify & Git-Release Plugin" `
  --notes-file "path/to/release_notes.md"
```

### Step 4: Verification & Inspection
Verify the published release directly from terminal:
```powershell
# View release details and notes
gh release view v0.3.0

# List all repository releases
gh release list
```


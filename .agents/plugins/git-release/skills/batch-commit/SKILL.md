---
name: batch-commit
description: Systematic procedure for grouping multi-file working tree changes into atomic, cohesive commit batches with dedicated Conventional Commit messages.
---

# Atomic Batch Commits Skill

Use this skill whenever a session involves modifications across multiple areas of the project (e.g. core code, tests, documentation, and configuration) and you need to break down the changes into **clean, atomic, and logical commit batches** rather than bundling everything into one monolithic commit.

---

## 1. Core Philosophy of Atomic Commits

An **atomic commit** encapsulates a single logical unit of change. 

### Why Batch Commits?
1. **Bisect & Debugging**: If a bug is introduced, `git bisect` identifies the exact commit responsible without mixing doc fixes or config tweaks.
2. **Review Clarity**: Reviewers and maintainers can evaluate code changes independently from documentation expansions.
3. **Reversibility**: A specific change can be reverted (`git revert <hash>`) cleanly without undoing unrelated work.
4. **Transparent History**: The Git commit log reads as a clear, sequential changelog.

---

## 2. Logical Clustering Taxonomy

When inspecting `git status -s`, cluster files according to the following standard tiers:

| Tier / Cluster | Scope Paths | Commit Type | Example Message |
| :--- | :--- | :--- | :--- |
| **Tier 1: Core & SDK** | `src/vulcan_mcp/`, `plugin/` | `feat(...)`, `fix(...)`, `refactor(...)` | `feat(handlers): add point-in-solid triangulation query` |
| **Tier 2: Tests & Quality** | `tests/` | `test(...)` | `test(harness): expand MockVulcanServer with drillhole mocks` |
| **Tier 3: Documentation** | `docs/`, `README.md`, `CHANGELOG.md` | `docs(...)` | `docs(tutorials): add 15-minute quickstart guide` |
| **Tier 4: Plugins & Agents** | `.agents/`, `skills-lock.json` | `feat(plugins)`, `feat(skills)` | `feat(plugins): introduce git-release plugin and specialist agent` |
| **Tier 5: Configuration** | `pyproject.toml`, `.gitignore`, `uv.lock` | `chore(...)`, `build(...)` | `chore(deps): update packaging metadata and exclude binaries` |

---

## 3. Batch Planning Protocol

When preparing batch commits:

### Step 1: Scan Working Tree
Inspect changed and untracked files:
```powershell
git status --porcelain
```

### Step 2: Formulate the Batch Plan
Group the files into 2 to 4 cohesive batches and present the plan to the user in a clear table:

```markdown
### Proposed Atomic Commit Batches:
1. **Batch 1 (Core)**: `src/vulcan_mcp/server.py`, `plugin/handlers/triangulation.py`
   - *Message*: `feat(triangulation): add point_inside query support`
2. **Batch 2 (Tests)**: `tests/test_mcp_tools.py`
   - *Message*: `test(triangulation): add unit test for point_inside handler`
3. **Batch 3 (Docs)**: `docs/MCP_TOOLS_REFERENCE.md`
   - *Message*: `docs(reference): update triangulation tool schema documentation`
```

### Step 3: Await Confirmation
Always ask the user for confirmation before executing each batch (respecting the **No Silent Commits** guardrail).

---

## 4. Sequential Execution Sequence

For each approved batch in order:

1. **Selective Staging**:
   Stage ONLY the files belonging to that batch:
   ```powershell
   git add <file1> <file2>
   ```

2. **Pre-Commit Verification**:
   If the batch touches code or tests, verify integrity:
   ```powershell
   uv run --no-sync pytest tests/test_vulcan_mcp.py -v
   uv run --no-sync ruff check .
   ```

3. **Commit with Specific Message**:
   ```powershell
   git commit -m "type(scope): description"
   ```

4. **Verify Remaining Working Tree**:
   Run `git status -s` and proceed to the next batch until the working tree is clean.

---

## 5. Strict Guardrails

* **Zero Monolithic Staging (`git add .`)**: When operating in batch commit mode, never run `git add .` or stage all files indiscriminately.
* **Test Isolation**: Run tests after each code batch to ensure each commit in Git history is individually functional and passing tests.

---
name: branch-workflow
description: Operating procedure for feature branch management, standardized branch naming (feat/*, fix/*), master branch protection, and merging/PR workflows.
---

# Feature Branch Workflow Skill

Use this skill whenever you are starting a new feature, bug fix, experimental customization, or refactor in **Vulcan MCP**. This skill ensures the main production branch (`master`) remains stable, protected, and clean by isolating all work in dedicated **Feature Branches**.

---

## 1. Master Branch Protection Principle

The `master` branch represents the stable, releasable baseline.

* **Strict Protection**: Never start developing new tools, complex handlers, or refactors directly on `master`.
* **Isolated Experimentation**: Work in dedicated feature branches so broken tests or incomplete edits never block the main branch.
* **Traceable Integration**: Merging leaves a clear merge history or squash commit summarizing the completed deliverable.

---

## 2. Standardized Branch Naming Taxonomy

Always format branch names using kebab-case with standard prefixes:

| Branch Prefix | When to Use | Example Branch Name |
| :--- | :--- | :--- |
| **`feat/`** | New FastMCP tools, actions, mining handlers, or skills | `feat/drillhole-compositing`, `feat/mesh-boolean` |
| **`fix/`** | Bug fixes, null handling, or Python 3.5 compatibility fixes | `fix/isis-collar-nulls`, `fix/bmf-coordinate-offset` |
| **`refactor/`** | Code cleanup, typing improvements, or internal architecture | `refactor/socket-listener`, `refactor/wire-framing` |
| **`docs/`** | Diátaxis tutorials, guides, and documentation expansions | `docs/tutorial-bench-design`, `docs/api-reference` |
| **`test/`** | Adding unit tests, mock servers, or test harness expansions | `test/mock-drillhole-queries`, `test/legend-scd` |

---

## 3. Interactive Initiation Protocol (Starting Work)

When the user requests a new change or feature (e.g., *"quiero cambiar X"*, *"agrega una función para Y"*):

### Step 1: Detect Work Scope & Propose Branch
Formulate a concise branch name and confirm with the user before touching code:
> *"I understand you want to implement [feature description]. To keep `master` protected and clean, I will create and switch to a dedicated branch: `feat/feature-name`. Shall we proceed?"*

### Step 2: Ensure Baseline is Clean & Up-to-Date
```powershell
# Verify current branch is master
git checkout master

# Verify working tree is clean
git status -s

# Pull latest commits
git pull origin master
```

### Step 3: Create and Switch to Feature Branch
```powershell
git checkout -b feat/<feature-name>
```

---

## 4. Development & Commit Protocol on Branch

1. **Develop Freely**: Implement the code changes, new handlers, or documentation on the feature branch.
2. **Validate**:
   ```powershell
   uv run --no-sync pytest tests/test_vulcan_mcp.py -v
   uv run --no-sync ruff check .
   ```
3. **Commit using Conventional Commits**:
   Follow [`git-commit`](../git-commit/SKILL.md) or [`batch-commit`](../batch-commit/SKILL.md).

---

## 5. Completion & Merging Protocol (Finishing Work)

When the work on the branch is completed and all tests pass (100%), there are two paths to merge:

### Path A: Local Fast-Forward / Merge (Recommended for solo local work)
```powershell
# 1. Switch back to master
git checkout master

# 2. Merge the feature branch
git merge feat/<feature-name>

# 3. Verify tests on master
uv run --no-sync pytest tests/test_vulcan_mcp.py -v

# 4. Push to remote
git push origin master

# 5. Delete the merged feature branch
git branch -d feat/<feature-name>
```

### Path B: GitHub Pull Request via `gh` CLI (Recommended for code review)
```powershell
# 1. Push the feature branch to GitHub
git push -u origin feat/<feature-name>

# 2. Create the Pull Request
gh pr create --title "feat: <feature description>" --body "Closes task. Tested with pytest."

# 3. Merge PR when approved
gh pr merge --squash --delete-branch
```

---

## 6. Practical Example: User Interaction Flow

```
User: "Quiero agregar una función para exportar drillholes a formato CSV"

Assistant (triggers branch-workflow):
1. Proposes branch: "Entendido. Para proteger 'master', crearemos la rama: feat/drillhole-csv-export"
2. Executes: git checkout -b feat/drillhole-csv-export
3. Implements code & tests on the branch.
4. Validates: uv run --no-sync pytest
5. Commits: feat(drillholes): add CSV export action
6. Prompts user: "Trabajo completado y verificado en la rama. ¿Deseas hacer el merge a master o abrir un Pull Request?"
```

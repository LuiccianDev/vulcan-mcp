---
name: git-commit
description: Interactive Conventional Commits manager. Formulates standardized commit messages (feat, fix, docs, refactor, test, chore) from git status/diff, and explicitly requests user approval before committing.
---

# Git Commit Skill (Conventional Commits & Interactive Workflow)

Use this skill whenever you need to prepare, inspect, or execute Git commits following the **Conventional Commits** standard.

---

## 1. Commit Type Taxonomy

| Type | When to Use | Example |
| :--- | :--- | :--- |
| **`feat`** | A new feature, tool action, or mining capability | `feat(drillholes): add 3d desurvey calculation` |
| **`fix`** | A bug fix or math correction | `fix(triangulation): handle zero division in centroid` |
| **`docs`** | Documentation, tutorial, or changelog changes | `docs(readme): add practical quickstart examples` |
| **`test`** | Adding, fixing, or updating test cases | `test(mock): add ast python 3.5 compatibility check` |
| **`refactor`** | Code changes that neither fix a bug nor add a feature | `refactor(wire): simplify SWIG list serializer` |
| **`chore`** | Build system, `.gitignore`, dependencies, or metadata | `chore(pyproject): update classifiers and gitignore` |

---

## 2. Interactive Workflow (Strict Protocol)

### Step 1: Pre-Commit Validation
Before offering a commit, always ensure code quality and testing pass:
```powershell
uv run --no-sync ruff check .
uv run --no-sync pytest tests/test_vulcan_mcp.py -v
```

### Step 2: Formulate the Proposal
Examine `git status -s` and `git diff --stat` to craft a clean, single-line summary with optional bullets.

### Step 3: Ask User for Confirmation
Present the proposed message and ask:
> *"All checks passed. Would you like me to commit these changes now (`git commit -m "..."`) or keep working?"*

### Step 4: Execute (Only Upon Approval)
When the user approves:
```powershell
git add <files>
git commit -m "type(scope): concise description"
```

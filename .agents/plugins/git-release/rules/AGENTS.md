# Git Commit & Semantic Release Rules

These rules govern how AI assistants interact with Git, format commits, bump version numbers, and consult with the user in **Vulcan MCP**.

---

## 1. Strictly Prohibited: No Silent Commits
* **Universal Guardrail**: The AI assistant MUST NEVER execute `git commit` automatically or silently.
* **Mandatory Confirmation**: After verifying code changes and automated tests (`pytest`), the assistant must always formulate a proposed Conventional Commit message and ask the user:
  > *"All tests passed. Would you like me to commit these changes now with message `type(scope): description` or keep working?"*
* Only when the user explicitly confirms (**"yes" / "commit" / "haz el commit"**) may the assistant run `git add` and `git commit`.

---

## 2. Commit Cadence Directive: Commits vs. Releases
* **Daily Edits / Commits**: Small bugfixes, doc clarifications, or test adjustments do NOT bump version numbers. They are regular git commits with the version unchanged.
* **Release Milestones**: Version numbers (`pyproject.toml`, `__init__.py`, `plugin.json`) are only bumped when closing a completed milestone, sprint, or public deliverable.

---

## 3. Autonomous Git Diff Inspection (Zero Memory Overhead)
* When the user asks for a release (e.g. *"prepara una nueva versión"*), the assistant MUST NOT ask the user to summarize what was done.
* Instead, the assistant automatically inspects Git history:
  ```powershell
  $latestTag = git describe --tags --abbrev=0
  git log "$latestTag..HEAD" --oneline
  git diff "$latestTag..HEAD" --stat
  ```
* Based on the diff, the assistant determines whether changes warrant a `PATCH`, `MINOR`, or `MAJOR` bump, drafts the [`CHANGELOG.md`](../../../CHANGELOG.md) entry, and presents it for user confirmation.

---

## 4. GitHub CLI (`gh`) Cloud Release Protocol
* **Pre-Flight Authentication**: Verify `gh auth status` before executing push or release actions.
* **Release Creation**: Upon user confirmation of a release milestone:
  1. Push commits and tags: `git push origin master --tags`.
  2. Extract release notes corresponding to the target version from `CHANGELOG.md`.
  3. Publish release: `gh release create <tag> --title "..." --notes-file "..."`.
  4. Verify with `gh release view <tag>`.
* **Zero Silent Releases**: As with commits, never execute `gh release create` without prior explicit confirmation of the version, title, and release notes.

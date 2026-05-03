---
description: Stage relevant changes and create a commit with a clear message
argument-hint: "[optional context for the message]"
---

Create a git commit for the current working changes. Extra context from the user: $ARGUMENTS

Steps:

1. Run `git status` and `git diff` (both staged and unstaged) in parallel to see what changed.
2. Run `git log -10 --oneline` to match the repo's commit message style.
3. Decide whether the changes are:
   - **Solution work** (new/modified files in topic dirs like `arrays/`, `dp/`, etc.): the message should name the problem(s) — e.g. `add 0001 two sum`, `update 0042 trapping rain water reflection`. One commit per problem when possible; group only when changes are tightly related.
   - **Tooling work** (changes under `src/leetcode_tools/`, `tests/`, `pyproject.toml`, `.claude/`, README, etc.): use a conventional short imperative subject — e.g. `add topic-consistency check to lc validate`, `fix metadata parser for empty constraints`.
   - **Daily file** (under `daily/`): unusual for me to commit by hand — the analysis prompt does this. Confirm with the user before proceeding.
4. Before staging, run `lc validate --strict` if any solution files changed. If it fails, fix the issues (or surface them to the user) before committing.
5. Stage only the files relevant to the change — never `git add -A`. Skip anything that looks like a secret or stray artifact.
6. Write the commit. Subject line ≤ 72 chars, imperative mood, lowercase. Body only when the *why* is non-obvious; otherwise omit it.
7. Run `git status` after committing to confirm the tree is clean.

Do not push. Do not amend a previous commit unless I explicitly ask.

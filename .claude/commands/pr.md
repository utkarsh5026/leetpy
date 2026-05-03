---
description: Open a pull request for the current branch
argument-hint: "[optional title or context]"
---

Open a GitHub pull request for the current branch. Extra context: $ARGUMENTS

Steps:

1. Run in parallel: `git status`, `git branch --show-current`, `git log main..HEAD --oneline`, and `git diff main...HEAD --stat`.
2. If on `main`, stop and tell me to switch to a feature branch first.
3. If the branch has unpushed commits, push with `-u origin <branch>`.
4. Run `lc validate --strict` and `pytest --cov` if either tooling or solutions changed. Surface failures before opening the PR.
5. Group the diff into one of:
   - **Solutions**: list problems added/updated in the body (e.g. `- add 0001 two sum`, `- update 0042 reflection`).
   - **Tooling**: summarize what changed in `lc` and why.
   - **Mixed**: split the body into "Solutions" and "Tooling" sections.
6. Open the PR with `gh pr create`. Title ≤ 70 chars, imperative mood, lowercase. Use a HEREDOC for the body in this shape:

   ```
   ## Summary
   - <bullet>
   - <bullet>

   ## Test plan
   - [ ] `lc validate --strict`
   - [ ] `pytest --cov`
   ```

   Drop the test-plan bullets that don't apply (e.g. omit `pytest` for solution-only PRs).
7. Print the PR URL.

Do not merge.

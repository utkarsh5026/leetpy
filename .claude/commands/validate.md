---
description: Run lc validate and explain any findings
argument-hint: "[path]"
---

Run `lc validate` and walk me through the results.

Path argument (optional): $ARGUMENTS

Steps:

1. Run `lc validate ${ARGUMENTS:+--path "$ARGUMENTS"}`.
2. If the output is clean, just say so and stop.
3. If there are findings:
   - Group by file.
   - For each finding, restate the rule and the fix in one line.
   - Do NOT auto-fix anything. Wait for me to decide which findings to address — some may be intentional (e.g. a problem legitimately spanning topics, which is the topic-consistency warning).

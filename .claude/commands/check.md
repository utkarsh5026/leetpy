---
description: Run the full local check suite (validate, tests, lint)
---

Run all local checks and report the results.

Run these in parallel:

- `lc validate` — solution conventions.
- `pytest --cov` — test suite with coverage.
- `ruff check .` — lint.
- `ruff format --check .` — formatting.

For each check report pass/fail in one line. If any fail, show the relevant failing output and stop before suggesting fixes — wait for me to decide what to do.

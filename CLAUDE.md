# CLAUDE.md

Instructions for Claude Code when working in this repo.

## What this repo is

`leetpy` is the local home for my leetcode practice. It is one of three pieces:

1. A chrome extension that captures submission metadata on leetcode and copies a formatted comment block to my clipboard.
2. An external analysis prompt that runs daily, writing per-problem critique to `daily/YYYY-MM-DD.md` and committing it.
3. **This repo** — solution files organized by topic, plus a python CLI (`lc`) that helps create and validate them.

## Layout

- Topic dirs (`arrays/`, `dp/`, `trees/`, …) hold solution files.
- `daily/` holds analysis markdown files written by the external prompt. **Do not write to `daily/` from this repo's tooling.**
- `src/leetcode_tools/` is the `lc` CLI source.
- `tests/` is the pytest suite.

## Conventions

- Solution filenames: `<NNNN>_<snake_case_title>.<ext>` with 4-digit zero padding (e.g. `0042_trapping_rain_water.py`). Un-numbered fallback: `<snake_case_title>.<ext>`.
- Every solution starts with a `LEETCODE METADATA` block (paste from chrome extension) and a `REFLECTION` block (filled by hand). See [README.md](README.md) for the exact format.
- Required metadata fields: `Problem`, `Url`, `Submitted`, `Language`. Placeholder substring is literally `<FILL IN`.
- Required reflection fields: `Time taken`, `First instinct`, `Changed approach`, `Got stuck on`.

## CLI commands (after `pip install -e ".[dev]"`)

- `lc new --topic <t> --title "<title>" [--number N] [--language python] [--dry-run]` — create a new solution scaffold.
- `lc validate [--path P] [--strict]` — check files match conventions; `--strict` exits non-zero on issues.

## Tooling

- Python 3.12+ required (uses `StrEnum`).
- `ruff check .` and `ruff format .` — always clean before committing.
- `pytest --cov` — coverage floor is 80%.

## Working philosophy

This repo is intentionally small. Resist the urge to add features I haven't asked for: no statistics scripts, no notion sync, no search tool, no test runner for solutions, no web ui. Tooling grows in response to real demand from accumulated practice, not in anticipation of it.

When adding to `lc`, prefer extending existing modules over creating new ones. Each subcommand should live in its own logic module (like `new_problem.py`, `validate.py`) with a thin CLI wrapper in `cli.py`.

## Code style

- Type hints everywhere, `from __future__ import annotations` at the top of each module.
- `pathlib.Path` over `os.path`.
- Frozen dataclasses for structured data.
- Docstrings only on public functions, and only to explain *why* — type hints carry the *what*.
- Comments only when the reasoning is non-obvious from the code.
- Keep functions ≤ ~20 lines; split when there's a clean seam.

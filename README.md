# leetpy

The local home for my leetcode practice. Holds solution files organized by topic, daily analysis files written by an external prompt, and a small python CLI (`lc`) that helps me create and validate solutions.

This repo is one of three pieces:

- A chrome extension that captures submission metadata on leetcode and copies a formatted comment block to the clipboard.
- An analysis prompt that runs daily, writing a per-problem critique to `daily/YYYY-MM-DD.md` and committing it.
- This repo: the canonical record of code I wrote, plus tooling.

## Layout

```text
arrays/ strings/ trees/ ...   topic directories holding solution files
daily/                        markdown files produced by the analysis prompt
src/leetcode_tools/           CLI source
tests/                        pytest tests
```

The `daily/` files are inputs to my reading, not products of this tooling. Nothing in `lc` writes them.

## File naming convention

Solution files: `<NNNN>_<snake_case_title>.<ext>` — four-digit zero-padded number so directory listings sort correctly.

```text
0001_two_sum.py
0042_trapping_rain_water.py
0146_lru_cache.py
```

For the rare problem with no leetcode number: `<snake_case_title>.<ext>`.

## Metadata comment block

Every solution starts with two comment blocks. The `LEETCODE METADATA` block is what the chrome extension produces — paste it from the clipboard. The `REFLECTION` block is filled in by hand after solving.

```python
# LEETCODE METADATA
# Problem: Two Sum
# Number: 1
# Url: https://leetcode.com/problems/two-sum
# Difficulty: Easy
# Topics: Arrays, Hashing
# Submitted: 2026-05-03T10:23:00
# Language: python3
# Runtime: 52 ms (beats 87.3%)
# Memory: 17.2 MB (beats 64.1%)
# Constraints:
#   - 2 <= nums.length <= 10^4
#   - -10^9 <= nums[i] <= 10^9
# Summary: Find indices of two numbers summing to target.
# END METADATA

# REFLECTION
# Time taken: 12
# First instinct: Hash map for O(n)
# Changed approach: No
# Got stuck on: Edge case with duplicates
# END REFLECTION

def two_sum(nums, target): ...
```

For non-python languages, swap `#` for the appropriate single-line comment marker (`//` for js/ts/rust/go/c/cpp/java, `--` for sql).

## Install

```bash
pip install -e ".[dev]"
```

Requires python 3.12+. After install, `lc` is available on the path.

## Commands

### `lc new`

Create a new solution file with a placeholder metadata block.

```bash
lc new --topic arrays --number 1 --title "Two Sum"
lc new --topic dp --title "Climbing Stairs" --number 70 --language python
lc new --topic graphs --number 200 --title "Number of Islands" --dry-run
```

After creating, paste the chrome extension's clipboard content over the placeholder metadata block. The reflection block is filled by hand.

### `lc validate`

Check that solution files match the conventions. Run before committing.

```bash
lc validate                    # whole repo
lc validate --path arrays/     # one directory
lc validate --path arrays/0001_two_sum.py
lc validate --strict           # exit non-zero if any issues
```

The validator checks:

- Filename matches the `<NNNN>_<snake_case>.<ext>` convention.
- A `LEETCODE METADATA` block exists with `Problem`, `Url`, `Submitted`, `Language` filled in (no `<FILL IN ...>` placeholders left over).
- A `REFLECTION` block exists with all four fields filled in.
- The topics in metadata overlap with the topic directory the file lives in (warning, not error).

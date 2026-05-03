from __future__ import annotations

from datetime import datetime

from leetcode_tools.parsing import (
    detect_comment_marker,
    parse_metadata_block,
    parse_reflection_block,
)

GOOD_PY = """\
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
"""


GOOD_JS = """\
// LEETCODE METADATA
// Problem: Reverse Linked List
// Url: https://leetcode.com/problems/reverse-linked-list
// Submitted: 2026-04-12
// Language: javascript
// END METADATA

// REFLECTION
// Time taken: 8
// First instinct: Iterative
// Changed approach: No
// Got stuck on: Nothing
// END REFLECTION
"""


def test_metadata_full_python_block():
    md = parse_metadata_block(GOOD_PY)
    assert md is not None
    assert md.title == "Two Sum"
    assert md.number == 1
    assert md.url == "https://leetcode.com/problems/two-sum"
    assert md.difficulty == "Easy"
    assert md.topics == ["Arrays", "Hashing"]
    assert md.submitted == datetime(2026, 5, 3, 10, 23, 0)
    assert md.language == "python3"
    assert md.runtime_ms == 52
    assert md.runtime_percentile == 87.3
    assert md.memory_mb == 17.2
    assert md.memory_percentile == 64.1
    assert md.constraints == ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9"]
    assert md.summary and md.summary.startswith("Find indices")


def test_metadata_javascript_block():
    md = parse_metadata_block(GOOD_JS)
    assert md is not None
    assert md.title == "Reverse Linked List"
    assert md.language == "javascript"
    assert md.runtime_ms is None


def test_metadata_returns_none_when_block_absent():
    assert parse_metadata_block("def foo(): pass\n") is None


def test_metadata_silently_skips_malformed_lines():
    src = """\
# LEETCODE METADATA
# Problem: X
# Url: https://example.com
# this line has no colon and should be ignored
# : empty key should be ignored
# Difficulty: Hard
# END METADATA
"""
    md = parse_metadata_block(src)
    assert md is not None
    assert md.title == "X"
    assert md.difficulty == "Hard"


def test_metadata_handles_missing_end_marker():
    src = """\
# LEETCODE METADATA
# Problem: Truncated
# Url: https://example.com
"""
    md = parse_metadata_block(src)
    assert md is not None
    assert md.title == "Truncated"


def test_reflection_full_block():
    refl = parse_reflection_block(GOOD_PY)
    assert refl is not None
    assert refl.time_taken_minutes == 12
    assert refl.first_instinct == "Hash map for O(n)"
    assert refl.changed_approach == "No"
    assert refl.got_stuck_on == "Edge case with duplicates"


def test_reflection_returns_none_when_block_absent():
    assert parse_reflection_block("# Problem: x\n") is None


def test_reflection_partial_block_yields_partial_object():
    src = """\
# REFLECTION
# Time taken: 30
# First instinct:
# END REFLECTION
"""
    refl = parse_reflection_block(src)
    assert refl is not None
    assert refl.time_taken_minutes == 30
    assert refl.first_instinct is None
    assert refl.changed_approach is None


def test_detect_comment_marker():
    assert detect_comment_marker("foo.py") == "#"
    assert detect_comment_marker("foo.rb") == "#"
    assert detect_comment_marker("foo.js") == "//"
    assert detect_comment_marker("foo.ts") == "//"
    assert detect_comment_marker("foo.rs") == "//"
    assert detect_comment_marker("foo.sql") == "--"
    assert detect_comment_marker("foo.unknown") == "//"


def test_metadata_parses_runtime_without_percentile():
    src = """\
# LEETCODE METADATA
# Problem: X
# Url: https://example.com
# Runtime: 100 ms
# Memory: 14 MB
# END METADATA
"""
    md = parse_metadata_block(src)
    assert md is not None
    assert md.runtime_ms == 100
    assert md.runtime_percentile is None
    assert md.memory_mb == 14.0


def test_metadata_constraints_inline_value():
    src = """\
# LEETCODE METADATA
# Problem: X
# Url: https://example.com
# Constraints: 1 <= n <= 100
# Language: python
# END METADATA
"""
    md = parse_metadata_block(src)
    assert md is not None
    assert md.constraints == ["1 <= n <= 100"]

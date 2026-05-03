from __future__ import annotations

from pathlib import Path

import pytest

from leetcode_tools.validate import (
    Severity,
    discover_solution_files,
    validate_files,
)

VALID_FILE = """\
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
# Summary: Find two indices summing to target.
# END METADATA

# REFLECTION
# Time taken: 12
# First instinct: Hash map
# Changed approach: No
# Got stuck on: Nothing
# END REFLECTION
"""


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "arrays").mkdir()
    (tmp_path / "dp").mkdir()
    (tmp_path / "daily").mkdir()
    (tmp_path / "src").mkdir()
    return tmp_path


def _write(repo: Path, rel: str, content: str) -> Path:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_passing_file_has_no_findings(repo: Path):
    path = _write(repo, "arrays/0001_two_sum.py", VALID_FILE)
    report = validate_files([path], repo)
    assert report.errors == ()
    assert report.warnings == ()


def test_filename_violation_flagged(repo: Path):
    path = _write(repo, "arrays/TwoSum.py", VALID_FILE)
    report = validate_files([path], repo)
    rules = {f.rule for f in report.errors}
    assert "filename" in rules


def test_missing_metadata_block_flagged(repo: Path):
    path = _write(repo, "arrays/0002_add_two_numbers.py", "def f(): pass\n")
    report = validate_files([path], repo)
    rules = {f.rule for f in report.errors}
    assert "metadata-present" in rules
    assert "reflection-present" in rules


def test_placeholder_metadata_flagged(repo: Path):
    body = VALID_FILE.replace(
        "# Url: https://leetcode.com/problems/two-sum",
        "# Url: <FILL IN FROM EXTENSION>",
    )
    path = _write(repo, "arrays/0001_two_sum.py", body)
    report = validate_files([path], repo)
    rules = {f.rule for f in report.errors}
    assert "metadata-placeholder" in rules


def test_missing_required_metadata_field_flagged(repo: Path):
    body = VALID_FILE.replace("# Submitted: 2026-05-03T10:23:00\n", "")
    path = _write(repo, "arrays/0001_two_sum.py", body)
    report = validate_files([path], repo)
    rules = {f.rule for f in report.errors}
    assert "metadata-required" in rules


def test_empty_reflection_field_flagged(repo: Path):
    body = VALID_FILE.replace("# First instinct: Hash map", "# First instinct:")
    path = _write(repo, "arrays/0001_two_sum.py", body)
    report = validate_files([path], repo)
    rules = {f.rule for f in report.errors}
    assert "reflection-complete" in rules


def test_topic_consistency_warning(repo: Path):
    path = _write(repo, "dp/0001_two_sum.py", VALID_FILE)
    report = validate_files([path], repo)
    rules = {(f.rule, f.severity) for f in report.warnings}
    assert ("topic-consistency", Severity.WARNING) in rules


def test_topic_consistency_no_warning_when_topics_empty(repo: Path):
    body = VALID_FILE.replace("# Topics: Arrays, Hashing\n", "")
    path = _write(repo, "dp/0001_two_sum.py", body)
    report = validate_files([path], repo)
    rules = {f.rule for f in report.warnings}
    assert "topic-consistency" not in rules


def test_discover_skips_excluded_dirs(repo: Path):
    _write(repo, "arrays/0001_two_sum.py", VALID_FILE)
    _write(repo, "daily/2026-05-03.md", "## daily\n")
    _write(repo, "src/foo.py", "x = 1\n")
    found = discover_solution_files(repo)
    names = {p.name for p in found}
    assert "0001_two_sum.py" in names
    assert "foo.py" not in names


def test_discover_with_specific_path(repo: Path):
    target = _write(repo, "arrays/0001_two_sum.py", VALID_FILE)
    found = discover_solution_files(repo, target)
    assert found == [target.resolve()]

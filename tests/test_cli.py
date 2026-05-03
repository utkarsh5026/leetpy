from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from leetcode_tools.cli import main

_VALID_SOLUTION = """\
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
def isolated_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("pyproject.toml").write_text(
        '[project]\nname="t"\nversion="0"\n',
        encoding="utf-8",
    )
    (tmp_path / "arrays").mkdir()
    return tmp_path


def test_cli_help_exits_zero() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "validate" in result.output


def test_cli_version_exits_zero() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0


def test_cli_validate_reports_success(isolated_repo: Path) -> None:
    (isolated_repo / "arrays" / "0001_two_sum.py").write_text(_VALID_SOLUTION, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["validate"])
    assert result.exit_code == 0
    assert "All files pass validation" in result.output


def test_cli_validate_strict_fails_on_errors(isolated_repo: Path) -> None:
    (isolated_repo / "arrays" / "0002_bad.py").write_text("def f():\n    pass\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["validate", "--strict"])
    assert result.exit_code == 1


def test_cli_new_dry_run(isolated_repo: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["new", "--topic", "arrays", "--title", "Two Sum", "--number", "1", "--dry-run"],
    )
    assert result.exit_code == 0
    assert "Would create" in result.output
    assert "0001_two_sum.py" in result.output


def test_cli_new_fails_when_file_exists(isolated_repo: Path) -> None:
    target = isolated_repo / "arrays" / "0001_two_sum.py"
    target.write_text(_VALID_SOLUTION, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["new", "--topic", "arrays", "--title", "Two Sum", "--number", "1"],
    )
    assert result.exit_code == 1
    assert "already exists" in result.output.lower()

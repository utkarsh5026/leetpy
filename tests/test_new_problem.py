from __future__ import annotations

from pathlib import Path

import pytest

from leetcode_tools.new_problem import (
    FileAlreadyExistsError,
    build_filename,
    create_new_problem,
    slugify_title,
)
from leetcode_tools.parsing import parse_metadata_block, parse_reflection_block


def test_slugify_title_basic():
    assert slugify_title("Two Sum") == "two_sum"
    assert slugify_title("Trapping Rain Water") == "trapping_rain_water"
    assert slugify_title("3Sum Closest") == "3sum_closest"
    assert slugify_title("Best Time to Buy & Sell Stock") == "best_time_to_buy_sell_stock"


def test_build_filename_padded_number():
    assert build_filename("Two Sum", 1, ".py") == "0001_two_sum.py"
    assert build_filename("Trapping Rain Water", 42, ".py") == "0042_trapping_rain_water.py"


def test_build_filename_no_number():
    assert build_filename("Custom Problem", None, ".py") == "custom_problem.py"


def test_create_new_problem_writes_file(tmp_path: Path):
    (tmp_path / "arrays").mkdir()
    plan = create_new_problem(
        repo_root=tmp_path,
        topic="arrays",
        title="Two Sum",
        number=1,
        language="python",
    )
    assert plan.created
    assert plan.path == tmp_path / "arrays" / "0001_two_sum.py"
    assert plan.path.exists()
    contents = plan.path.read_text()
    assert "LEETCODE METADATA" in contents
    assert "REFLECTION" in contents
    assert "<FILL IN FROM EXTENSION>" in contents


def test_dry_run_does_not_write(tmp_path: Path):
    plan = create_new_problem(
        repo_root=tmp_path,
        topic="arrays",
        title="Two Sum",
        number=1,
        language="python",
        dry_run=True,
    )
    assert not plan.created
    assert not plan.path.exists()
    assert "LEETCODE METADATA" in plan.content


def test_refuse_overwrite(tmp_path: Path):
    (tmp_path / "arrays").mkdir()
    create_new_problem(
        repo_root=tmp_path,
        topic="arrays",
        title="Two Sum",
        number=1,
        language="python",
    )
    with pytest.raises(FileAlreadyExistsError):
        create_new_problem(
            repo_root=tmp_path,
            topic="arrays",
            title="Two Sum",
            number=1,
            language="python",
        )


def test_template_is_parseable(tmp_path: Path):
    plan = create_new_problem(
        repo_root=tmp_path,
        topic="arrays",
        title="Two Sum",
        number=1,
        language="python",
        dry_run=True,
    )
    md = parse_metadata_block(plan.content)
    refl = parse_reflection_block(plan.content)
    assert md is not None
    assert md.title == "Two Sum"
    assert refl is not None


def test_javascript_uses_double_slash_marker(tmp_path: Path):
    plan = create_new_problem(
        repo_root=tmp_path,
        topic="arrays",
        title="Two Sum",
        number=1,
        language="javascript",
        dry_run=True,
    )
    assert plan.path.suffix == ".js"
    assert plan.content.startswith("// LEETCODE METADATA")

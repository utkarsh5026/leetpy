from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .parsing import detect_comment_marker

_LANGUAGE_EXTENSIONS: dict[str, str] = {
    "python": ".py",
    "python3": ".py",
    "py": ".py",
    "javascript": ".js",
    "js": ".js",
    "typescript": ".ts",
    "ts": ".ts",
    "rust": ".rs",
    "go": ".go",
    "java": ".java",
    "cpp": ".cpp",
    "c++": ".cpp",
    "c": ".c",
    "ruby": ".rb",
    "rb": ".rb",
    "sql": ".sql",
    "kotlin": ".kt",
    "swift": ".swift",
}


@dataclass(frozen=True)
class NewProblemPlan:
    path: Path
    content: str
    created: bool


class FileAlreadyExistsError(Exception):
    pass


def slugify_title(title: str) -> str:
    """Convert a problem title to snake_case suitable for a filename."""
    cleaned = re.sub(r"[^A-Za-z0-9\s_-]", "", title)
    cleaned = re.sub(r"[\s\-]+", "_", cleaned).strip("_").lower()
    return cleaned or "untitled"


def build_filename(title: str, number: int | None, extension: str) -> str:
    slug = slugify_title(title)
    if number is None:
        return f"{slug}{extension}"
    return f"{number:04d}_{slug}{extension}"


def language_extension(language: str) -> str:
    key = language.strip().lower()
    if key in _LANGUAGE_EXTENSIONS:
        return _LANGUAGE_EXTENSIONS[key]
    if key.startswith("."):
        return key
    return ".py"


def render_template(title: str, number: int | None, language: str, marker: str) -> str:
    """Render a placeholder solution file. Fields the chrome extension fills in
    are marked with `<FILL IN FROM EXTENSION>` so `lc validate` flags them if
    they're forgotten."""
    number_line = str(number) if number is not None else "<FILL IN FROM EXTENSION>"
    lines = [
        f"{marker} LEETCODE METADATA",
        f"{marker} Problem: {title}",
        f"{marker} Number: {number_line}",
        f"{marker} Url: <FILL IN FROM EXTENSION>",
        f"{marker} Difficulty: <FILL IN FROM EXTENSION>",
        f"{marker} Topics: <FILL IN FROM EXTENSION>",
        f"{marker} Submitted: <FILL IN FROM EXTENSION>",
        f"{marker} Language: {language}",
        f"{marker} Runtime: <FILL IN FROM EXTENSION>",
        f"{marker} Memory: <FILL IN FROM EXTENSION>",
        f"{marker} Summary: <FILL IN FROM EXTENSION>",
        f"{marker} END METADATA",
        "",
        f"{marker} REFLECTION",
        f"{marker} Time taken: ",
        f"{marker} First instinct: ",
        f"{marker} Changed approach: ",
        f"{marker} Got stuck on: ",
        f"{marker} END REFLECTION",
        "",
        "",
    ]
    return "\n".join(lines)


def plan_new_problem(
    *,
    repo_root: Path,
    topic: str,
    title: str,
    number: int | None,
    language: str,
) -> NewProblemPlan:
    """Compute the path and content for a new solution file without touching disk."""
    extension = language_extension(language)
    filename = build_filename(title, number, extension)
    path = repo_root / topic / filename
    marker = detect_comment_marker(path)
    content = render_template(title, number, language, marker)
    return NewProblemPlan(path=path, content=content, created=False)


def create_new_problem(
    *,
    repo_root: Path,
    topic: str,
    title: str,
    number: int | None,
    language: str,
    dry_run: bool = False,
) -> NewProblemPlan:
    plan = plan_new_problem(
        repo_root=repo_root, topic=topic, title=title, number=number, language=language
    )
    if dry_run:
        return plan
    if plan.path.exists():
        raise FileAlreadyExistsError(str(plan.path))
    plan.path.parent.mkdir(parents=True, exist_ok=True)
    plan.path.write_text(plan.content, encoding="utf-8")
    return NewProblemPlan(path=plan.path, content=plan.content, created=True)

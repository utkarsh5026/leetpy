from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from .parsing import parse_metadata_block, parse_reflection_block
from .types import ProblemMetadata, Reflection

_REQUIRED_METADATA_FIELDS = ("Problem", "Url", "Submitted", "Language")
_PLACEHOLDER_MARKER = "<FILL IN"
_FILENAME_RE = re.compile(r"^(?:\d{4}_)?[a-z0-9]+(?:_[a-z0-9]+)*\.[A-Za-z0-9]+$")
_SKIP_DIRS = frozenset({"daily", "tests", "src", "build", "dist", "__pycache__"})
_SOLUTION_EXTENSIONS = frozenset(
    {".py", ".js", ".ts", ".rs", ".go", ".java", ".cpp", ".c", ".rb", ".sql", ".kt", ".swift"}
)


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    path: Path
    severity: Severity
    rule: str
    message: str
    fix: str


@dataclass(frozen=True)
class FileReport:
    path: Path
    findings: tuple[Finding, ...]

    @property
    def ok(self) -> bool:
        return not self.findings


@dataclass(frozen=True)
class ValidationReport:
    files: tuple[FileReport, ...]

    @property
    def all_findings(self) -> tuple[Finding, ...]:
        return tuple(f for fr in self.files for f in fr.findings)

    @property
    def errors(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.all_findings if f.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.all_findings if f.severity is Severity.WARNING)


def discover_solution_files(root: Path, target: Path | None = None) -> list[Path]:
    """Return solution files under `target` (or `root` if None), skipping
    directories that don't hold solutions."""
    base = (target or root).resolve()
    if base.is_file():
        return [base] if _is_candidate(base, root.resolve()) else []
    return sorted(_walk(base, root.resolve()))


def _walk(base: Path, repo_root: Path) -> Iterator[Path]:
    for entry in base.iterdir():
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            if entry.name in _SKIP_DIRS:
                continue
            yield from _walk(entry, repo_root)
            continue
        if _is_candidate(entry, repo_root):
            yield entry


def _is_candidate(path: Path, repo_root: Path) -> bool:
    if path.suffix.lower() not in _SOLUTION_EXTENSIONS:
        return False
    try:
        rel_parts = path.resolve().relative_to(repo_root).parts
    except ValueError:
        return True
    return not any(part in _SKIP_DIRS or part.startswith(".") for part in rel_parts[:-1])


def validate_files(paths: Iterable[Path], repo_root: Path) -> ValidationReport:
    reports = tuple(_validate_one(p, repo_root) for p in paths)
    return ValidationReport(files=reports)


def _validate_one(path: Path, repo_root: Path) -> FileReport:
    findings: list[Finding] = []
    findings.extend(_check_filename(path))

    try:
        contents = path.read_text(encoding="utf-8")
    except OSError as exc:
        findings.append(
            Finding(
                path=path,
                severity=Severity.ERROR,
                rule="readable",
                message=f"Could not read file: {exc}",
                fix="Check file permissions and encoding.",
            )
        )
        return FileReport(path=path, findings=tuple(findings))

    metadata = parse_metadata_block(contents)
    findings.extend(_check_metadata(path, contents, metadata))

    reflection = parse_reflection_block(contents)
    findings.extend(_check_reflection(path, contents, reflection))

    if metadata is not None:
        findings.extend(_check_topic_consistency(path, repo_root, metadata))

    return FileReport(path=path, findings=tuple(findings))


def _check_filename(path: Path) -> list[Finding]:
    if _FILENAME_RE.match(path.name):
        return []
    return [
        Finding(
            path=path,
            severity=Severity.ERROR,
            rule="filename",
            message=f"Filename '{path.name}' does not match <NNNN>_<snake_case>.<ext>.",
            fix="Rename to e.g. 0042_trapping_rain_water.py (4-digit number, snake_case title).",
        )
    ]


def _check_metadata(path: Path, contents: str, metadata: ProblemMetadata | None) -> list[Finding]:
    if metadata is None:
        return [
            Finding(
                path=path,
                severity=Severity.ERROR,
                rule="metadata-present",
                message="No LEETCODE METADATA block found.",
                fix="Paste the chrome extension's clipboard content at the top of the file.",
            )
        ]

    findings: list[Finding] = []
    raw_block = _raw_block_text(contents, "LEETCODE METADATA", "END METADATA")
    for required in _REQUIRED_METADATA_FIELDS:
        line = _find_field_line(raw_block, required)
        if line is None or not _field_value(line):
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.ERROR,
                    rule="metadata-required",
                    message=f"Required metadata field '{required}' is missing or empty.",
                    fix=f"Add a '{required}: <value>' line inside the METADATA block.",
                )
            )
            continue
        if _PLACEHOLDER_MARKER in line:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.ERROR,
                    rule="metadata-placeholder",
                    message=f"Field '{required}' still contains a placeholder.",
                    fix="Replace the placeholder with the value from the chrome extension.",
                )
            )
    return findings


def _check_reflection(path: Path, contents: str, reflection: Reflection | None) -> list[Finding]:
    if reflection is None:
        return [
            Finding(
                path=path,
                severity=Severity.ERROR,
                rule="reflection-present",
                message="No REFLECTION block found.",
                fix="Add a REFLECTION block with Time taken / First instinct / "
                "Changed approach / Got stuck on.",
            )
        ]

    expected: list[tuple[str, object]] = [
        ("Time taken", reflection.time_taken_minutes),
        ("First instinct", reflection.first_instinct),
        ("Changed approach", reflection.changed_approach),
        ("Got stuck on", reflection.got_stuck_on),
    ]
    findings: list[Finding] = []
    for label, value in expected:
        if value in (None, ""):
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.ERROR,
                    rule="reflection-complete",
                    message=f"Reflection field '{label}' is empty.",
                    fix=f"Fill in '{label}' before committing.",
                )
            )
    return findings


def _check_topic_consistency(
    path: Path, repo_root: Path, metadata: ProblemMetadata
) -> list[Finding]:
    if not metadata.topics:
        return []
    try:
        rel = path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return []
    if len(rel.parts) < 2:
        return []
    directory = rel.parts[0].lower()
    normalized = {_normalize_topic(t) for t in metadata.topics}
    if _normalize_topic(directory) in normalized:
        return []
    return [
        Finding(
            path=path,
            severity=Severity.WARNING,
            rule="topic-consistency",
            message=(
                f"File is under '{directory}/' but metadata topics are "
                f"{metadata.topics}; no overlap."
            ),
            fix="Move the file to a matching topic directory or confirm the categorization.",
        )
    ]


def _normalize_topic(topic: str) -> str:
    return re.sub(r"[\s_-]+", "", topic).lower()


def _raw_block_text(contents: str, start: str, end: str) -> list[str]:
    lines = contents.splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        payload = _comment_payload(line)
        if not inside and payload == start:
            inside = True
            continue
        if inside and payload == end:
            break
        if inside:
            out.append(line)
    return out


def _comment_payload(line: str) -> str:
    stripped = line.lstrip()
    for marker in ("#", "//", "--"):
        if stripped.startswith(marker):
            return stripped[len(marker) :].strip()
    return stripped.strip()


def _find_field_line(block_lines: list[str], field: str) -> str | None:
    needle = field.lower()
    for line in block_lines:
        stripped = line.lstrip()
        for marker in ("#", "//", "--"):
            if stripped.startswith(marker):
                payload = stripped[len(marker) :].lstrip()
                if ":" in payload and payload.split(":", 1)[0].strip().lower() == needle:
                    return payload
    return None


def _field_value(line: str) -> str:
    return line.split(":", 1)[1].strip() if ":" in line else ""

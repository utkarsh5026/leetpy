from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from .types import ProblemMetadata, Reflection

_COMMENT_MARKERS_BY_EXT: dict[str, str] = {
    ".py": "#",
    ".rb": "#",
    ".sql": "--",
    ".js": "//",
    ".ts": "//",
    ".jsx": "//",
    ".tsx": "//",
    ".rs": "//",
    ".go": "//",
    ".c": "//",
    ".cpp": "//",
    ".cc": "//",
    ".h": "//",
    ".hpp": "//",
    ".java": "//",
    ".kt": "//",
    ".swift": "//",
}

_RUNTIME_RE = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>ms|MB|mb|kb|KB)\s*"
    r"(?:\(beats\s*(?P<pct>\d+(?:\.\d+)?)\s*%\s*\))?",
    re.IGNORECASE,
)


def detect_comment_marker(file_path: str | Path) -> str:
    """Return the single-line comment marker for the given file's language.

    Defaults to `//` for unknown extensions because that's the most common
    marker among the languages I'm likely to use.
    """
    ext = Path(file_path).suffix.lower()
    return _COMMENT_MARKERS_BY_EXT.get(ext, "//")


def _find_block(file_contents: str, start_label: str, end_label: str) -> list[str] | None:
    """Return the lines (without the start/end markers) of the first block whose
    opener contains `start_label` and whose closer contains `end_label`. Returns
    None if the start marker is absent — the only condition that signals "no block at all"."""
    lines = file_contents.splitlines()
    start_idx: int | None = None
    for i, line in enumerate(lines):
        if _is_comment_line(line) and _strip_comment(line).strip() == start_label:
            start_idx = i
            break
    if start_idx is None:
        return None
    for j in range(start_idx + 1, len(lines)):
        if _is_comment_line(lines[j]) and _strip_comment(lines[j]).strip() == end_label:
            return lines[start_idx + 1 : j]
    return lines[start_idx + 1 :]


def _is_comment_line(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith(("#", "//", "--"))


def _strip_comment(line: str) -> str:
    """Remove leading whitespace and a single comment marker from a line."""
    stripped = line.lstrip()
    for marker in ("#", "//", "--"):
        if stripped.startswith(marker):
            return stripped[len(marker) :].lstrip()
    return stripped


def _comment_indent(line: str) -> int:
    """Indentation *within* the comment payload — counts leading spaces after
    the comment marker. Used to detect indented continuation lines like
    constraint bullets."""
    stripped = line.lstrip()
    for marker in ("#", "//", "--"):
        if stripped.startswith(marker):
            payload = stripped[len(marker) :]
            return len(payload) - len(payload.lstrip())
    return 0


def _split_field(payload: str) -> tuple[str, str] | None:
    if ":" not in payload:
        return None
    key, _, value = payload.partition(":")
    return key.strip(), value.strip()


def parse_metadata_block(file_contents: str) -> ProblemMetadata | None:
    """Parse the LEETCODE METADATA block. Returns None only if the opening marker
    is absent — missing/malformed individual fields are silently skipped because
    this block is produced by an external tool and we don't want one bad field
    to discard the rest."""
    block = _find_block(file_contents, "LEETCODE METADATA", "END METADATA")
    if block is None:
        return None

    fields: dict[str, str] = {}
    constraints: list[str] = []
    in_constraints = False

    for raw in block:
        if not _is_comment_line(raw):
            in_constraints = False
            continue
        indent = _comment_indent(raw)
        payload = _strip_comment(raw)
        if not payload:
            in_constraints = False
            continue
        if in_constraints and indent > 0:
            constraints.append(payload.lstrip("-* ").strip())
            continue
        in_constraints = False
        split = _split_field(payload)
        if split is None:
            continue
        key, value = split
        if key.lower() == "constraints":
            in_constraints = True
            if value:
                constraints.append(value)
            continue
        fields[key.lower()] = value

    return _build_metadata(fields, constraints)


def _build_metadata(fields: dict[str, str], constraints: list[str]) -> ProblemMetadata | None:
    title = fields.get("problem") or fields.get("title")
    url = fields.get("url")
    if not title or not url:
        # Without a title or url there is no meaningful record. Treat as
        # "block present but unusable" — a stricter signal than missing block.
        title = title or ""
        url = url or ""

    runtime_ms, runtime_pct = _parse_perf(fields.get("runtime"))
    memory_val, memory_pct = _parse_perf(fields.get("memory"))

    return ProblemMetadata(
        title=title,
        url=url,
        number=_safe_int(fields.get("number")),
        difficulty=fields.get("difficulty") or None,
        topics=_split_list(fields.get("topics")),
        submitted=_safe_datetime(fields.get("submitted")),
        language=fields.get("language") or None,
        runtime_ms=int(runtime_ms) if runtime_ms is not None else None,
        runtime_percentile=runtime_pct,
        memory_mb=memory_val,
        memory_percentile=memory_pct,
        constraints=constraints,
        summary=fields.get("summary") or None,
    )


def parse_reflection_block(file_contents: str) -> Reflection | None:
    block = _find_block(file_contents, "REFLECTION", "END REFLECTION")
    if block is None:
        return None

    fields: dict[str, str] = {}
    for raw in block:
        if not _is_comment_line(raw):
            continue
        payload = _strip_comment(raw)
        split = _split_field(payload)
        if split is None:
            continue
        key, value = split
        fields[key.lower()] = value

    return Reflection(
        time_taken_minutes=_safe_int(fields.get("time taken")),
        first_instinct=fields.get("first instinct") or None,
        changed_approach=fields.get("changed approach") or None,
        got_stuck_on=fields.get("got stuck on") or None,
    )


def _parse_perf(value: str | None) -> tuple[float | None, float | None]:
    if not value:
        return None, None
    match = _RUNTIME_RE.search(value)
    if not match:
        return None, None
    val = float(match.group("value"))
    pct = float(match.group("pct")) if match.group("pct") else None
    return val, pct


def _safe_int(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"-?\d+", value)
    return int(match.group(0)) if match else None


def _safe_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    candidates = [value, value.replace(" ", "T"), value.split(" ")[0]]
    for candidate in candidates:
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            continue
    return None


def _split_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [p.strip() for p in value.split(",") if p.strip()]

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ProblemMetadata:
    """Parsed contents of a LEETCODE METADATA block.

    Frozen because the metadata flows through several stages of validation;
    accidental mutation in one stage would silently corrupt later checks.
    """

    title: str
    url: str
    number: int | None = None
    difficulty: str | None = None
    topics: list[str] = field(default_factory=list)
    submitted: datetime | None = None
    language: str | None = None
    runtime_ms: int | None = None
    runtime_percentile: float | None = None
    memory_mb: float | None = None
    memory_percentile: float | None = None
    constraints: list[str] = field(default_factory=list)
    summary: str | None = None


@dataclass(frozen=True)
class Reflection:
    """Parsed contents of a REFLECTION block. All fields optional because the
    block is hand-filled and may be partial when validation runs."""

    time_taken_minutes: int | None = None
    first_instinct: str | None = None
    changed_approach: str | None = None
    got_stuck_on: str | None = None

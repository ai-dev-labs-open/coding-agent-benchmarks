from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from ..tasks import TaskDefinition


@dataclass(frozen=True)
class FileEdit:
    """A deterministic filesystem edit produced by an agent."""

    path: str
    content: str


@dataclass(frozen=True)
class AgentContext:
    """Inputs passed to an agent for a single task."""

    task: TaskDefinition
    workspace_path: Path


@dataclass(frozen=True)
class AgentResult:
    """Structured agent response applied by the runner."""

    agent_id: str
    edits: list[FileEdit] = field(default_factory=list)
    notes: str = ""


class Agent(Protocol):
    """Provider-agnostic agent contract."""

    agent_id: str

    def solve(self, context: AgentContext) -> AgentResult:
        """Return deterministic file edits for the given task."""

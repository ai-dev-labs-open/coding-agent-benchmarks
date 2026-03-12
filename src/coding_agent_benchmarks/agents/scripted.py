from __future__ import annotations

import json
from pathlib import Path

from .base import AgentContext, AgentResult, FileEdit


class FixtureSolverAgent:
    """Loads deterministic solution edits from the task workspace."""

    agent_id = "fixture-solver"

    def solve(self, context: AgentContext) -> AgentResult:
        solution_file = Path(context.task.source_path).parent / "solution.json"
        payload = json.loads(solution_file.read_text(encoding="utf-8"))
        edits = [FileEdit(path=item["path"], content=item["content"]) for item in payload["edits"]]
        return AgentResult(
            agent_id=self.agent_id,
            edits=edits,
            notes=payload.get("notes", "Loaded fixture solution."),
        )


class NoOpAgent:
    """Produces no edits and is expected to fail most tasks."""

    agent_id = "noop"

    def solve(self, context: AgentContext) -> AgentResult:
        return AgentResult(agent_id=self.agent_id, edits=[], notes="No changes applied.")

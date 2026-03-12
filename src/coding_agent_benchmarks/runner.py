from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from .agents.base import Agent, AgentContext, AgentResult, FileEdit
from .tasks import TaskDefinition, TaskRepository


@dataclass(frozen=True)
class ValidationResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    duration_seconds: float


@dataclass(frozen=True)
class TaskRunResult:
    task_id: str
    suite: str
    agent_id: str
    success: bool
    score: float
    category: str
    difficulty: str
    duration_seconds: float
    edit_count: int
    notes: str
    validation: ValidationResult

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["validation"]["command"] = list(self.validation.command)
        return payload


def _group_stats(results: list[TaskRunResult], key: str) -> dict[str, dict[str, object]]:
    """Return pass/total counts grouped by an attribute of TaskRunResult."""
    groups: dict[str, list[TaskRunResult]] = {}
    for r in results:
        groups.setdefault(getattr(r, key), []).append(r)
    return {
        group: {
            "total": len(items),
            "passed": sum(1 for i in items if i.success),
            "pass_rate": round(sum(1 for i in items if i.success) / len(items), 4),
        }
        for group, items in sorted(groups.items())
    }


@dataclass(frozen=True)
class SuiteRunResult:
    suite: str
    agent_id: str
    total_tasks: int
    passed_tasks: int
    average_score: float
    duration_seconds: float
    results: list[TaskRunResult]
    by_category: dict[str, dict[str, object]]
    by_difficulty: dict[str, dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return {
            "suite": self.suite,
            "agent_id": self.agent_id,
            "total_tasks": self.total_tasks,
            "passed_tasks": self.passed_tasks,
            "average_score": self.average_score,
            "duration_seconds": self.duration_seconds,
            "by_category": self.by_category,
            "by_difficulty": self.by_difficulty,
            "results": [result.to_dict() for result in self.results],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def summary_lines(self) -> list[str]:
        """Return a compact human-readable summary."""
        lines = [
            f"Suite:  {self.suite}",
            f"Agent:  {self.agent_id}",
            f"Result: {self.passed_tasks}/{self.total_tasks} passed"
            f"  ({self.average_score * 100:.0f}%)"
            f"  in {self.duration_seconds:.1f}s",
            "",
            "By category:",
        ]
        for cat, stats in self.by_category.items():
            lines.append(
                f"  {cat:<25} {stats['passed']}/{stats['total']}"
                f"  ({stats['pass_rate'] * 100:.0f}%)"
            )
        lines.append("")
        lines.append("By difficulty:")
        for diff, stats in self.by_difficulty.items():
            lines.append(
                f"  {diff:<25} {stats['passed']}/{stats['total']}"
                f"  ({stats['pass_rate'] * 100:.0f}%)"
            )
        return lines


class BenchmarkRunner:
    """Executes tasks against an agent and records deterministic results."""

    def __init__(self, task_repository: TaskRepository | None = None) -> None:
        self.task_repository = task_repository or TaskRepository()

    def run_task(self, task: TaskDefinition, agent: Agent) -> TaskRunResult:
        started = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix=f"{task.id}-") as temp_dir:
            workspace_path = Path(temp_dir) / "workspace"
            shutil.copytree(task.workspace_path, workspace_path)
            agent_result = agent.solve(AgentContext(task=task, workspace_path=workspace_path))
            self.apply_edits(workspace_path, agent_result.edits)
            validation = self.validate(workspace_path, task)
        duration = time.perf_counter() - started
        success = validation.returncode == 0 and not validation.timed_out
        score = 1.0 if success else 0.0
        return TaskRunResult(
            task_id=task.id,
            suite=task.suite,
            agent_id=agent_result.agent_id,
            success=success,
            score=score,
            category=task.category,
            difficulty=task.difficulty,
            duration_seconds=round(duration, 4),
            edit_count=len(agent_result.edits),
            notes=agent_result.notes,
            validation=validation,
        )

    def run_suite(self, suite: str, agent: Agent) -> SuiteRunResult:
        tasks = self.task_repository.list_tasks(suite=suite)
        started = time.perf_counter()
        results = [self.run_task(task, agent) for task in tasks]
        duration = time.perf_counter() - started
        passed = sum(1 for result in results if result.success)
        average = round(sum(result.score for result in results) / len(results), 4) if results else 0.0
        return SuiteRunResult(
            suite=suite,
            agent_id=agent.agent_id,
            total_tasks=len(results),
            passed_tasks=passed,
            average_score=average,
            duration_seconds=round(duration, 4),
            results=results,
            by_category=_group_stats(results, "category"),
            by_difficulty=_group_stats(results, "difficulty"),
        )

    @staticmethod
    def apply_edits(workspace_path: Path, edits: list[FileEdit]) -> None:
        for edit in edits:
            destination = workspace_path / edit.path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(edit.content, encoding="utf-8")

    @staticmethod
    def validate(workspace_path: Path, task: TaskDefinition) -> ValidationResult:
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                task.validation_command,
                cwd=workspace_path,
                capture_output=True,
                text=True,
                timeout=task.timeout_seconds,
                check=False,
            )
            timed_out = False
            returncode = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as error:
            timed_out = True
            returncode = -1
            stdout = error.stdout or ""
            stderr = error.stderr or ""
        duration = time.perf_counter() - started
        return ValidationResult(
            command=task.validation_command,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            timed_out=timed_out,
            duration_seconds=round(duration, 4),
        )

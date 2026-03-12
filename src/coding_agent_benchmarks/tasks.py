from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TaskDefinition:
    id: str
    title: str
    category: str
    difficulty: str
    instruction: str
    workspace: str
    validation_command: list[str]
    timeout_seconds: int
    suite: str
    source_path: Path

    @property
    def workspace_path(self) -> Path:
        return self.source_path.parent / self.workspace


class TaskRepository:
    """Loads task manifests from the bundled tasks directory."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[2] / "tasks"

    def list_tasks(self, suite: str | None = None) -> list[TaskDefinition]:
        manifests = sorted(self.root.rglob("task.json"))
        tasks = [self._load_manifest(path) for path in manifests]
        if suite is None:
            return tasks
        return [task for task in tasks if task.suite == suite]

    def get_task(self, task_id: str) -> TaskDefinition:
        for task in self.list_tasks():
            if task.id == task_id:
                return task
        raise KeyError(f"Unknown task: {task_id}")

    def suites(self) -> list[str]:
        return sorted({task.suite for task in self.list_tasks()})

    def _load_manifest(self, path: Path) -> TaskDefinition:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return TaskDefinition(
            id=payload["id"],
            title=payload["title"],
            category=payload["category"],
            difficulty=payload["difficulty"],
            instruction=payload["instruction"],
            workspace=payload["workspace"],
            validation_command=payload["validation_command"],
            timeout_seconds=payload["timeout_seconds"],
            suite=payload["suite"],
            source_path=path,
        )

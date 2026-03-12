from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

VALID_CATEGORIES = {"bugfix", "feature", "refactor", "test_generation"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "difficulty",
    "instruction",
    "workspace",
    "validation_command",
    "timeout_seconds",
    "suite",
}


class ManifestError(ValueError):
    """Raised when a task.json fails validation."""


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


def validate_manifest(payload: dict, path: Path) -> None:
    """Raise ManifestError with a clear message if the manifest is invalid."""
    loc = str(path)

    missing = REQUIRED_FIELDS - payload.keys()
    if missing:
        raise ManifestError(f"{loc}: missing required fields: {sorted(missing)}")

    if payload["category"] not in VALID_CATEGORIES:
        raise ManifestError(
            f"{loc}: invalid category {payload['category']!r};"
            f" must be one of {sorted(VALID_CATEGORIES)}"
        )

    if payload["difficulty"] not in VALID_DIFFICULTIES:
        raise ManifestError(
            f"{loc}: invalid difficulty {payload['difficulty']!r};"
            f" must be one of {sorted(VALID_DIFFICULTIES)}"
        )

    if not isinstance(payload["validation_command"], list) or not payload["validation_command"]:
        raise ManifestError(f"{loc}: validation_command must be a non-empty list")

    if not isinstance(payload["timeout_seconds"], int) or payload["timeout_seconds"] <= 0:
        raise ManifestError(f"{loc}: timeout_seconds must be a positive integer")

    task_id = payload["id"]
    if not task_id or " " in task_id:
        raise ManifestError(f"{loc}: id must be a slug with no spaces, got {task_id!r}")

    workspace_path = path.parent / payload["workspace"]
    if not workspace_path.exists():
        raise ManifestError(
            f"{loc}: workspace directory does not exist: {workspace_path}"
        )


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
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ManifestError(f"{path}: invalid JSON — {exc}") from exc
        validate_manifest(payload, path)
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

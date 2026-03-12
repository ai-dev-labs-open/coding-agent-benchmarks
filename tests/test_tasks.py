import json
from pathlib import Path

import pytest

from coding_agent_benchmarks.tasks import ManifestError, TaskRepository, validate_manifest


def test_list_tasks_returns_all_core_python_tasks() -> None:
    repository = TaskRepository()

    tasks = repository.list_tasks()

    assert len(tasks) == 8
    assert {task.suite for task in tasks} == {"core-python"}


def test_get_task_exposes_manifest_fields() -> None:
    repository = TaskRepository()

    task = repository.get_task("py_feature_inventory")

    assert task.category == "feature"
    assert task.timeout_seconds == 10
    assert task.workspace_path == Path(task.source_path).parent / "workspace"


def _good_payload(tmp_path: Path) -> dict:
    (tmp_path / "workspace").mkdir()
    return {
        "id": "my_task",
        "title": "My Task",
        "category": "bugfix",
        "difficulty": "easy",
        "instruction": "Do the thing.",
        "workspace": "workspace",
        "validation_command": ["pytest", "-q"],
        "timeout_seconds": 10,
        "suite": "core-python",
    }


def test_validate_manifest_accepts_valid_payload(tmp_path: Path) -> None:
    payload = _good_payload(tmp_path)
    validate_manifest(payload, tmp_path / "task.json")  # should not raise


def test_validate_manifest_rejects_missing_field(tmp_path: Path) -> None:
    payload = _good_payload(tmp_path)
    del payload["category"]
    with pytest.raises(ManifestError, match="missing required fields"):
        validate_manifest(payload, tmp_path / "task.json")


def test_validate_manifest_rejects_bad_category(tmp_path: Path) -> None:
    payload = _good_payload(tmp_path)
    payload["category"] = "unknown"
    with pytest.raises(ManifestError, match="invalid category"):
        validate_manifest(payload, tmp_path / "task.json")


def test_validate_manifest_rejects_bad_difficulty(tmp_path: Path) -> None:
    payload = _good_payload(tmp_path)
    payload["difficulty"] = "extreme"
    with pytest.raises(ManifestError, match="invalid difficulty"):
        validate_manifest(payload, tmp_path / "task.json")


def test_validate_manifest_rejects_empty_validation_command(tmp_path: Path) -> None:
    payload = _good_payload(tmp_path)
    payload["validation_command"] = []
    with pytest.raises(ManifestError, match="non-empty list"):
        validate_manifest(payload, tmp_path / "task.json")


def test_validate_manifest_rejects_missing_workspace(tmp_path: Path) -> None:
    payload = _good_payload(tmp_path)
    payload["workspace"] = "nonexistent"
    with pytest.raises(ManifestError, match="workspace directory does not exist"):
        validate_manifest(payload, tmp_path / "task.json")


def test_validate_manifest_rejects_id_with_spaces(tmp_path: Path) -> None:
    payload = _good_payload(tmp_path)
    payload["id"] = "bad id"
    with pytest.raises(ManifestError, match="slug"):
        validate_manifest(payload, tmp_path / "task.json")

from pathlib import Path

from coding_agent_benchmarks.tasks import TaskRepository


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

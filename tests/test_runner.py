import json
from pathlib import Path

from coding_agent_benchmarks.agents.scripted import FixtureSolverAgent, NoOpAgent
from coding_agent_benchmarks.agents.base import FileEdit
from coding_agent_benchmarks.runner import BenchmarkRunner
from coding_agent_benchmarks.tasks import TaskDefinition, TaskRepository


def test_apply_edits_creates_nested_files(tmp_path: Path) -> None:
    runner = BenchmarkRunner()

    runner.apply_edits(
        tmp_path,
        [
            FileEdit(path="nested/output.txt", content="ok"),
        ],
    )

    assert (tmp_path / "nested" / "output.txt").read_text(encoding="utf-8") == "ok"


def test_run_task_with_fixture_solver_passes() -> None:
    repository = TaskRepository()
    runner = BenchmarkRunner(task_repository=repository)
    task = repository.get_task("py_bugfix_discount")

    result = runner.run_task(task, FixtureSolverAgent())

    assert result.success is True
    assert result.score == 1.0
    assert result.validation.returncode == 0


def test_run_task_with_noop_fails() -> None:
    repository = TaskRepository()
    runner = BenchmarkRunner(task_repository=repository)
    task = repository.get_task("py_bugfix_discount")

    result = runner.run_task(task, NoOpAgent())

    assert result.success is False
    assert result.score == 0.0
    assert result.validation.returncode != 0


def test_suite_report_serialization_contains_results() -> None:
    repository = TaskRepository()
    runner = BenchmarkRunner(task_repository=repository)

    report = runner.run_suite("core-python", FixtureSolverAgent())
    payload = json.loads(report.to_json())

    assert payload["suite"] == "core-python"
    assert payload["passed_tasks"] == 12
    assert len(payload["results"]) == 12
    assert "by_category" in payload
    assert "by_difficulty" in payload


def test_suite_report_summary_lines() -> None:
    repository = TaskRepository()
    runner = BenchmarkRunner(task_repository=repository)

    report = runner.run_suite("core-python", FixtureSolverAgent())
    lines = report.summary_lines()

    assert any("core-python" in line for line in lines)
    assert any("By category:" in line for line in lines)
    assert any("By difficulty:" in line for line in lines)


def test_suite_report_by_category_and_difficulty() -> None:
    repository = TaskRepository()
    runner = BenchmarkRunner(task_repository=repository)

    report = runner.run_suite("core-python", FixtureSolverAgent())

    for stats in report.by_category.values():
        assert stats["passed"] == stats["total"]
    for stats in report.by_difficulty.values():
        assert stats["passed"] == stats["total"]


def test_validation_timeout_is_recorded(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "sleeper.py").write_text("import time\ntime.sleep(0.2)\n", encoding="utf-8")
    manifest_path = tmp_path / "task.json"
    task = TaskDefinition(
        id="timeout_case",
        title="Timeout",
        category="bugfix",
        difficulty="easy",
        instruction="n/a",
        workspace="workspace",
        validation_command=["python3", "sleeper.py"],
        timeout_seconds=0.01,
        suite="core-python",
        source_path=manifest_path,
    )

    validation = BenchmarkRunner.validate(workspace, task)

    assert validation.timed_out is True
    assert validation.returncode == -1

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "coding_agent_benchmarks.cli", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        check=False,
    )


def test_list_command_outputs_task_ids() -> None:
    completed = run_cli("list")

    assert completed.returncode == 0
    assert "py_bugfix_discount" in completed.stdout
    assert "py_test_generation_tax" in completed.stdout


def test_run_command_passes_with_fixture_solver() -> None:
    completed = run_cli("run", "py_bugfix_slugify", "--agent", "fixture-solver")
    payload = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert payload["success"] is True
    assert payload["task_id"] == "py_bugfix_slugify"


def test_eval_command_writes_report(tmp_path: Path) -> None:
    output = tmp_path / "report.json"

    completed = run_cli(
        "eval", "--suite", "core-python", "--agent", "fixture-solver", "--output", str(output)
    )

    assert completed.returncode == 0
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["passed_tasks"] == 12
    assert "by_category" in payload
    assert "by_difficulty" in payload


def test_eval_command_prints_summary(tmp_path: Path) -> None:
    output = tmp_path / "report.json"

    completed = run_cli(
        "eval", "--suite", "core-python", "--agent", "fixture-solver", "--output", str(output)
    )

    assert "By category:" in completed.stdout
    assert "By difficulty:" in completed.stdout


def test_new_task_command_scaffolds_directory(tmp_path: Path) -> None:
    # Run with a custom tasks root by monkeypatching via env not feasible in subprocess;
    # instead verify the scaffold against a real temp structure by calling the handler directly.
    from coding_agent_benchmarks import cli

    class FakeArgs:
        task_id = "py_bugfix_scaffold_test"
        suite = "core-python"
        category = "bugfix"
        difficulty = "easy"

    # Temporarily override the tasks root
    original = cli._TASKS_ROOT
    cli._TASKS_ROOT = tmp_path / "tasks"
    try:
        (tmp_path / "tasks" / "core-python").mkdir(parents=True)
        result = cli.handle_new_task(FakeArgs())  # type: ignore[arg-type]
    finally:
        cli._TASKS_ROOT = original

    assert result == 0
    task_dir = tmp_path / "tasks" / "core-python" / "py_bugfix_scaffold_test"
    assert (task_dir / "task.json").exists()
    assert (task_dir / "solution.json").exists()
    assert (task_dir / "workspace").is_dir()
    manifest = json.loads((task_dir / "task.json").read_text())
    assert manifest["id"] == "py_bugfix_scaffold_test"
    assert manifest["category"] == "bugfix"


def test_run_command_unknown_agent_returns_error() -> None:
    completed = run_cli("run", "py_bugfix_discount", "--agent", "nonexistent")

    assert completed.returncode == 2
    assert "nonexistent" in completed.stderr

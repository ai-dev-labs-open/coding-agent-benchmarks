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

    completed = run_cli("eval", "--suite", "core-python", "--agent", "fixture-solver", "--output", str(output))

    assert completed.returncode == 0
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["passed_tasks"] == 8

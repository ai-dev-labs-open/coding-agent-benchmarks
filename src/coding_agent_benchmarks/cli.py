from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Sequence

from .agents.scripted import FixtureSolverAgent, NoOpAgent
from .runner import BenchmarkRunner
from .tasks import ManifestError, TaskRepository, VALID_CATEGORIES, VALID_DIFFICULTIES

_TASKS_ROOT = Path(__file__).resolve().parents[2] / "tasks"


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "command"):
        parser.print_help()
        return 1
    try:
        return args.func(args)
    except (KeyError, ManifestError) as error:
        print(str(error), file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bench", description="Coding agent benchmark CLI")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List available benchmark tasks")
    list_parser.add_argument("--suite", default=None, help="Filter tasks by suite")
    list_parser.set_defaults(func=handle_list)

    run_parser = subparsers.add_parser("run", help="Run a single benchmark task")
    run_parser.add_argument("task_id", help="Task identifier")
    run_parser.add_argument("--agent", default="fixture-solver", help="Agent identifier")
    run_parser.set_defaults(func=handle_run)

    eval_parser = subparsers.add_parser("eval", help="Run a benchmark suite")
    eval_parser.add_argument("--suite", default="core-python", help="Suite identifier")
    eval_parser.add_argument("--agent", default="fixture-solver", help="Agent identifier")
    eval_parser.add_argument("--output", required=True, help="Path to the JSON report file")
    eval_parser.set_defaults(func=handle_eval)

    new_parser = subparsers.add_parser(
        "new-task", help="Scaffold a new task directory with placeholder files"
    )
    new_parser.add_argument("task_id", help="Unique task slug (e.g. py_bugfix_myfeature)")
    new_parser.add_argument(
        "--suite", default="core-python", help="Suite name (default: core-python)"
    )
    new_parser.add_argument(
        "--category",
        default="bugfix",
        choices=sorted(VALID_CATEGORIES),
        help="Task category",
    )
    new_parser.add_argument(
        "--difficulty",
        default="easy",
        choices=sorted(VALID_DIFFICULTIES),
        help="Task difficulty",
    )
    new_parser.set_defaults(func=handle_new_task)

    return parser


def handle_list(args: argparse.Namespace) -> int:
    repository = TaskRepository()
    tasks = repository.list_tasks(suite=args.suite)
    for task in tasks:
        print(f"{task.id}\t{task.suite}\t{task.category}\t{task.difficulty}\t{task.title}")
    return 0


def handle_run(args: argparse.Namespace) -> int:
    repository = TaskRepository()
    runner = BenchmarkRunner(task_repository=repository)
    task = repository.get_task(args.task_id)
    agent = resolve_agent(args.agent)
    result = runner.run_task(task, agent)
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.success else 1


def handle_eval(args: argparse.Namespace) -> int:
    repository = TaskRepository()
    runner = BenchmarkRunner(task_repository=repository)
    agent = resolve_agent(args.agent)
    report = runner.run_suite(args.suite, agent)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.to_json(), encoding="utf-8")
    print("\n".join(report.summary_lines()))
    print(f"\nWrote report to {output_path}")
    return 0 if report.passed_tasks == report.total_tasks else 1


def handle_new_task(args: argparse.Namespace) -> int:
    task_id: str = args.task_id
    if " " in task_id:
        print(f"Error: task_id must be a slug with no spaces, got {task_id!r}", file=sys.stderr)
        return 2

    task_dir = _TASKS_ROOT / args.suite / task_id
    workspace_dir = task_dir / "workspace"

    if task_dir.exists():
        print(f"Error: {task_dir} already exists", file=sys.stderr)
        return 2

    workspace_dir.mkdir(parents=True)

    manifest = {
        "id": task_id,
        "title": task_id.replace("_", " ").title(),
        "category": args.category,
        "difficulty": args.difficulty,
        "instruction": "TODO: describe what the agent should do.",
        "workspace": "workspace",
        "validation_command": ["pytest", "-q"],
        "timeout_seconds": 10,
        "suite": args.suite,
    }
    (task_dir / "task.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    placeholder_src = textwrap.dedent("""\
        # TODO: add the starter implementation here.
        """)
    placeholder_test = textwrap.dedent("""\
        # TODO: add tests that validate the agent's solution.
        def test_placeholder() -> None:
            assert True
        """)
    (workspace_dir / "solution.py").write_text(placeholder_src, encoding="utf-8")
    (workspace_dir / "test_solution.py").write_text(placeholder_test, encoding="utf-8")

    solution = {"notes": "TODO: provide the reference solution edits.", "edits": []}
    (task_dir / "solution.json").write_text(
        json.dumps(solution, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Scaffolded new task at {task_dir}")
    print(f"  Edit {task_dir / 'task.json'} to complete the manifest.")
    print(f"  Add starter files to {workspace_dir}/")
    print(f"  Add solution edits to {task_dir / 'solution.json'}")
    return 0


def resolve_agent(agent_id: str):
    if agent_id == FixtureSolverAgent.agent_id:
        return FixtureSolverAgent()
    if agent_id == NoOpAgent.agent_id:
        return NoOpAgent()
    raise KeyError(f"Unknown agent: {agent_id!r} — available: fixture-solver, noop")


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .agents.scripted import FixtureSolverAgent, NoOpAgent
from .runner import BenchmarkRunner
from .tasks import TaskRepository


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "command"):
        parser.print_help()
        return 1
    try:
        return args.func(args)
    except KeyError as error:
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
    print(f"Wrote report to {output_path}")
    return 0 if report.passed_tasks == report.total_tasks else 1


def resolve_agent(agent_id: str):
    if agent_id == FixtureSolverAgent.agent_id:
        return FixtureSolverAgent()
    if agent_id == NoOpAgent.agent_id:
        return NoOpAgent()
    raise KeyError(f"Unknown agent: {agent_id}")


if __name__ == "__main__":
    raise SystemExit(main())

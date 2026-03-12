# Coding Agent Benchmarks

Coding Agent Benchmarks is a vendor-neutral, Python-first benchmark for evaluating coding agents on small repo-based software tasks.

The project focuses on tasks that resemble real development work: fixing bugs, adding features, refactoring code, and generating tests inside a starter repository. Each task is validated deterministically with local commands, so results are reproducible and do not depend on model-graded scoring.

## Why Repo-Based Tasks

Many coding benchmarks emphasize isolated algorithm problems. Those are useful, but they do not reflect how coding agents usually work. In practice, agents read existing files, reason about code structure, edit multiple files, and validate changes against tests. This benchmark is designed around that workflow.

## V1 Deliverables

- Local CLI for listing tasks, running one task, and evaluating a suite.
- Provider-agnostic agent interface.
- Deterministic scoring based on validation results and execution metadata.
- Eight Python repo-style tasks in an initial `core-python` suite.
- Scripted agents for local smoke tests and CI.

## Non-Goals

- Live model integrations in v1.
- Network-based evaluation.
- Human or LLM-judged scoring.
- Broad language coverage before the Python workflow is stable.

## Quickstart

Requirements:

- Python 3.11+
- `pytest` installed in the local environment

Create a virtual environment if you want isolated dependencies, then install the project in editable mode:

```bash
python3 -m pip install -e .
```

If you want to try the repo before installing it, prepend `PYTHONPATH=src` to the module commands shown below.

List tasks:

```bash
bench list
```

Equivalent no-install command:

```bash
PYTHONPATH=src python3 -m coding_agent_benchmarks.cli list
```

Run one task with the scripted solution agent:

```bash
bench run py_bugfix_discount --agent fixture-solver
```

Evaluate the default suite and write a JSON report:

```bash
bench eval --suite core-python --agent fixture-solver --output report.json
```

## Planned Structure

```text
src/coding_agent_benchmarks/
  agents/          Agent interface and scripted agents
  cli.py           Command-line entrypoint
  runner.py        Task execution and scoring
  tasks.py         Task loading and validation
tasks/
  core-python/     Task manifests and starter workspaces
tests/             Unit and integration tests
```

## Task Model

Each task manifest defines:

- `id`: stable task identifier
- `title`: human-readable name
- `category`: bugfix, feature, refactor, or test_generation
- `difficulty`: easy, medium, or hard
- `instruction`: task prompt given to the agent
- `workspace`: relative path to a starter repository
- `validation_command`: local command used to score success
- `timeout_seconds`: validation timeout
- `suite`: suite membership

## Roadmap

1. Stabilize the Python runner and task format.
2. Add richer scoring metadata and result analysis utilities.
3. Add pluggable provider integrations behind the same agent interface.
4. Expand coverage to TypeScript and issue-to-PR style tasks.

## Contributing Direction

The repo is intentionally small in v1. Contributions should favor:

- Deterministic validation over heuristic scoring
- Small, inspectable task repositories
- Stable public interfaces
- Reproducible local execution without external credentials

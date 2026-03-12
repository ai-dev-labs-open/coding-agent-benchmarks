# Coding Agent Benchmarks

Coding Agent Benchmarks is a vendor-neutral, Python-first benchmark for evaluating coding agents on small repo-based software tasks.

The project focuses on tasks that resemble real development work: fixing bugs, adding features, refactoring code, and generating tests inside a starter repository. Each task is validated deterministically with local commands, so results are reproducible and do not depend on model-graded scoring.

## Why Repo-Based Tasks

Many coding benchmarks emphasize isolated algorithm problems. Those are useful, but they do not reflect how coding agents usually work. In practice, agents read existing files, reason about code structure, edit multiple files, and validate changes against tests. This benchmark is designed around that workflow.

## What Is Included

- Local CLI for listing tasks, running one task, and evaluating a suite.
- Provider-agnostic agent interface with a registry for easy extension.
- Deterministic scoring based on validation results and execution metadata.
- 12 Python repo-style tasks in the `core-python` suite across four categories and three difficulty levels.
- Scripted agents (`fixture-solver`, `noop`) for local smoke tests and CI.
- Live `claude-api` agent backed by `claude-opus-4-6` with an agentic tool-use loop.
- Per-category and per-difficulty summary stats in both the JSON report and the CLI output.
- `bench new-task` scaffold command for authoring new tasks safely.

## Non-Goals

- Live model integrations in v1.
- Network-based evaluation.
- Human or LLM-judged scoring.
- Broad language coverage before the Python workflow is stable.

## Quickstart

Requirements:

- Python 3.11+
- `pytest` installed in the local environment

Install in editable mode:

```bash
python3 -m pip install -e .
```

List tasks:

```bash
bench list
```

Run one task with the scripted solution agent:

```bash
bench run py_bugfix_discount --agent fixture-solver
```

Evaluate the full suite and write a JSON report:

```bash
bench eval --suite core-python --agent fixture-solver --output report.json
```

Sample output:

```
Suite:  core-python
Agent:  fixture-solver
Result: 12/12 passed  (100%)  in 2.4s

By category:
  bugfix                    3/3  (100%)
  feature                   3/3  (100%)
  refactor                  3/3  (100%)
  test_generation           3/3  (100%)

By difficulty:
  easy                      4/4  (100%)
  hard                      2/2  (100%)
  medium                    6/6  (100%)
```

An example JSON report is at [`docs/example-report.json`](docs/example-report.json).

## Structure

```text
src/coding_agent_benchmarks/
  agents/          Agent interface, registry, and scripted agents
  cli.py           Command-line entrypoint
  runner.py        Task execution and scoring
  tasks.py         Task loading and manifest validation
tasks/
  core-python/     Task manifests and starter workspaces
tests/             Unit and integration tests
docs/
  authoring-tasks.md   Guide for adding new tasks
  example-report.json  Sample bench eval output
```

## Task Model

Each task manifest (`task.json`) defines:

| Field | Description |
|---|---|
| `id` | Stable task slug |
| `title` | Human-readable name |
| `category` | `bugfix`, `feature`, `refactor`, or `test_generation` |
| `difficulty` | `easy`, `medium`, or `hard` |
| `instruction` | Prompt given to the agent |
| `workspace` | Path to starter files |
| `validation_command` | Local command used to score success |
| `timeout_seconds` | Validation timeout |
| `suite` | Suite membership |

See [`docs/authoring-tasks.md`](docs/authoring-tasks.md) for a full guide on writing new tasks.

## Using the Claude API Agent

A live `claude-api` agent is included. It calls `claude-opus-4-6` with a `write_file` tool to express file edits as structured tool calls, then runs the agentic loop until the model stops.

Install with the `anthropic` extra:

```bash
pip install "coding-agent-benchmarks[anthropic]"
```

Set your API key and run:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
bench run py_bugfix_discount --agent claude-api
bench eval --suite core-python --agent claude-api --output report.json
```

## Adding a Custom Agent

Implement the `Agent` protocol (a class with `agent_id: str` and `solve(context) -> AgentResult`) and register it:

```python
from coding_agent_benchmarks.agents import registry

class MyAgent:
    agent_id = "my-agent"

    def solve(self, context):
        ...

registry.register(MyAgent.agent_id, MyAgent)
```

Then run:

```bash
bench run py_bugfix_discount --agent my-agent
```

## Roadmap

1. ~~Add CI.~~
2. ~~Improve reporting (per-category/difficulty stats, human-readable summary).~~
3. ~~Improve task ergonomics (manifest validation, scaffold command, authoring guide).~~
4. ~~Agent registry/factory pattern.~~
5. ~~Add pluggable provider integrations (live model agents).~~
6. Expand to TypeScript and issue-to-PR style tasks.

## Contributing

Contributions should favor:

- Deterministic validation over heuristic scoring
- Small, inspectable task repositories
- Stable public interfaces
- Reproducible local execution without external credentials

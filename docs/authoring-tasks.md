# Authoring Tasks

This document describes how to add a new benchmark task to the `core-python` suite (or a new suite).

## Quick start

Use the scaffold command to create the directory skeleton:

```bash
bench new-task py_bugfix_myfeature --category bugfix --difficulty easy
```

This creates:

```
tasks/core-python/py_bugfix_myfeature/
  task.json        # manifest — fill this in
  solution.json    # reference solution edits
  workspace/
    solution.py        # starter implementation placeholder
    test_solution.py   # test placeholder
```

## Directory layout

Every task lives in its own directory under `tasks/<suite>/<task-id>/`:

```
tasks/
  core-python/
    py_bugfix_myfeature/
      task.json       required — task manifest
      solution.json   required — reference solution (used by fixture-solver)
      workspace/      required — starter files given to the agent
        ...           any files the agent will read and edit
```

## task.json fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique slug (no spaces). Must match the directory name. |
| `title` | string | yes | Short human-readable name. |
| `category` | string | yes | One of `bugfix`, `feature`, `refactor`, `test_generation`. |
| `difficulty` | string | yes | One of `easy`, `medium`, `hard`. |
| `instruction` | string | yes | The prompt given to the agent. Be specific. |
| `workspace` | string | yes | Relative path to the starter workspace directory (usually `"workspace"`). |
| `validation_command` | list[str] | yes | Command run to score the task, e.g. `["pytest", "-q"]`. Must exit 0 on success. |
| `timeout_seconds` | int | yes | Maximum seconds for the validation command. Keep it short (10–30 s). |
| `suite` | string | yes | Suite this task belongs to (e.g. `"core-python"`). |

Example:

```json
{
  "id": "py_bugfix_myfeature",
  "title": "Fix off-by-one in myfeature",
  "category": "bugfix",
  "difficulty": "easy",
  "instruction": "The function `compute` in `myfeature.py` returns an incorrect result when the input is zero. Fix it.",
  "workspace": "workspace",
  "validation_command": ["pytest", "-q"],
  "timeout_seconds": 10,
  "suite": "core-python"
}
```

## solution.json format

`solution.json` is used by the `fixture-solver` scripted agent to apply a known-good solution. It is also the reference answer used to verify the task is solvable.

```json
{
  "notes": "Human-readable explanation of the fix.",
  "edits": [
    {
      "path": "myfeature.py",
      "content": "... full corrected file content ..."
    }
  ]
}
```

Each edit in `edits` replaces the entire file at `path` (relative to the workspace root). You can include edits for multiple files in one solution.

## Workspace design guidelines

- **Minimal**: include only the files the agent needs to read and edit.
- **Self-contained**: the workspace must run the validation command without network access or external dependencies beyond the Python stdlib and pytest.
- **Deterministic**: the validation command must always produce the same pass/fail result for a given set of file contents.
- **Fast**: keep validation under 10 seconds. pytest on a small workspace runs in well under 1 second.

## Writing good tasks

**Bugfix tasks**: introduce a small, specific bug in a real-looking function. The instruction should describe the *expected behaviour*, not the bug. The tests should fail on the starter code and pass after the fix.

**Feature tasks**: provide a partial implementation (e.g. a module with helper functions) and ask the agent to add one new function. Include tests that are already written and currently failing.

**Refactor tasks**: provide duplicated or tangled code and ask the agent to restructure it. The tests should pass both before and after — the validation proves nothing broke.

**Test generation tasks**: provide a complete, correct implementation and an empty or minimal test file. The instruction tells the agent what coverage to achieve. The fixture solution fills in the tests.

## Validating your task

After filling in the files, run:

```bash
# Confirm the manifest parses without errors
bench list

# Confirm fixture-solver passes
bench run py_bugfix_myfeature --agent fixture-solver

# Confirm noop fails (starter code should not pass on its own)
bench run py_bugfix_myfeature --agent noop
```

For test-generation tasks the noop check is not required — an empty test file often passes pytest by default. Instead confirm manually that the solution tests actually exercise the implementation.

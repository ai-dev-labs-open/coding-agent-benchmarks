# Claude Code Handoff Prompt

Use this prompt as the starting instruction for Claude Code when continuing work on this repository.

```text
You are continuing work in the repository `coding-agent-benchmarks`.

First, inspect the repo before changing anything. Read `README.md`, `pyproject.toml`, `src/coding_agent_benchmarks/`, `tasks/core-python/`, and `tests/` so you understand the current public contract and the existing implementation.

Project intent:
- This repo is a vendor-neutral, Python-first benchmark for coding agents.
- V1 already exists as a local runnable benchmark with:
  - an installable `bench` CLI
  - a provider-agnostic agent interface
  - deterministic scoring from local validation commands
  - 8 Python repo-style tasks in the `core-python` suite
  - scripted agents `fixture-solver` and `noop`
- The project should stay lightweight, inspectable, and reproducible without external credentials.

Current invariants you must preserve unless there is a strong reason to change them:
- Python 3.11+ only
- deterministic validation only; no LLM grading
- provider-neutral design
- stable CLI shape:
  - `bench list`
  - `bench run <task-id> --agent <agent-id>`
  - `bench eval --suite <suite> --agent <agent-id> --output <report.json>`
- task manifests remain simple and local
- the repo must remain runnable without live model integrations

What is already implemented:
- task loading and manifest model
- temporary workspace creation per task
- deterministic application of file edits produced by an agent
- validation command execution with timeout handling
- suite report JSON generation
- tests covering task loading, runner behavior, timeout handling, and CLI flows

Your job:
- Continue building the project from this foundation into a stronger open-source benchmark while preserving the current working interfaces.
- Prefer small, coherent increments that keep tests green.
- If you change any public behavior, update `README.md` and tests in the same change.

Recommended next priorities, in order:
1. Add CI so the benchmark and tests run automatically on GitHub.
2. Improve reporting:
   - add per-category and per-difficulty summary stats
   - add a compact human-readable CLI summary after `bench eval`
   - keep the JSON output stable and machine-friendly
3. Improve task ergonomics:
   - add manifest validation with clearer error messages
   - add helper tooling to scaffold a new task safely
   - document how to author new tasks
4. Make the agent interface more extensible without adding live providers yet:
   - define a cleaner registry/factory pattern for agents
   - keep `fixture-solver` and `noop`
   - make future provider integrations easy to add
5. Strengthen the benchmark corpus:
   - add more Python tasks with realistic multi-file edits
   - keep tasks deterministic and fast
6. Polish project quality:
   - better developer docs
   - example reports
   - release/packaging polish

Constraints:
- Do not add network-dependent functionality as part of the core benchmark path.
- Do not replace deterministic validation with subjective scoring.
- Do not over-engineer abstractions. This project should look serious, but stay lean.
- Avoid broad rewrites unless they clearly improve maintainability.

Execution guidance:
- Inspect the current tests before editing code.
- Make one coherent change at a time.
- Run the relevant tests after each meaningful change.
- Keep commit messages clean and human-readable.

Definition of good work:
- The repo stays easy to understand from the README.
- New functionality is covered by tests.
- The benchmark stays runnable locally on a fresh machine with minimal setup.
- The public interfaces become stronger, not noisier.

When you finish a change, summarize:
- what you changed
- what commands you ran to verify it
- any follow-up work that remains
```

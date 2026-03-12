"""Tests for ClaudeApiAgent using mocked anthropic calls."""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coding_agent_benchmarks.agents import registry, ClaudeApiAgent
from coding_agent_benchmarks.agents.base import AgentContext
from coding_agent_benchmarks.tasks import TaskDefinition


# ---------------------------------------------------------------------------
# Helpers to build fake API responses
# ---------------------------------------------------------------------------

def _make_text_block(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


def _make_tool_use_block(tool_id: str, name: str, path: str, content: str) -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = name
    block.input = {"path": path, "content": content}
    return block


def _make_response(
    stop_reason: str,
    blocks: list[MagicMock],
) -> MagicMock:
    resp = MagicMock()
    resp.stop_reason = stop_reason
    resp.content = blocks
    return resp


def _make_task(tmp_path: Path, instruction: str = "Fix the bug.") -> TaskDefinition:
    task_json = tmp_path / "task.json"
    task_json.write_text("{}", encoding="utf-8")
    return TaskDefinition(
        id="test_task",
        title="Test",
        category="bugfix",
        difficulty="easy",
        instruction=instruction,
        workspace="workspace",
        validation_command=["pytest"],
        timeout_seconds=10,
        suite="core-python",
        source_path=str(task_json),
    )


def _make_context(tmp_path: Path, task: TaskDefinition | None = None) -> AgentContext:
    workspace = tmp_path / "workspace"
    workspace.mkdir(exist_ok=True)
    (workspace / "solution.py").write_text("x = 1\n", encoding="utf-8")
    task = task or _make_task(tmp_path)
    return AgentContext(task=task, workspace_path=workspace)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_claude_api_agent_registered_in_registry() -> None:
    assert "claude-api" in registry.available()


def test_claude_api_agent_build_returns_instance() -> None:
    agent = registry.build("claude-api")
    assert isinstance(agent, ClaudeApiAgent)


def test_claude_api_agent_raises_without_anthropic(tmp_path: Path) -> None:
    """If anthropic is not importable, solve() raises ImportError."""
    context = _make_context(tmp_path)
    agent = ClaudeApiAgent()

    with patch.dict(sys.modules, {"anthropic": None}):
        with pytest.raises(ImportError, match="anthropic"):
            agent.solve(context)


def test_claude_api_agent_single_write_file_call(tmp_path: Path) -> None:
    """Agent returns one FileEdit when Claude calls write_file once."""
    context = _make_context(tmp_path)
    agent = ClaudeApiAgent()

    tool_block = _make_tool_use_block("tu1", "write_file", "solution.py", "x = 2\n")
    text_block = _make_text_block("Fixed the bug.")
    response = _make_response("end_turn", [tool_block, text_block])

    stream_cm = MagicMock()
    stream_cm.__enter__ = MagicMock(return_value=stream_cm)
    stream_cm.__exit__ = MagicMock(return_value=False)
    stream_cm.get_final_message = MagicMock(return_value=response)

    mock_client = MagicMock()
    mock_client.messages.stream.return_value = stream_cm

    mock_anthropic = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
        result = agent.solve(context)

    assert len(result.edits) == 1
    assert result.edits[0].path == "solution.py"
    assert result.edits[0].content == "x = 2\n"
    assert result.notes == "Fixed the bug."


def test_claude_api_agent_multiple_file_edits(tmp_path: Path) -> None:
    """Agent collects edits from multiple write_file calls in one response."""
    context = _make_context(tmp_path)
    agent = ClaudeApiAgent()

    blocks = [
        _make_tool_use_block("tu1", "write_file", "a.py", "a=1\n"),
        _make_tool_use_block("tu2", "write_file", "b.py", "b=2\n"),
        _make_text_block("Updated two files."),
    ]
    response = _make_response("end_turn", blocks)

    stream_cm = MagicMock()
    stream_cm.__enter__ = MagicMock(return_value=stream_cm)
    stream_cm.__exit__ = MagicMock(return_value=False)
    stream_cm.get_final_message = MagicMock(return_value=response)

    mock_client = MagicMock()
    mock_client.messages.stream.return_value = stream_cm
    mock_anthropic = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
        result = agent.solve(context)

    assert len(result.edits) == 2
    paths = {e.path for e in result.edits}
    assert paths == {"a.py", "b.py"}


def test_claude_api_agent_multi_turn_loop(tmp_path: Path) -> None:
    """Agent loops when stop_reason is 'tool_use' and stops on 'end_turn'."""
    context = _make_context(tmp_path)
    agent = ClaudeApiAgent()

    # First turn: Claude calls a tool and stop_reason is "tool_use"
    first_tool = _make_tool_use_block("tu1", "write_file", "a.py", "a=1\n")
    first_response = _make_response("tool_use", [first_tool])

    # Second turn: Claude is done
    second_tool = _make_tool_use_block("tu2", "write_file", "b.py", "b=2\n")
    second_text = _make_text_block("Done.")
    second_response = _make_response("end_turn", [second_tool, second_text])

    responses = iter([first_response, second_response])

    def fake_stream_cm(*args, **kwargs):
        cm = MagicMock()
        resp = next(responses)
        cm.__enter__ = MagicMock(return_value=cm)
        cm.__exit__ = MagicMock(return_value=False)
        cm.get_final_message = MagicMock(return_value=resp)
        return cm

    mock_client = MagicMock()
    mock_client.messages.stream.side_effect = fake_stream_cm
    mock_anthropic = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
        result = agent.solve(context)

    # Both turns' edits should be collected
    assert len(result.edits) == 2
    assert mock_client.messages.stream.call_count == 2
    assert result.notes == "Done."


def test_claude_api_agent_no_tool_calls_stops_immediately(tmp_path: Path) -> None:
    """If Claude produces no tool calls, solve() returns empty edits."""
    context = _make_context(tmp_path)
    agent = ClaudeApiAgent()

    text_block = _make_text_block("Nothing to change.")
    response = _make_response("end_turn", [text_block])

    stream_cm = MagicMock()
    stream_cm.__enter__ = MagicMock(return_value=stream_cm)
    stream_cm.__exit__ = MagicMock(return_value=False)
    stream_cm.get_final_message = MagicMock(return_value=response)

    mock_client = MagicMock()
    mock_client.messages.stream.return_value = stream_cm
    mock_anthropic = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
        result = agent.solve(context)

    assert result.edits == []
    assert result.notes == "Nothing to change."


def test_claude_api_agent_workspace_files_in_prompt(tmp_path: Path) -> None:
    """The API call should include workspace file contents in the user message."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "main.py").write_text("def foo(): pass\n", encoding="utf-8")

    task = _make_task(tmp_path, instruction="Add return value to foo.")
    context = AgentContext(task=task, workspace_path=workspace)
    agent = ClaudeApiAgent()

    response = _make_response("end_turn", [_make_text_block("done")])
    stream_cm = MagicMock()
    stream_cm.__enter__ = MagicMock(return_value=stream_cm)
    stream_cm.__exit__ = MagicMock(return_value=False)
    stream_cm.get_final_message = MagicMock(return_value=response)

    mock_client = MagicMock()
    mock_client.messages.stream.return_value = stream_cm
    mock_anthropic = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
        agent.solve(context)

    call_kwargs = mock_client.messages.stream.call_args[1]
    user_content = call_kwargs["messages"][0]["content"]
    assert "Add return value to foo." in user_content
    assert "def foo(): pass" in user_content
    assert "main.py" in user_content

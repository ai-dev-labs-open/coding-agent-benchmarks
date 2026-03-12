"""Live agent that calls the Anthropic Claude API to solve benchmark tasks.

Usage
-----
Install the optional dependency::

    pip install coding-agent-benchmarks[anthropic]

This registers the agent automatically.  Then run::

    ANTHROPIC_API_KEY=sk-... bench run py_bugfix_discount --agent claude-api

Or register manually::

    from coding_agent_benchmarks.agents import registry
    from coding_agent_benchmarks.agents.claude_api import ClaudeApiAgent
    registry.register(ClaudeApiAgent.agent_id, ClaudeApiAgent)
"""

from __future__ import annotations

from typing import Any

from .base import AgentContext, AgentResult, FileEdit


_SYSTEM_PROMPT = """\
You are an expert software engineer solving a coding benchmark task.

You will be given:
1. A task instruction describing what change needs to be made.
2. The current contents of all relevant files in the workspace.

Use the `write_file` tool to write the complete new content for every file you
need to create or modify.  Call `write_file` once per file — do not include
inline code blocks.  After all edits are written, you may add a brief explanation
and then stop.
"""

_WRITE_FILE_TOOL: dict[str, Any] = {
    "name": "write_file",
    "description": (
        "Write the full content of a file in the workspace. "
        "Call this once per file you need to create or modify."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the file within the workspace (e.g. 'solution.py').",
            },
            "content": {
                "type": "string",
                "description": "Complete new content for the file.",
            },
        },
        "required": ["path", "content"],
        "additionalProperties": False,
    },
}


class ClaudeApiAgent:
    """Benchmark agent backed by the Anthropic Claude API.

    Requires the ``anthropic`` package (``pip install anthropic``) and the
    ``ANTHROPIC_API_KEY`` environment variable to be set.

    The agent:
    1. Reads every file in the task workspace.
    2. Sends the task instruction and file contents to Claude.
    3. Uses a ``write_file`` tool so Claude can express file edits
       as structured tool calls rather than free-form text.
    4. Runs the agentic loop until Claude stops calling tools.
    5. Returns the collected ``FileEdit`` objects.
    """

    agent_id = "claude-api"
    model = "claude-opus-4-6"

    def solve(self, context: AgentContext) -> AgentResult:
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError(
                "The 'anthropic' package is required to use ClaudeApiAgent. "
                "Install it with: pip install anthropic"
            ) from exc

        client = anthropic.Anthropic()

        # Build workspace listing
        workspace = context.workspace_path
        file_sections: list[str] = []
        for path in sorted(workspace.rglob("*")):
            if path.is_file() and not path.name.startswith("."):
                rel = path.relative_to(workspace)
                content = path.read_text(encoding="utf-8", errors="replace")
                file_sections.append(f"### {rel}\n```\n{content}\n```")

        workspace_text = (
            "\n\n".join(file_sections) if file_sections else "(empty workspace)"
        )

        user_message = (
            f"## Task\n\n{context.task.instruction}\n\n"
            f"## Workspace files\n\n{workspace_text}\n\n"
            "Write the corrected or new file contents using the `write_file` tool."
        )

        messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
        edits: list[FileEdit] = []
        notes = "Solution applied via Claude API."

        # Agentic loop — continue until Claude issues no more tool calls.
        while True:
            with client.messages.stream(
                model=self.model,
                max_tokens=8192,
                thinking={"type": "adaptive"},
                system=_SYSTEM_PROMPT,
                tools=[_WRITE_FILE_TOOL],
                tool_choice={"type": "auto"},
                messages=messages,
            ) as stream:
                response = stream.get_final_message()

            tool_uses = [b for b in response.content if b.type == "tool_use"]

            # Collect write_file edits from this turn.
            for tool_use in tool_uses:
                if tool_use.name == "write_file":
                    edits.append(
                        FileEdit(
                            path=tool_use.input["path"],
                            content=tool_use.input["content"],
                        )
                    )

            # Extract any text explanation Claude provided.
            text_blocks = [b for b in response.content if b.type == "text"]
            if text_blocks:
                notes = text_blocks[-1].text

            if response.stop_reason == "end_turn" or not tool_uses:
                break

            # Feed tool results back so Claude can continue.
            messages.append({"role": "assistant", "content": response.content})
            tool_results = [
                {
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": f"File '{tu.input['path']}' written successfully.",
                }
                for tu in tool_uses
                if tu.name == "write_file"
            ]
            messages.append({"role": "user", "content": tool_results})

        return AgentResult(agent_id=self.agent_id, edits=edits, notes=notes)

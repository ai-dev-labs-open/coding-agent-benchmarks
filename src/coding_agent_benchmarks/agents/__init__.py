"""Available agent implementations."""

from .base import Agent, AgentContext, AgentResult, FileEdit
from .claude_api import ClaudeApiAgent
from .registry import AgentRegistry, registry
from .scripted import FixtureSolverAgent, NoOpAgent

# Register built-in scripted agents (always available).
registry.register(FixtureSolverAgent.agent_id, FixtureSolverAgent)
registry.register(NoOpAgent.agent_id, NoOpAgent)

# Register the live Claude API agent (requires the ``anthropic`` package at
# runtime, but the class itself is importable without it).
registry.register(ClaudeApiAgent.agent_id, ClaudeApiAgent)

__all__ = [
    "Agent",
    "AgentContext",
    "AgentRegistry",
    "AgentResult",
    "ClaudeApiAgent",
    "FileEdit",
    "FixtureSolverAgent",
    "NoOpAgent",
    "registry",
]

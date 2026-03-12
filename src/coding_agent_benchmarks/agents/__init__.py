"""Available agent implementations."""

from .base import Agent, AgentContext, AgentResult, FileEdit
from .registry import AgentRegistry, registry
from .scripted import FixtureSolverAgent, NoOpAgent

# Register built-in agents.
registry.register(FixtureSolverAgent.agent_id, FixtureSolverAgent)
registry.register(NoOpAgent.agent_id, NoOpAgent)

__all__ = [
    "Agent",
    "AgentContext",
    "AgentRegistry",
    "AgentResult",
    "FileEdit",
    "FixtureSolverAgent",
    "NoOpAgent",
    "registry",
]

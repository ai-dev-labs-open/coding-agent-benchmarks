"""Agent registry: maps agent IDs to factory callables.

To add a new agent, call ``register`` with its ID and a zero-argument factory:

    from coding_agent_benchmarks.agents.registry import registry
    registry.register("my-agent", MyAgent)

Third-party packages can register agents at import time from their own
``__init__`` or via a ``coding_agent_benchmarks.agents`` entry-point group
(entry-point discovery is not implemented in v1, but the registry is ready
for it).
"""

from __future__ import annotations

from typing import Callable

from .base import Agent


class AgentRegistry:
    """Maps string agent IDs to zero-argument factory callables."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[[], Agent]] = {}

    def register(self, agent_id: str, factory: Callable[[], Agent]) -> None:
        """Register a factory under *agent_id*.  Raises if already registered."""
        if agent_id in self._factories:
            raise ValueError(f"Agent already registered: {agent_id!r}")
        self._factories[agent_id] = factory

    def build(self, agent_id: str) -> Agent:
        """Instantiate and return the agent for *agent_id*.

        Raises ``KeyError`` with the available IDs listed when unknown.
        """
        if agent_id not in self._factories:
            available = ", ".join(sorted(self._factories))
            raise KeyError(
                f"Unknown agent: {agent_id!r} — available: {available}"
            )
        return self._factories[agent_id]()

    def available(self) -> list[str]:
        """Return sorted list of registered agent IDs."""
        return sorted(self._factories)


# Module-level singleton used by the CLI and runner.
registry = AgentRegistry()

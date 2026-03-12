import pytest

from coding_agent_benchmarks.agents import registry, FixtureSolverAgent, NoOpAgent
from coding_agent_benchmarks.agents.registry import AgentRegistry
from coding_agent_benchmarks.agents.base import AgentContext, AgentResult


def test_registry_contains_builtin_agents() -> None:
    assert "fixture-solver" in registry.available()
    assert "noop" in registry.available()


def test_registry_build_returns_correct_type() -> None:
    agent = registry.build("fixture-solver")
    assert isinstance(agent, FixtureSolverAgent)

    agent = registry.build("noop")
    assert isinstance(agent, NoOpAgent)


def test_registry_build_unknown_raises_key_error() -> None:
    with pytest.raises(KeyError, match="unknown-agent"):
        registry.build("unknown-agent")


def test_registry_error_lists_available_agents() -> None:
    with pytest.raises(KeyError, match="fixture-solver"):
        registry.build("bad-id")


def test_registry_register_duplicate_raises() -> None:
    r = AgentRegistry()
    r.register("my-agent", NoOpAgent)
    with pytest.raises(ValueError, match="already registered"):
        r.register("my-agent", NoOpAgent)


def test_registry_custom_agent_can_be_registered_and_used() -> None:
    class EchoAgent:
        agent_id = "echo"

        def solve(self, context: AgentContext) -> AgentResult:
            return AgentResult(agent_id=self.agent_id, edits=[], notes="echo")

    r = AgentRegistry()
    r.register("echo", EchoAgent)
    agent = r.build("echo")
    assert agent.agent_id == "echo"

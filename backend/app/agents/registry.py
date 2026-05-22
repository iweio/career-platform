"""Agent Registry — simple dict, no harness needed."""

from app.agents.base import AgentBase
from app.agents.resume_analyzer.graph import agent as resume_analyzer
from app.agents.job_matcher.graph import agent as job_matcher
from app.agents.career_planner.graph import agent as career_planner
from app.agents.learning_plan.graph import agent as learning_plan

_registry: dict[str, AgentBase] = {}
_initialized = False


def init_agents():
    """Register all 4 agents. Call once at startup."""
    global _initialized
    if _initialized:
        return
    register(resume_analyzer)
    register(job_matcher)
    register(career_planner)
    register(learning_plan)
    _initialized = True


def register(agent: AgentBase) -> None:
    _registry[agent.agent_id] = agent


def get_agent(agent_id: str) -> AgentBase:
    return _registry[agent_id]


def list_agents() -> list[dict]:
    return [
        {"agent_id": a.agent_id, "display_name": a.display_name, "description": a.description}
        for a in _registry.values()
    ]

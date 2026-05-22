from abc import ABC, abstractmethod
from typing import Any, Dict
from langgraph.graph import StateGraph


class AgentBase(ABC):
    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Build and return a compiled LangGraph StateGraph (with self_reflect node)."""
        ...

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the graph with input data, return result."""
        graph = self.build_graph()
        return await graph.ainvoke(input_data)

    @property
    @abstractmethod
    def agent_id(self) -> str:
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

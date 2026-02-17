"""Minimal AI Chief of Staff orchestration flow.

This script intentionally works without external dependencies.
If `langgraph` is available, `build_langgraph_flow` shows how the same nodes could be wired.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class StaffTask:
    owner: str
    title: str
    priority: str


@dataclass
class ChiefOfStaffState:
    request: str
    goals: List[str] = field(default_factory=list)
    tasks: List[StaffTask] = field(default_factory=list)
    status: str = "new"


def intake(state: ChiefOfStaffState) -> ChiefOfStaffState:
    state.status = "intake_complete"
    state.goals = [
        "Convert executive request into 1-week objectives",
        "Identify owners and deadlines",
        "Create visibility for follow-up",
    ]
    return state


def planning(state: ChiefOfStaffState) -> ChiefOfStaffState:
    state.status = "plan_ready"
    state.tasks = [
        StaffTask("finance_lead", "Draft budget impact memo", "high"),
        StaffTask("ops_lead", "Create implementation timeline", "high"),
        StaffTask("ea", "Schedule decision review meeting", "medium"),
    ]
    return state


def review(state: ChiefOfStaffState) -> ChiefOfStaffState:
    state.status = "ready_for_exec_review"
    return state


def run_minimal_flow(request: str) -> ChiefOfStaffState:
    state = ChiefOfStaffState(request=request)
    for step in (intake, planning, review):
        state = step(state)
    return state


def build_langgraph_flow():
    """Optional: wire the same logic using LangGraph when available."""
    try:
        from langgraph.graph import END, StateGraph
    except ImportError:
        return None

    graph = StateGraph(ChiefOfStaffState)
    graph.add_node("intake", intake)
    graph.add_node("planning", planning)
    graph.add_node("review", review)
    graph.set_entry_point("intake")
    graph.add_edge("intake", "planning")
    graph.add_edge("planning", "review")
    graph.add_edge("review", END)
    return graph.compile()


if __name__ == "__main__":
    result = run_minimal_flow("Prepare Q3 cross-functional launch plan")
    print("Status:", result.status)
    print("Goals:")
    for goal in result.goals:
        print("-", goal)
    print("Tasks:")
    for task in result.tasks:
        print(f"- [{task.priority}] {task.owner}: {task.title}")

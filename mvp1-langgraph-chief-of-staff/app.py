"""Minimal LangGraph-based AI Chief of Staff workflow.

This focuses on orchestration behavior, not model quality.
"""

from typing import TypedDict, List

from langgraph.graph import END, StateGraph


class ChiefOfStaffState(TypedDict):
    objective: str
    context: str
    priorities: List[str]
    draft_plan: str
    final_plan: str


def planner_node(state: ChiefOfStaffState) -> ChiefOfStaffState:
    objective = state["objective"]
    context = state["context"]
    state["priorities"] = [
        f"Clarify success criteria for: {objective}",
        "Identify dependencies and blockers",
        "Define next 7-day execution milestones",
    ]
    state["draft_plan"] = (
        f"Objective: {objective}\n"
        f"Context: {context}\n"
        f"Priorities:\n- " + "\n- ".join(state["priorities"])
    )
    return state


def reviewer_node(state: ChiefOfStaffState) -> ChiefOfStaffState:
    state["final_plan"] = (
        state["draft_plan"]
        + "\n\nReview notes:\n"
        + "- Confirm owners for each milestone\n"
        + "- Add meeting cadence (daily/weekly)\n"
        + "- Track risks in a single shared dashboard"
    )
    return state


def build_graph():
    graph = StateGraph(ChiefOfStaffState)
    graph.add_node("planner", planner_node)
    graph.add_node("reviewer", reviewer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "reviewer")
    graph.add_edge("reviewer", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    result = app.invoke(
        {
            "objective": "Launch internal AI assistant for leadership staff",
            "context": "Pilot with 2 departments in 30 days",
            "priorities": [],
            "draft_plan": "",
            "final_plan": "",
        }
    )

    print("=== Chief of Staff Plan ===")
    print(result["final_plan"])

    print("\nAlternatives to test next:")
    print("- CrewAI for role-based multi-agent collaboration")
    print("- AutoGen for conversational agent swarms")
    print("- Temporal + plain LangChain for durable workflow orchestration")

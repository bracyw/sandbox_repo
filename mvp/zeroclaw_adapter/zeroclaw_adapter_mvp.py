"""Minimal ZeroClaw integration-style adapter for an AI Chief of Staff.

This does not depend on the real ZeroClaw package. It models how a routing layer
might package and dispatch tasks into a ZeroClaw-compatible backend.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class RoutedTask:
    queue: str
    payload: Dict[str, str]


class ChiefOfStaffRouter:
    """Simple routing logic that can later call ZeroClaw APIs."""

    TEAM_QUEUES = {
        "finance": "zeroclaw-finance",
        "operations": "zeroclaw-ops",
        "exec_support": "zeroclaw-ea",
    }

    def route(self, objective: str) -> List[RoutedTask]:
        return [
            RoutedTask(
                queue=self.TEAM_QUEUES["finance"],
                payload={"task": f"Estimate cost impact for: {objective}"},
            ),
            RoutedTask(
                queue=self.TEAM_QUEUES["operations"],
                payload={"task": f"Build rollout checklist for: {objective}"},
            ),
            RoutedTask(
                queue=self.TEAM_QUEUES["exec_support"],
                payload={"task": f"Prepare exec briefing for: {objective}"},
            ),
        ]


def demo() -> None:
    router = ChiefOfStaffRouter()
    objective = "Launch internal AI assistant pilot"
    routed_tasks = router.route(objective)

    print("Routing objective:", objective)
    for routed in routed_tasks:
        print(f"- queue={routed.queue} payload={routed.payload}")


if __name__ == "__main__":
    demo()

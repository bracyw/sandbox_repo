from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Dict, List


@dataclass
class Command:
    name: str
    objective: str
    constraints: List[str]


class ChiefOfStaffRouter:
    """Minimal command router inspired by ZeroClaw-style command dispatch."""

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable[[Command], dict]] = {
            "plan_week": self._plan_week,
            "status_brief": self._status_brief,
        }

    def handle(self, command: Command) -> dict:
        handler = self._handlers.get(command.name)
        if not handler:
            return {
                "ok": False,
                "error": f"unknown command: {command.name}",
                "supported": sorted(self._handlers.keys()),
            }
        return {"ok": True, "result": handler(command)}

    def _plan_week(self, command: Command) -> dict:
        return {
            "objective": command.objective,
            "priorities": [
                "Clarify scope and owners",
                "Execute top 3 unblockers",
                "Publish Friday review",
            ],
            "constraints": command.constraints,
        }

    def _status_brief(self, command: Command) -> dict:
        return {
            "summary": f"Progress update for: {command.objective}",
            "highlights": [
                "Key milestone advanced",
                "One risk identified",
                "Next decision needed from leadership",
            ],
            "constraints": command.constraints,
        }


def main() -> None:
    router = ChiefOfStaffRouter()
    sample = Command(
        name="plan_week",
        objective="Prepare partner launch readiness plan",
        constraints=["team size fixed", "budget cap $20k"],
    )
    print(json.dumps(router.handle(sample), indent=2))


if __name__ == "__main__":
    main()

# MVP 1: LangGraph (and alternatives) for an AI Chief of Staff

This MVP shows a minimal planning/execution loop for a Chief-of-Staff style assistant.

## What this can do

- Intake goals from a founder/executive.
- Break into weekly priorities.
- Generate action items and owners.
- Track status updates and propose next actions.

## Minimal architecture

```text
Input (Slack/Email/Form)
  -> Planner Agent
  -> Delegation Agent
  -> Follow-up Agent
  -> Weekly Summary Agent
  -> Output (Notion/Jira/Slack)
```

## LangGraph state idea

```python
state = {
  "goal": "Launch partner GTM in 4 weeks",
  "constraints": ["no new hires", "budget <= $20k"],
  "tasks": [],
  "risks": [],
  "updates": []
}
```

## Example nodes to implement

- `intake_node`: normalize user goals into structured inputs.
- `plan_node`: produce 3-5 strategic workstreams.
- `delegate_node`: convert workstreams into tasks with owners/dates.
- `followup_node`: generate reminders and escalation messages.
- `summary_node`: produce executive summary with blockers.

## Alternatives to test quickly

1. **CrewAI**: role-based collaboration model and easier quick-start setup.
2. **Microsoft AutoGen**: good for multi-agent chat loops and tool use.
3. **OpenAI Assistants + scheduler**: simplest path if graph control is not required initially.

## Minimal success criteria

- Given one weekly objective, the system outputs:
  - 3+ actionable tasks,
  - clear owner + deadline,
  - one concise status brief.

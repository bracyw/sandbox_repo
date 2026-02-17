# MVP 1: LangGraph (or alternatives) Chief of Staff flow

This MVP provides a tiny state-machine style orchestration flow.

## Why this helps

- Test intake → planning → review loops.
- Validate which tasks should be delegated and to whom.
- Compare lightweight custom orchestrator vs. LangGraph runtime.

## Run

```bash
python3 chief_of_staff_flow.py
```

## Next steps

- Add real LLM calls for goal extraction and task generation.
- Add memory store for follow-up updates.
- Add Slack/Email integration for delegation.

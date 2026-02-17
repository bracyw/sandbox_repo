# MVP 2: ZeroClaw-based Chief of Staff adapter

This MVP sketches a routing layer that can sit in front of a ZeroClaw deployment.

## What it demonstrates

- Objective intake from an executive request.
- Mapping to team-specific queues.
- Structured task payloads suitable for worker execution.

## Run

```bash
python3 zeroclaw_adapter_mvp.py
```

## Build-off ideas for https://github.com/zeroclaw-labs/zeroclaw

- Replace `ChiefOfStaffRouter.route` output with actual ZeroClaw task submission calls.
- Add result callbacks so the Chief of Staff can summarize status.
- Add policy controls for approval gates and escalation.

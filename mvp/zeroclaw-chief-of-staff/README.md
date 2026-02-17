# MVP 2: Build on ZeroClaw for an AI Chief of Staff

This MVP sketches how to extend ideas from `zeroclaw` into a Chief-of-Staff system.

## Core concept

Use a central command router (ZeroClaw-like command model) to:

- accept requests (`plan_qbr`, `prepare_board_update`, `follow_up_on_hiring`),
- route to specialist agents,
- return structured outputs for leadership workflows.

## Proposed modules

- `ChiefOfStaffRouter`: routes commands to handlers.
- `PlanningHandler`: generates strategic plans and milestones.
- `OperationsHandler`: converts plans into tasks and operating cadences.
- `CommsHandler`: drafts stakeholder updates.

See `src/chief_of_staff_router.py` for a tiny in-repo starter.

## MVP success criteria

- CLI command triggers routing.
- Returns machine-readable JSON output.
- Supports at least two command types (`plan_week`, `status_brief`).

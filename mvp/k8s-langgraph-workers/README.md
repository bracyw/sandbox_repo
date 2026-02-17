# MVP 3: Kubernetes setup with basic LangGraph workers and queue

This MVP provides a minimal Kubernetes baseline for queue-backed AI workers.

## What is included

- Redis queue deployment/service.
- Worker deployment that polls Redis for jobs.
- API deployment placeholder that can enqueue jobs.

## Deploy quickly

```bash
kubectl apply -f manifests/
```

## Flow

1. API receives request.
2. API writes job payload to Redis list (`chief_of_staff_jobs`).
3. Worker pops jobs, runs LangGraph workflow, writes result to logs/store.

## Next steps

- Replace placeholder images with your own image registry.
- Add persistent result store (Postgres/S3).
- Add horizontal scaling (HPA or KEDA).

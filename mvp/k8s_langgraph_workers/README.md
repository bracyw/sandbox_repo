# MVP 3: Kubernetes setup for basic LangGraph-style workers + queues

This folder contains a minimal queue-backed setup:

- Redis deployment/service as queue backend.
- Worker deployment for processing tasks.
- Producer CronJob that enqueues heartbeat tasks.

## Apply

```bash
kubectl apply -f namespace.yaml
kubectl apply -f redis.yaml
kubectl apply -f worker.yaml
kubectl apply -f producer-cronjob.yaml
```

## Notes

- Image values are placeholders and should be replaced with real worker/producer images.
- This is intentionally minimal to validate cluster wiring and flow.

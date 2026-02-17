# Kubernetes MVP: LangGraph workers + queue

This folder contains a minimal Kubernetes setup for running background worker processes against a queue.

## Included resources

- `namespace.yaml`: isolated namespace (`ai-chief-of-staff`)
- `redis.yaml`: in-cluster Redis queue
- `worker-configmap.yaml`: environment config for workers
- `worker-deployment.yaml`: basic worker deployment with 2 replicas

## Apply

```bash
kubectl apply -f .
```

## Validate

```bash
kubectl get all -n ai-chief-of-staff
```

## Notes

- Worker image is currently a placeholder (`python:3.11-slim`) that prints heartbeat logs.
- Replace with your real worker image once LangGraph task-consumer code is packaged.

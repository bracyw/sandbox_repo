# AI Chief of Staff MVP Sandbox

This repo contains three lightweight MVPs to quickly test direction for an **AI Chief of Staff** product.

## MVPs

1. **LangGraph (or alternatives) orchestration MVP**
   - Folder: `mvp/langgraph_orchestrator/`
   - Demonstrates an agent workflow that turns an executive request into prioritized, delegated tasks.

2. **ZeroClaw-based integration MVP**
   - Folder: `mvp/zeroclaw_adapter/`
   - Demonstrates how a Chief of Staff layer can wrap and route tasks into ZeroClaw-compatible executors.

3. **Kubernetes MVP for workers + queues**
   - Folder: `mvp/k8s_langgraph_workers/`
   - Provides basic queue-backed worker infrastructure suitable for LangGraph-style task execution.

## Quick checks

```bash
python3 mvp/langgraph_orchestrator/chief_of_staff_flow.py
python3 mvp/zeroclaw_adapter/zeroclaw_adapter_mvp.py
```

The Kubernetes manifests can be inspected and applied to a test cluster:

```bash
kubectl apply -f mvp/k8s_langgraph_workers/
```

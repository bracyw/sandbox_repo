# AI Chief of Staff MVP Sandbox

This repository contains three small MVP starters so you can quickly test different implementation paths for an **AI Chief of Staff**:

1. **LangGraph or alternatives** (agent orchestration patterns).
2. **A ZeroClaw-based approach** (bootstrapping from `zeroclaw`).
3. **Kubernetes with workers + queue** (minimal deploy shape for LangGraph-style jobs).

Each MVP is intentionally lightweight and designed to be iterated into separate production repositories if useful.

## Structure

- `mvp/langgraph-alternatives`: quick architecture and starter flows.
- `mvp/zeroclaw-chief-of-staff`: minimal adapter around ZeroClaw ideas.
- `mvp/k8s-langgraph-workers`: queue-driven worker deployment manifests.

# AI Chief of Staff MVP Sandbox

This repo now contains **three lightweight MVP starters** so you can quickly test different implementation paths:

1. **LangGraph (and alternatives) for an AI Chief of Staff**  
   Path: `mvp1-langgraph-chief-of-staff/`
2. **ZeroClaw-based AI Chief of Staff scaffold**  
   Path: `mvp2-zeroclaw-chief-of-staff/`
3. **Kubernetes setup for LangGraph workers + queue**  
   Path: `mvp3-k8s-langgraph-workers/`

## Quick start

### 1) LangGraph MVP
```bash
cd mvp1-langgraph-chief-of-staff
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### 2) ZeroClaw scaffold MVP
```bash
cd mvp2-zeroclaw-chief-of-staff
python adapter.py
```

### 3) Kubernetes queue/worker MVP
```bash
kubectl apply -f mvp3-k8s-langgraph-workers/
```

> These are intentionally minimal so you can rapidly iterate into separate production-ready PRs later.

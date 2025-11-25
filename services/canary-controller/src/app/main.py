from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Canary Controller", version="1.0.0")


class MetricsSnapshot(BaseModel):
    error_rate: float
    latency_p95_ms: int
    cpu_percent: float


class CanaryDecisionRequest(BaseModel):
    app_name: str
    stable_weight: int
    canary_weight: int
    metrics: MetricsSnapshot
    max_error_rate: float = 0.02
    max_latency_p95_ms: int = 500


class CanaryDecisionResult(BaseModel):
    app_name: str
    new_stable_weight: int
    new_canary_weight: int
    action: str
    reason: str


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/decide", response_model=CanaryDecisionResult)
def decide(req: CanaryDecisionRequest):
    m = req.metrics
    if m.error_rate > req.max_error_rate or m.latency_p95_ms > req.max_latency_p95_ms:
        action = "rollback"
        new_stable = 100
        new_canary = 0
        reason = "Canary metrics exceeded thresholds."
    elif req.canary_weight < 50:
        action = "promote"
        new_canary = min(100, req.canary_weight + 10)
        new_stable = 100 - new_canary
        reason = "Canary healthy, increasing traffic."
    else:
        action = "hold"
        new_canary = req.canary_weight
        new_stable = req.stable_weight
        reason = "Canary stable at current level."

    return CanaryDecisionResult(
        app_name=req.app_name,
        new_stable_weight=new_stable,
        new_canary_weight=new_canary,
        action=action,
        reason=reason,
    )

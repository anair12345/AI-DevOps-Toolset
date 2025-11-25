from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SLO Keeper", version="1.0.0")


class SLOInput(BaseModel):
    service_name: str
    target_slo_percent: float
    total_events: int
    bad_events: int


class SLOResult(BaseModel):
    service_name: str
    target_slo_percent: float
    current_slo_percent: float
    error_budget_percent_remaining: float
    error_budget_status: str


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/compute", response_model=SLOResult)
def compute(req: SLOInput):
    if req.total_events == 0:
        current = 100.0
    else:
        good = req.total_events - req.bad_events
        current = (good / req.total_events) * 100

    error_budget = max(0.0, req.target_slo_percent - (100 - current))
    status = "healthy"
    if error_budget < 50:
        status = "warning"
    if error_budget <= 0:
        status = "exhausted"

    return SLOResult(
        service_name=req.service_name,
        target_slo_percent=req.target_slo_percent,
        current_slo_percent=current,
        error_budget_percent_remaining=error_budget,
        error_budget_status=status,
    )

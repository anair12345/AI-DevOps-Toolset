from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI(title="Chaos Scheduler", version="1.0.0")


class ChaosExperimentRequest(BaseModel):
    service_name: str
    blast_radius: str
    duration_minutes: int = 30
    earliest_start: datetime | None = None


class ChaosExperimentPlan(BaseModel):
    service_name: str
    scheduled_start: datetime
    scheduled_end: datetime
    blast_radius: str
    safeguards: list[str]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/plan-experiment", response_model=ChaosExperimentPlan)
def plan_experiment(req: ChaosExperimentRequest):
    start = req.earliest_start or datetime.utcnow() + timedelta(hours=1)
    end = start + timedelta(minutes=req.duration_minutes)
    safeguards = [
        "Disable experiment if error budget is exhausted.",
        "Abort immediately if SLO violation detected.",
    ]
    return ChaosExperimentPlan(
        service_name=req.service_name,
        scheduled_start=start,
        scheduled_end=end,
        blast_radius=req.blast_radius,
        safeguards=safeguards,
    )

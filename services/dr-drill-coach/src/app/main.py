from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="DR Drill Coach", version="1.0.0")


class DRDrillRequest(BaseModel):
    drill_id: str
    start_time: datetime
    end_time: datetime
    rto_target_minutes: int
    rpo_target_minutes: int


class DRDrillResult(BaseModel):
    drill_id: str
    actual_rto_minutes: float
    actual_rpo_minutes: float
    rto_met: bool
    rpo_met: bool
    grade: str


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/score", response_model=DRDrillResult)
def score(req: DRDrillRequest):
    duration = (req.end_time - req.start_time).total_seconds() / 60
    rpo = duration / 2

    rto_met = duration <= req.rto_target_minutes
    rpo_met = rpo <= req.rpo_target_minutes

    if rto_met and rpo_met:
        grade = "A"
    elif rto_met or rpo_met:
        grade = "B"
    else:
        grade = "C"

    return DRDrillResult(
        drill_id=req.drill_id,
        actual_rto_minutes=duration,
        actual_rpo_minutes=rpo,
        rto_met=rto_met,
        rpo_met=rpo_met,
        grade=grade,
    )

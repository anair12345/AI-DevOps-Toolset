from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Incident RCA Builder", version="1.0.0")


class RCARequest(BaseModel):
    incident_id: str
    from_time: datetime
    to_time: datetime
    services: list[str] | None = None


class RCATimelineEvent(BaseModel):
    timestamp: datetime
    message: str
    source: str


class RCAResult(BaseModel):
    incident_id: str
    summary: str
    probable_cause: str
    contributing_factors: list[str]
    remediation_actions: list[str]
    timeline: list[RCATimelineEvent]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/build", response_model=RCAResult)
def build_rca(req: RCARequest):
    timeline = [
        RCATimelineEvent(
            timestamp=req.from_time, message="Elevated error rate detected", source="monitoring"
        ),
        RCATimelineEvent(
            timestamp=req.from_time, message="Deployment started", source="pipeline"
        ),
        RCATimelineEvent(
            timestamp=req.to_time, message="Rollback completed", source="pipeline"
        ),
    ]
    summary = (
        f"Incident {req.incident_id} between {req.from_time} and {req.to_time} "
        "appears correlated with a recent deployment."
    )
    probable_cause = "New deployment introduced a breaking configuration change."
    contributing_factors = [
        "Insufficient pre-deployment synthetic checks",
        "Missing canary rollout for high-risk changes",
    ]
    remediation_actions = [
        "Add config validation step to pipeline",
        "Introduce canary releases for this service",
    ]

    return RCAResult(
        incident_id=req.incident_id,
        summary=summary,
        probable_cause=probable_cause,
        contributing_factors=contributing_factors,
        remediation_actions=remediation_actions,
        timeline=timeline,
    )

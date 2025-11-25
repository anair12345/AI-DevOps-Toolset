from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Runbook Copilot", version="1.0.0")


class RunbookRequest(BaseModel):
    prompt: str
    runbook_id: str
    dry_run: bool = True
    requested_by: str | None = None


class RunbookPlan(BaseModel):
    run_id: str
    runbook_id: str
    dry_run: bool
    steps: list[str]
    guardrails: list[str]
    status: str
    created_at: datetime


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/plan", response_model=RunbookPlan)
def plan_runbook(req: RunbookRequest):
    steps = [
        "Validate requester and RBAC permissions",
        f"Fetch runbook '{req.runbook_id}' definition",
        "Simulate execution and calculate impact",
        "Request approval if required",
    ]
    guardrails = [
        "No destructive operations in PROD without approval",
        "Read-only actions allowed without change ticket",
    ]
    run_id = f"rb-{int(datetime.utcnow().timestamp())}"

    return RunbookPlan(
        run_id=run_id,
        runbook_id=req.runbook_id,
        dry_run=req.dry_run,
        steps=steps,
        guardrails=guardrails,
        status="planned",
        created_at=datetime.utcnow(),
    )

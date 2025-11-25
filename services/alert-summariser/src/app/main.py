from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Alert Summariser", version="1.0.0")


class Alert(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    raw: dict | None = None


class AlertSummary(BaseModel):
    id: str
    summary: str
    route: str
    labels: list[str]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/summarise", response_model=AlertSummary)
def summarise(alert: Alert):
    summary = f"[{alert.severity}] {alert.title} :: {alert.description[:200]}"
    labels: list[str] = []
    sev = alert.severity.lower()
    if sev in ("sev0", "sev1", "critical"):
        labels.append("high-priority")
        route = "platform-oncall"
    elif sev in ("sev2", "warning"):
        labels.append("medium-priority")
        route = "service-team"
    else:
        labels.append("low-priority")
        route = "backlog"

    return AlertSummary(id=alert.id, summary=summary, route=route, labels=labels)

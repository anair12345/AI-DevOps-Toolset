from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date

app = FastAPI(title="Cost Drift Watcher", version="1.0.0")


class CostDriftRequest(BaseModel):
    subscription_id: str
    lookback_days: int = 30
    threshold_percent: float = 20.0
    tag_filter: dict[str, str] | None = None


class CostDriftItem(BaseModel):
    resource_id: str
    previous_avg: float
    current_avg: float
    drift_percent: float
    tags: dict[str, str] | None = None
    suggestion: str


class CostDriftResult(BaseModel):
    subscription_id: str
    as_of: date
    items: list[CostDriftItem]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/analyse", response_model=CostDriftResult)
def analyse(req: CostDriftRequest):
    resource_id = (
        f"/subscriptions/{req.subscription_id}/resourceGroups/rg-sample/providers/"
        "Microsoft.Compute/virtualMachines/vm-sample"
    )
    prev = 100.0
    current = 140.0
    drift = ((current - prev) / prev) * 100

    items: list[CostDriftItem] = []
    if drift >= req.threshold_percent:
        items.append(
            CostDriftItem(
                resource_id=resource_id,
                previous_avg=prev,
                current_avg=current,
                drift_percent=drift,
                tags=req.tag_filter or {"env": "dev"},
                suggestion="Review sizing or schedule shutdown for non-business hours.",
            )
        )

    return CostDriftResult(subscription_id=req.subscription_id, as_of=date.today(), items=items)

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date, timedelta

app = FastAPI(title="Capacity Forecaster", version="1.0.0")


class CapacityForecastRequest(BaseModel):
    resource_id: str
    metric_name: str = "cpuPercent"
    horizon_days: int = 7


class ForecastPoint(BaseModel):
    date: date
    value: float


class CapacityForecastResult(BaseModel):
    resource_id: str
    metric_name: str
    points: list[ForecastPoint]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/forecast", response_model=CapacityForecastResult)
def forecast(req: CapacityForecastRequest):
    today = date.today()
    points: list[ForecastPoint] = []
    base = 60.0
    for i in range(req.horizon_days):
        points.append(ForecastPoint(date=today + timedelta(days=i), value=base + i * 1.5))

    return CapacityForecastResult(
        resource_id=req.resource_id,
        metric_name=req.metric_name,
        points=points,
    )

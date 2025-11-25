from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="DB Upgrade Orchestrator", version="1.0.0")


class DBUpgradeRequest(BaseModel):
    server_name: str
    database_name: str
    current_version: str
    target_version: str
    read_replica: bool = True


class DBUpgradeStep(BaseModel):
    order: int
    description: str


class DBUpgradePlan(BaseModel):
    server_name: str
    database_name: str
    current_version: str
    target_version: str
    steps: list[DBUpgradeStep]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/plan-upgrade", response_model=DBUpgradePlan)
def plan_upgrade(req: DBUpgradeRequest):
    steps = [
        DBUpgradeStep(order=1, description="Take baseline backup and verify restore procedure."),
        DBUpgradeStep(order=2, description="Create or validate read replica (if enabled)."),
        DBUpgradeStep(order=3, description="Run pre-upgrade compatibility checks."),
        DBUpgradeStep(order=4, description=f"Upgrade server to version {req.target_version}."),
        DBUpgradeStep(order=5, description="Run post-upgrade health checks and performance tests."),
        DBUpgradeStep(order=6, description="Promote replica / reconfigure connections if needed."),
    ]
    return DBUpgradePlan(
        server_name=req.server_name,
        database_name=req.database_name,
        current_version=req.current_version,
        target_version=req.target_version,
        steps=steps,
    )

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Access Review Bot", version="1.0.0")


class AccessReviewRequest(BaseModel):
    scope: str
    inactivity_days_threshold: int = 90


class PrincipalAccess(BaseModel):
    principal_id: str
    display_name: str | None
    last_activity_days_ago: int
    recommended_action: str


class AccessReviewResult(BaseModel):
    scope: str
    dormant_principals: list[PrincipalAccess]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/review", response_model=AccessReviewResult)
def review(req: AccessReviewRequest):
    dormant = [
        PrincipalAccess(
            principal_id="00000000-0000-0000-0000-000000000001",
            display_name="sample-user",
            last_activity_days_ago=req.inactivity_days_threshold + 10,
            recommended_action="Revoke or downgrade role.",
        )
    ]
    return AccessReviewResult(scope=req.scope, dormant_principals=dormant)

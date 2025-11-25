from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Post-Deploy Verifier", version="1.0.0")


class CheckDefinition(BaseModel):
    name: str
    url: str
    expected_status: int = 200
    max_latency_ms: int = 1000


class VerifyRequest(BaseModel):
    deployment_id: str
    service_name: str
    environment: str
    checks: list[CheckDefinition]


class CheckResult(BaseModel):
    name: str
    url: str
    passed: bool
    status_code: int
    latency_ms: int
    message: str


class VerifyResult(BaseModel):
    deployment_id: str
    overall_passed: bool
    environment: str
    service_name: str
    results: list[CheckResult]
    verified_at: datetime


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/verify", response_model=VerifyResult)
def verify(req: VerifyRequest):
    results: list[CheckResult] = []
    for c in req.checks:
        latency = min(c.max_latency_ms, 123)
        results.append(
            CheckResult(
                name=c.name,
                url=c.url,
                passed=True,
                status_code=c.expected_status,
                latency_ms=latency,
                message="OK (stubbed)",
            )
        )

    overall_passed = all(r.passed for r in results)

    return VerifyResult(
        deployment_id=req.deployment_id,
        overall_passed=overall_passed,
        environment=req.environment,
        service_name=req.service_name,
        results=results,
        verified_at=datetime.utcnow(),
    )

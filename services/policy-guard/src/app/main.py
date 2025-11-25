from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Policy Guard", version="1.0.0")


class PolicyGuardRequest(BaseModel):
    scope: str
    evaluate_tags: bool = True


class NonCompliantResource(BaseModel):
    resource_id: str
    policy_name: str
    description: str
    severity: str
    suggested_fix: str


class PolicyGuardResult(BaseModel):
    scope: str
    non_compliant: list[NonCompliantResource]
    auto_pr_possible: bool


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/evaluate", response_model=PolicyGuardResult)
def evaluate(req: PolicyGuardRequest):
    non_compliant = [
        NonCompliantResource(
            resource_id=f"{req.scope}/providers/Microsoft.Compute/virtualMachines/vm1",
            policy_name="Enforce tags",
            description="Resource missing required 'env' tag.",
            severity="medium",
            suggested_fix="Add tag env=dev (or appropriate environment).",
        )
    ]

    return PolicyGuardResult(
        scope=req.scope,
        non_compliant=non_compliant,
        auto_pr_possible=True,
    )

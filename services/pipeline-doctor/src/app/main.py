from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Pipeline Doctor", version="1.0.0")


class PipelineLogRequest(BaseModel):
    pipeline_name: str
    run_id: str
    log_text: str


class PipelineIssue(BaseModel):
    line: int
    snippet: str
    suggestion: str


class PipelineAnalysisResult(BaseModel):
    pipeline_name: str
    run_id: str
    issues: list[PipelineIssue]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/analyse-log", response_model=PipelineAnalysisResult)
def analyse_log(req: PipelineLogRequest):
    issues: list[PipelineIssue] = []
    lines = req.log_text.splitlines()
    for i, line in enumerate(lines, start=1):
        if "ERROR" in line or "Error" in line:
            issues.append(
                PipelineIssue(
                    line=i,
                    snippet=line[:200],
                    suggestion="Check the step around this line; consider enabling verbose logging or validating credentials.",
                )
            )

    return PipelineAnalysisResult(
        pipeline_name=req.pipeline_name,
        run_id=req.run_id,
        issues=issues,
    )

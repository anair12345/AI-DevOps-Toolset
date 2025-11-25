from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Release Notes Generator", version="1.0.0")


class ReleaseNotesRequest(BaseModel):
    repo: str
    from_ref: str
    to_ref: str
    include_tests: bool = True
    include_work_items: bool = True


class ReleaseNotesResult(BaseModel):
    markdown: str
    risk_score: int
    highlights: list[str]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/generate", response_model=ReleaseNotesResult)
def generate(req: ReleaseNotesRequest):
    markdown = f"""# Release Notes

**Repository:** {req.repo}  
**Range:** {req.from_ref} → {req.to_ref}

## Changes
- Feature: Sample feature A
- Bugfix: Fix for issue B

## Risks
- Schema changes may impact downstream services.

"""

    risk_score = 65
    highlights = [
        "Includes schema changes.",
        "Multiple services touched in single release.",
    ]

    return ReleaseNotesResult(markdown=markdown, risk_score=risk_score, highlights=highlights)

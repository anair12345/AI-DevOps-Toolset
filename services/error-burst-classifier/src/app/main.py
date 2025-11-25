from fastapi import FastAPI
from pydantic import BaseModel
from collections import defaultdict

app = FastAPI(title="Error Burst Classifier", version="1.0.0")


class LogEntry(BaseModel):
    timestamp: str
    message: str


class Cluster(BaseModel):
    pattern: str
    count: int
    sample_messages: list[str]


class ClassificationRequest(BaseModel):
    logs: list[LogEntry]


class ClassificationResult(BaseModel):
    clusters: list[Cluster]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/cluster", response_model=ClassificationResult)
def cluster(req: ClassificationRequest):
    buckets: dict[str, list[str]] = defaultdict(list)
    for entry in req.logs:
        key = entry.message.split(":")[0][:80]
        buckets[key].append(entry.message)

    clusters: list[Cluster] = []
    for pattern, msgs in buckets.items():
        clusters.append(
            Cluster(
                pattern=pattern,
                count=len(msgs),
                sample_messages=msgs[:3],
            )
        )

    return ClassificationResult(clusters=clusters)

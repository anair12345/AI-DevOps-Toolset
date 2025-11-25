from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI(title="Log PII Scrubber", version="1.0.0")


class PiiScrubRequest(BaseModel):
    text: str


class PiiScrubResult(BaseModel):
    redacted_text: str
    detected_types: list[str]


_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_PHONE_RE = re.compile(r"\+?\d[\d\-\s]{7,}\d")


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/scrub", response_model=PiiScrubResult)
def scrub(req: PiiScrubRequest):
    detected: set[str] = set()

    def _email_repl(match: re.Match):
        detected.add("email")
        return "<redacted-email>"

    def _phone_repl(match: re.Match):
        detected.add("phone")
        return "<redacted-phone>"

    text = _EMAIL_RE.sub(_email_repl, req.text)
    text = _PHONE_RE.sub(_phone_repl, text)

    return PiiScrubResult(redacted_text=text, detected_types=sorted(detected))

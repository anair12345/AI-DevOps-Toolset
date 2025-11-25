from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI(title="Secret Expiry Sentry", version="1.0.0")


class SecretScanRequest(BaseModel):
    vault_name: str
    days_ahead: int = 14
    auto_rotate: bool = False


class SecretExpiryItem(BaseModel):
    name: str
    type: str
    expires_on: datetime
    will_expire_within_days: int
    auto_rotate_attempted: bool
    auto_rotate_status: str | None = None


class SecretScanResult(BaseModel):
    vault_name: str
    scanned_at: datetime
    items: list[SecretExpiryItem]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/scan", response_model=SecretScanResult)
def scan(req: SecretScanRequest):
    now = datetime.utcnow()
    dummy_expiry = now + timedelta(days=req.days_ahead - 1)
    will_expire_within = (dummy_expiry - now).days

    auto_rotate_attempted = req.auto_rotate
    auto_rotate_status = "not-requested"
    if req.auto_rotate:
        auto_rotate_status = "scheduled"

    item = SecretExpiryItem(
        name="sample-cert",
        type="certificate",
        expires_on=dummy_expiry,
        will_expire_within_days=will_expire_within,
        auto_rotate_attempted=auto_rotate_attempted,
        auto_rotate_status=auto_rotate_status,
    )

    return SecretScanResult(vault_name=req.vault_name, scanned_at=now, items=[item])

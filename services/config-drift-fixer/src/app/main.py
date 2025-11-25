from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Config Drift Fixer", version="1.0.0")


class ConfigDriftRequest(BaseModel):
    live_config: dict
    desired_config: dict


class ConfigDiffItem(BaseModel):
    path: str
    live_value: str | None
    desired_value: str | None
    change_type: str


class ConfigDriftResult(BaseModel):
    drift_detected: bool
    diffs: list[ConfigDiffItem]


def _diff_dict(prefix: str, live: dict, desired: dict) -> list[ConfigDiffItem]:
    diffs: list[ConfigDiffItem] = []
    keys = set(live.keys()) | set(desired.keys())
    for key in sorted(keys):
        path = f"{prefix}.{key}" if prefix else key
        if key not in live:
            diffs.append(
                ConfigDiffItem(
                    path=path,
                    live_value=None,
                    desired_value=str(desired[key]),
                    change_type="add",
                )
            )
        elif key not in desired:
            diffs.append(
                ConfigDiffItem(
                    path=path,
                    live_value=str(live[key]),
                    desired_value=None,
                    change_type="remove",
                )
            )
        else:
            lv = live[key]
            dv = desired[key]
            if isinstance(lv, dict) and isinstance(dv, dict):
                diffs.extend(_diff_dict(path, lv, dv))
            elif lv != dv:
                diffs.append(
                    ConfigDiffItem(
                        path=path,
                        live_value=str(lv),
                        desired_value=str(dv),
                        change_type="update",
                    )
                )
    return diffs


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/compare", response_model=ConfigDriftResult)
def compare(req: ConfigDriftRequest):
    diffs = _diff_dict("", req.live_config, req.desired_config)
    return ConfigDriftResult(drift_detected=len(diffs) > 0, diffs=diffs)

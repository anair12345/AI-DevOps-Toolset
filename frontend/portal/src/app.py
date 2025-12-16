import os
import json
import requests
import streamlit as st

st.set_page_config(page_title="DevOps AI Toolkit Portal", layout="wide")
st.title("DevOps AI Toolkit Portal")

# Base URL: if running in-cluster, set TOOLKIT_BASE_URL to an ingress/gateway.
# If port-forwarding a specific service, set it to http://localhost:8080
base_url = os.getenv("TOOLKIT_BASE_URL", "http://localhost:8080").rstrip("/")

st.sidebar.header("Connection")
base_url = st.sidebar.text_input("Base URL", base_url)

st.sidebar.markdown("**Tip:** Port-forward a service like `kubectl port-forward svc/alert-summariser 8080:80` and set Base URL to `http://localhost:8080`.")

services = [
  ("alert-summariser", "POST", "/summarise"),
  ("runbook-copilot", "POST", "/plan"),
  ("incident-rca-builder", "POST", "/build"),
  ("post-deploy-verifier", "POST", "/verify"),
  ("cost-drift-watcher", "POST", "/analyse"),
  ("secret-expiry-sentry", "POST", "/scan"),
  ("policy-guard", "POST", "/evaluate"),
  ("container-cve-gate", "POST", "/evaluate-image"),
  ("db-upgrade-orchestrator", "POST", "/plan-upgrade"),
  ("release-notes-generator", "POST", "/generate"),
  ("canary-controller", "POST", "/decide"),
  ("error-burst-classifier", "POST", "/cluster"),
  ("pipeline-doctor", "POST", "/analyse-log"),
  ("capacity-forecaster", "POST", "/forecast"),
  ("chaos-scheduler", "POST", "/plan-experiment"),
  ("slo-keeper", "POST", "/compute"),
  ("access-review-bot", "POST", "/review"),
  ("dr-drill-coach", "POST", "/score"),
  ("log-pii-scrubber", "POST", "/scrub"),
  ("config-drift-fixer", "POST", "/compare"),
]

svc = st.selectbox("Choose a service", services, format_func=lambda x: f"{x[0]}  ({x[1]} {x[2]})")
svc_name, method, path = svc

st.subheader(f"Request builder: {svc_name}")

# Default payloads (minimal working examples)
defaults = {
  "alert-summariser": {"id":"a1","title":"CPU high","description":"CPU over 90% for 5 mins","severity":"sev2","raw":{"example":True}},
  "runbook-copilot": {"prompt":"restart service","runbook_id":"rb-restart-web","dry_run":True,"requested_by":"akhil"},
  "incident-rca-builder": {"incident_id":"inc-123","from_time":"2025-12-16T00:00:00Z","to_time":"2025-12-16T01:00:00Z","services":["api","worker"]},
  "post-deploy-verifier": {"deployment_id":"d-1","service_name":"api","environment":"dev","checks":[{"name":"health","url":"http://api/healthz","expected_status":200,"max_latency_ms":1000}]},
  "cost-drift-watcher": {"subscription_id":"00000000-0000-0000-0000-000000000000","lookback_days":30,"threshold_percent":20,"tag_filter":{"env":"dev"}},
  "secret-expiry-sentry": {"vault_name":"kv-sample","days_ahead":14,"auto_rotate":False},
  "policy-guard": {"scope":"/subscriptions/0000/resourceGroups/rg-sample","evaluate_tags":True},
  "container-cve-gate": {"image":"acr.azurecr.io/app:123","max_allowed_severity":"medium"},
  "db-upgrade-orchestrator": {"server_name":"pg-srv","database_name":"db","current_version":"11","target_version":"16","read_replica":True},
  "release-notes-generator": {"repo":"Org/Repo","from_ref":"v1.0.0","to_ref":"v1.1.0","include_tests":True,"include_work_items":True},
  "canary-controller": {"app_name":"api","stable_weight":90,"canary_weight":10,"metrics":{"error_rate":0.005,"latency_p95_ms":220,"cpu_percent":55}},
  "error-burst-classifier": {"logs":[{"timestamp":"2025-12-16T00:00:00Z","message":"TimeoutError: DB timed out"},{"timestamp":"2025-12-16T00:01:00Z","message":"TimeoutError: DB timed out"}]},
  "pipeline-doctor": {"pipeline_name":"build-api","run_id":"42","log_text":"Step 1\nERROR: failed to login\nStep 2"},
  "capacity-forecaster": {"resource_id":"/subscriptions/0000/resourceGroups/rg/providers/Microsoft.ContainerService/managedClusters/aks","metric_name":"cpuPercent","horizon_days":7},
  "chaos-scheduler": {"service_name":"api","blast_radius":"small","duration_minutes":15,"earliest_start":None},
  "slo-keeper": {"service_name":"api","target_slo_percent":99.9,"total_events":10000,"bad_events":5},
  "access-review-bot": {"scope":"/subscriptions/0000","inactivity_days_threshold":90},
  "dr-drill-coach": {"drill_id":"dr-1","start_time":"2025-12-16T00:00:00Z","end_time":"2025-12-16T00:20:00Z","rto_target_minutes":30,"rpo_target_minutes":15},
  "log-pii-scrubber": {"text":"Contact me at test@example.com or +44 7700 900123"},
  "config-drift-fixer": {"live_config":{"a":1,"b":2},"desired_config":{"a":1,"b":3,"c":4}},
}

payload = st.text_area("JSON payload", value=json.dumps(defaults.get(svc_name, {}), indent=2), height=220)

col1, col2 = st.columns([1, 1])
with col1:
  if st.button("Call service"):
    try:
      data = json.loads(payload) if payload.strip() else {}
    except Exception as e:
      st.error(f"Invalid JSON: {e}")
      st.stop()

    # Services are standalone, so base_url should be the service root.
    url = f"{base_url}{path}"
    try:
      resp = requests.request(method, url, json=data, timeout=20)
      st.write("Status:", resp.status_code)
      try:
        st.json(resp.json())
      except Exception:
        st.text(resp.text)
    except Exception as e:
      st.error(f"Request failed: {e}")

with col2:
  st.markdown("### How to use")
  st.markdown(
    """1. Port-forward a service or expose it via ingress.  
2. Set **Base URL** to the service base (e.g., `http://localhost:8080`).  
3. Select service → tweak JSON → click **Call service**."""
  )

# DevOps AI Toolkit (20 Microservices) — Local Deployment Guide

This repo contains **20 FastAPI microservices** (Python) + a **Streamlit portal frontend**, deployable locally to Kubernetes using **Helm**, with scripts for **KIND** (recommended) and **Minikube**. Azure IaC/pipelines also exist, but this README focuses on **local dry-run**.

---

## What you get

* `services/*` — 20 microservices, each with:

  * `src/app/main.py` (FastAPI)
  * `Dockerfile`
  * `requirements.txt`
  * `helm/chart/` (Helm chart)
  * `helm/chart/values.local.yaml` (local override)
* `frontend/portal` — Streamlit UI + Dockerfile + Helm chart
* `infra/local` — local scripts for KIND / Minikube
* `Makefile` + `Taskfile.yml` — convenience commands
* `infra/` — Terraform + Azure DevOps pipeline (Azure deployment)

---

## Local deployment options

### Recommended: KIND

Best balance of:

* AKS-like behavior
* fast startup
* easy local image loading

### Alternative: Minikube

Good if you already use it and prefer its addons.

---

# Prerequisites

## OS assumptions

* Windows 10/11 with **WSL2 Ubuntu** (recommended), or native Linux/macOS.
* Docker runs via **Docker Desktop** on Windows.

> If you’re on Windows, do this in WSL2 to avoid PowerShell execution-policy/tooling friction.

---

## Required tools (KIND path)

### 1) Docker Desktop (Windows)

* Install Docker Desktop
* **Enable WSL integration**:

  * Docker Desktop → Settings → Resources → WSL Integration
  * ✅ Enable “integration with my default WSL distro”
  * ✅ Toggle your distro (e.g. Ubuntu)
  * Apply & Restart

### 2) In WSL (Ubuntu) install CLI tools

Run:

```bash
sudo apt update && sudo apt upgrade -y

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/kubectl

# helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

### 3) Verify installs

```bash
docker version
kubectl version --client
helm version
kind version
```

---

## Optional tools

### Taskfile (optional)

If you want to use `task ...` commands:

```bash
# Ubuntu/WSL (using snap)
sudo snap install task --classic
task --version
```

Or just use `make` / direct scripts.

### Make (optional)

Most WSL distros already have make. If not:

```bash
sudo apt install -y make
make --version
```

---

# Repo setup

## 1) Ensure scripts are executable

From repo root:

```bash
chmod +x infra/local/scripts/*.sh
```

---

# Local deploy — KIND (recommended)

## Deploy ONE service

Example:

```bash
./infra/local/scripts/run-kind.sh alert-summariser
```

What it does:

* Creates a KIND cluster `devops-ai` (if missing)
* Builds the Docker image `alert-summariser:local`
* Loads the image into KIND
* Helm installs using `values.local.yaml`

## Deploy ALL services (20)

```bash
./infra/local/scripts/run-kind.sh all
```

## Check status

```bash
kubectl get nodes
kubectl get pods
kubectl get svc
```

---

# Local deploy — Minikube (alternative)

## Start Minikube

```bash
minikube start
```

## Deploy one service

```bash
./infra/local/scripts/run-minikube.sh alert-summariser
```

## Deploy all services

```bash
./infra/local/scripts/run-minikube.sh all
```

---

# Accessing services locally

Services are deployed as **ClusterIP** by default (no ingress), so you access them via **port-forward**.

## Example: alert-summariser

```bash
kubectl port-forward svc/alert-summariser 8080:80
```

Then:

```bash
curl http://localhost:8080/healthz
```

---

# Deploy + access the Portal (Streamlit frontend)

## 1) Deploy portal to KIND

```bash
make portal-kind
```

(Alternative)

```bash
task portal:kind
```

## 2) Port-forward the portal

```bash
kubectl port-forward svc/devops-ai-portal 8501:80
```

Open:

* `http://localhost:8501`

### How the portal calls services (important)

The portal calls **one service base URL at a time**.

**Simplest flow:**

1. Port-forward the service you want:

   ```bash
   kubectl port-forward svc/alert-summariser 8080:80
   ```
2. In the portal sidebar, set **Base URL**:

   * `http://localhost:8080`
3. Select a service → edit JSON → **Call service**

> This is intentional for local dry-run. A later upgrade is adding ingress/gateway so the portal can call all services without port-forwarding.

---

# Using Makefile / Taskfile

## Deploy one service to KIND

```bash
make kind-deploy-one SERVICE=alert-summariser
```

## Deploy all services to KIND

```bash
make kind-deploy-all
```

## Deploy portal to KIND

```bash
make portal-kind
```

### Taskfile examples

```bash
task kind:deploy-one SERVICE=alert-summariser
task kind:deploy-all
task portal:kind
```

---

# Local config that matters

Each service chart has:

* `services/<svc>/helm/chart/values.yaml` (default)
* `services/<svc>/helm/chart/values.local.yaml` (**local override**)

Local override sets:

* `image.repository: <svc>`
* `image.tag: local`
* `replicaCount: 1`

So the local scripts can:

* build `svc:local`
* load into cluster
* deploy with Helm using the local tag

---

# Troubleshooting

## “docker could not be found in this WSL distro”

Fix:

* Docker Desktop → Settings → Resources → WSL Integration → enable Ubuntu → Apply & Restart
* In Windows PowerShell (Admin): `wsl --shutdown`
* Reopen Ubuntu and run `docker version`

## Pods stuck in ImagePullBackOff

Cause: image not available in cluster.
Fix:

* KIND: rerun script (it loads images into KIND)
* Verify image was loaded:

  ```bash
  kind get clusters
  docker images | head
  ```
* Re-deploy:

  ```bash
  ./infra/local/scripts/run-kind.sh alert-summariser
  ```

## Service exists but port-forward fails

Check service name:

```bash
kubectl get svc
```

## Helm says release already exists

That’s fine—Helm is idempotent. Use:

```bash
helm upgrade --install <name> <chart>
```

---

# Next upgrades (optional)

* Add **Ingress-NGINX** and route services under a single host
* Add a simple **gateway** so the portal can call `/api/<svc>/...`
* Wire Azure SDK + Azure OpenAI into selected services
* Add OpenTelemetry / Prometheus metrics
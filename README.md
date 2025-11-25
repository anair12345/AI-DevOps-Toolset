# DevOps AI Toolkit - 20 Microservices

This repository contains 20 FastAPI-based Python microservices, each packaged for deployment
to Azure Kubernetes Service (AKS) using Docker and Helm, plus Terraform IaC and Azure DevOps pipelines.

## Structure

- `infra/` - Terraform definitions for AKS, ACR, and Log Analytics, plus `azure-pipelines-infra.yml`.
- `services/<service-name>/`
  - `src/app/main.py` - FastAPI app for the service.
  - `requirements.txt` - Python dependencies.
  - `Dockerfile` - Container image build definition.
  - `helm/chart/` - Helm chart with `values.yaml`, `templates/deployment.yaml`, and `templates/service.yaml`.
  - `azure-pipelines-app.yml` - Azure DevOps pipeline for build & deploy.

Update `ACR_NAME`, `AKS_RG`, and `AKS_NAME` variables in each app pipeline and infra pipeline
to match your environment, then run the infra pipeline first to provision AKS/ACR.

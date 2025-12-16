SHELL := /usr/bin/env bash

KIND_CLUSTER ?= devops-ai

.PHONY: kind-up kind-deploy-one kind-deploy-all minikube-deploy-one minikube-deploy-all portal-kind portal-minikube

kind-up:
	./infra/local/scripts/run-kind.sh all || true

kind-deploy-one:
	./infra/local/scripts/run-kind.sh $(SERVICE)

kind-deploy-all:
	./infra/local/scripts/run-kind.sh all

minikube-deploy-one:
	./infra/local/scripts/run-minikube.sh $(SERVICE)

minikube-deploy-all:
	./infra/local/scripts/run-minikube.sh all

portal-kind:
	@echo "Building portal image"
	cd frontend/portal && docker build -t devops-ai-portal:local .
	kind load docker-image devops-ai-portal:local --name $(KIND_CLUSTER)
	helm upgrade --install devops-ai-portal ./frontend/portal/helm/chart \
		--set image.repository=devops-ai-portal \
		--set image.tag=local

portal-minikube:
	@echo "Building portal image (minikube docker-env required)"
	cd frontend/portal && docker build -t devops-ai-portal:local .
	helm upgrade --install devops-ai-portal ./frontend/portal/helm/chart \
		--set image.repository=devops-ai-portal \
		--set image.tag=local

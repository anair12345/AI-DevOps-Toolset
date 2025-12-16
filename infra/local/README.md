# Local Kubernetes Dry-Run

You can dry-run these microservices locally using either KIND (recommended) or Minikube.

## KIND (recommended)
Prereqs: docker, kind, kubectl, helm

From repo root:
- Deploy one service:
  `./infra/local/scripts/run-kind.sh alert-summariser`
- Deploy all services:
  `./infra/local/scripts/run-kind.sh all`

## Minikube
Prereqs: minikube, docker, kubectl, helm

From repo root:
- Deploy one service:
  `./infra/local/scripts/run-minikube.sh alert-summariser`
- Deploy all services:
  `./infra/local/scripts/run-minikube.sh all`

## Access a service
Port-forward:
`kubectl port-forward svc/alert-summariser 8080:80`
Then:
`curl http://localhost:8080/healthz`

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SERVICES_DIR="$ROOT_DIR/services"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1"; exit 1; }; }

need minikube
need kubectl
need helm
need docker

echo "==> Starting minikube (if not running)"
minikube status >/dev/null 2>&1 || minikube start

echo "==> Pointing docker CLI at minikube's docker daemon"
eval "$(minikube docker-env)"

SERVICE="${1:-}"
if [[ -z "$SERVICE" ]]; then
  echo "Usage: $0 <service-name|all>"
  echo "Example: $0 alert-summariser"
  echo "Example: $0 all"
  exit 1
fi

build_and_deploy_one() {
  local svc="$1"
  echo "==> Building $svc"
  ( cd "$SERVICES_DIR/$svc" && docker build -t "${svc}:local" . )
  echo "==> Deploying via Helm"
  helm upgrade --install "$svc" "$SERVICES_DIR/$svc/helm/chart" \
    --values "$SERVICES_DIR/$svc/helm/chart/values.local.yaml" \
    --set name="$svc" \
    --set image.repository="$svc" \
    --set image.tag="local"
}

if [[ "$SERVICE" == "all" ]]; then
  for dir in "$SERVICES_DIR"/*; do
    [[ -d "$dir" ]] || continue
    build_and_deploy_one "$(basename "$dir")"
  done
else
  build_and_deploy_one "$SERVICE"
fi

echo "==> Done"
echo "Tip: port-forward a service:"
echo "  kubectl port-forward svc/<service-name> 8080:80"

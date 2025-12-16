#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-devops-ai}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SERVICES_DIR="$ROOT_DIR/services"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1"; exit 1; }; }

need docker
need kind
need kubectl
need helm

echo "==> Ensuring kind cluster '$CLUSTER_NAME' exists"
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  kind create cluster --name "$CLUSTER_NAME" --config "$ROOT_DIR/infra/local/kind/kind-config.yaml"
else
  echo "Cluster already exists."
fi

kubectl config use-context "kind-${CLUSTER_NAME}" >/dev/null

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
  echo "==> Loading image into kind"
  kind load docker-image "${svc}:local" --name "$CLUSTER_NAME"
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

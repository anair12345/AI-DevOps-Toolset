Param(
  [Parameter(Mandatory=$true)][string]$Service,
  [string]$ClusterName = "devops-ai"
)

function Need($cmd) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    Write-Error "Missing dependency: $cmd"
    exit 1
  }
}

Need docker
Need kind
Need kubectl
Need helm

$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$ServicesDir = Join-Path $RootDir "services"
$KindConfig = Join-Path $RootDir "infra\local\kind\kind-config.yaml"

Write-Host "==> Ensuring kind cluster '$ClusterName' exists"
$clusters = kind get clusters
if ($clusters -notcontains $ClusterName) {
  kind create cluster --name $ClusterName --config $KindConfig
} else {
  Write-Host "Cluster already exists."
}

kubectl config use-context ("kind-" + $ClusterName) | Out-Null

function BuildAndDeployOne($svc) {
  Write-Host "==> Building $svc"
  Push-Location (Join-Path $ServicesDir $svc)
  docker build -t ($svc + ":local") .
  Pop-Location

  Write-Host "==> Loading image into kind"
  kind load docker-image ($svc + ":local") --name $ClusterName

  Write-Host "==> Deploying via Helm"
  $chart = Join-Path $ServicesDir "$svc\helm\chart"
  $valuesLocal = Join-Path $chart "values.local.yaml"
  helm upgrade --install $svc $chart `
    --values $valuesLocal `
    --set name=$svc `
    --set image.repository=$svc `
    --set image.tag=local
}

if ($Service -eq "all") {
  Get-ChildItem $ServicesDir -Directory | ForEach-Object { BuildAndDeployOne $_.Name }
} else {
  BuildAndDeployOne $Service
}

Write-Host "==> Done"
Write-Host "Tip: kubectl port-forward svc/<service-name> 8080:80"

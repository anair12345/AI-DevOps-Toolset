locals {
  suffix  = "${var.name_prefix}-${var.env}"
  rg_name = coalesce(var.rg_name, "rg-${local.suffix}-platform")
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = var.location
  tags     = var.tags
}

resource "random_string" "acr" {
  length  = 8
  upper   = false
  special = false
}

resource "azurerm_container_registry" "acr" {
  name                = "acr${random_string.acr.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Premium"
  admin_enabled       = false
  tags                = var.tags
}

resource "azurerm_log_analytics_workspace" "law" {
  name                = "log-${local.suffix}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "aks-${local.suffix}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "aks-${local.suffix}"

  oidc_issuer_enabled      = true
  workload_identity_enabled = true

  default_node_pool {
    name                         = "system"
    node_count                   = var.aks_node_count
    vm_size                      = var.aks_node_size
    type                         = "VirtualMachineScaleSets"
    only_critical_addons_enabled = true
    orchestrator_version         = "1.30"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
  }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
  }

  tags = var.tags
}

resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
}

output "rg_name"  { value = azurerm_resource_group.rg.name }
output "acr_name" { value = azurerm_container_registry.acr.name }
output "aks_name" { value = azurerm_kubernetes_cluster.aks.name }
output "aks_rg"   { value = azurerm_kubernetes_cluster.aks.resource_group_name }

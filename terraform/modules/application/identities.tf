locals {
  user_managed_identity_prefix = lower("umi-aca-${var.env_name}")
}

# Create a User-Assigned Managed Identity for the web App
resource "azurerm_user_assigned_identity" "web_app_identity" {
  name                = "${local.user_managed_identity_prefix}-web"
  resource_group_name = var.resource_group_name
  location            = var.location

  lifecycle {
    ignore_changes = [tags]
  }
}

# Create a User-Assigned Managed Identity for the worker App
resource "azurerm_user_assigned_identity" "worker_app_identity" {
  name                = "${local.user_managed_identity_prefix}-worker"
  resource_group_name = var.resource_group_name
  location            = var.location

  lifecycle {
    ignore_changes = [tags]
  }
}

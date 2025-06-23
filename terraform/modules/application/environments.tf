# The Container App Environment for public-facing web app(s)
resource "azurerm_container_app_environment" "public" {
  name                           = "${var.container_app_environment_prefix}-public"
  location                       = var.location
  resource_group_name            = var.resource_group_name
  log_analytics_workspace_id     = var.log_analytics_workspace_id
  infrastructure_subnet_id       = var.public_subnet_id
  internal_load_balancer_enabled = true

  # Add a Consumption profile
  # This also enables Workload Profiles, which is required for the advanced networking
  # with NAT gateway etc.
  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
    minimum_count         = 0
    maximum_count         = 0
  }

  lifecycle {
    ignore_changes = [
      # managed by Azure, prevent replacement of the environment
      infrastructure_resource_group_name,
      tags
    ]
  }
}

# The Container App Environment for the background worker application
resource "azurerm_container_app_environment" "worker" {
  name                       = "${var.container_app_environment_prefix}-worker"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = var.log_analytics_workspace_id
  infrastructure_subnet_id   = var.worker_subnet_id

  # Add a Consumption profile
  # This also enables Workload Profiles, which is required for the advanced networking
  # with NAT gateway etc.
  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
    minimum_count         = 0
    maximum_count         = 0
  }

  lifecycle {
    ignore_changes = [
      # managed by Azure, prevent replacement of the environment
      infrastructure_resource_group_name,
      tags
    ]
  }
}

# Mounts the 'config' file share to the public Container App Environment.
resource "azurerm_container_app_environment_storage" "config" {
  account_name                 = var.storage_account_name
  access_key                   = var.storage_account_primary_access_key
  access_mode                  = "ReadOnly"
  container_app_environment_id = azurerm_container_app_environment.public.id
  name                         = var.storage_share_names.config
  share_name                   = var.storage_share_names.config
}

# Mounts the 'requests' file share to the worker Container App Environment.
resource "azurerm_container_app_environment_storage" "requests" {
  account_name                 = var.storage_account_name
  access_key                   = var.storage_account_primary_access_key
  access_mode                  = "ReadWrite"
  container_app_environment_id = azurerm_container_app_environment.worker.id
  name                         = var.storage_share_names.requests
  share_name                   = var.storage_share_names.requests
}

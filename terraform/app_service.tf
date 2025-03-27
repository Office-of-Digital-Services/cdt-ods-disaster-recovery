resource "azurerm_service_plan" "main" {
  name                = "ASP-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "B1"

  lifecycle {
    ignore_changes = [tags]
  }
}

locals {
  data_mount = "/cdt/app/data"
}

resource "azurerm_linux_web_app" "main" {
  name                      = "AS-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  location                  = data.azurerm_resource_group.main.location
  resource_group_name       = data.azurerm_resource_group.main.name
  service_plan_id           = azurerm_service_plan.main.id
  https_only                = true
  virtual_network_subnet_id = local.subnet_id

  site_config {
    ftps_state             = "Disabled"
    vnet_route_all_enabled = true
  }

  identity {
    identity_ids = []
    type         = "SystemAssigned"
  }

  logs {
    detailed_error_messages = false
    failed_request_tracing  = false

    http_logs {
      file_system {
        retention_in_days = 99999
        retention_in_mb   = 100
      }
    }
  }

  app_settings = {
    "WEBSITE_TIME_ZONE"                   = "America/Los_Angeles",
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "true",
    "WEBSITES_PORT"                       = "8000",

    # Requests
    "REQUESTS_CONNECT_TIMEOUT" = "${local.secret_prefix}requests-connect-timeout)",
    "REQUESTS_READ_TIMEOUT"    = "${local.secret_prefix}requests-read-timeout)",

    # Django settings
    "DJANGO_ALLOWED_HOSTS" = "${local.secret_prefix}django-allowed-hosts)",
    "DJANGO_STORAGE_DIR"   = "${local.secret_prefix}django-storage-dir)",
    "DJANGO_DEBUG"         = local.is_prod ? null : "${local.secret_prefix}django-debug)",
    "DJANGO_LOG_LEVEL"     = "${local.secret_prefix}django-log-level)",

    "DJANGO_SECRET_KEY"      = "${local.secret_prefix}django-secret-key)",
    "DJANGO_TRUSTED_ORIGINS" = "${local.secret_prefix}django-trusted-origins)",

    "HEALTHCHECK_USER_AGENTS" = local.is_dev ? null : "${local.secret_prefix}healthcheck-user-agents)",
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags]
  }
}

resource "azurerm_app_service_custom_hostname_binding" "main" {
  hostname            = local.hostname
  app_service_name    = azurerm_linux_web_app.main.name
  resource_group_name = data.azurerm_resource_group.main.name
}

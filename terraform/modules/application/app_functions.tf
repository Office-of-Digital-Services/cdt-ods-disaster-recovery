# The functions app used for doing utility tasks using Azure Functions

 # A random key to secure the function's alert_to_slack endpoint
resource "random_string" "function_key" {
  length  = 32
  special = false
}

# Key Vault Secret
data "azurerm_key_vault_secret" "slack_webhook_url" {
  name         = "slack-webhook-url"
  key_vault_id = var.key_vault_id
}

# An API key for querying Application Insights Log search data
resource "azurerm_application_insights_api_key" "appi_api_key" {
  name                    = "functions-app-api-key"
  application_insights_id = var.application_insights_id
  read_permissions        = ["search"]
}

# Azure Container App hosting the Azure Functions
resource "azurerm_container_app" "functions" {
  name                         = "${var.container_app_prefix}-functions"
  container_app_environment_id = azurerm_container_app_environment.worker.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  max_inactive_revisions       = 10
  workload_profile_name        = "Consumption"

  identity {
    identity_ids = [azurerm_user_assigned_identity.functions_app_identity.id]
    type         = "UserAssigned"
  }

  # Secrets that will be injected as environment variables
  secret {
    name     = data.azurerm_key_vault_secret.slack_webhook_url.name
    key_vault_secret_id = "${var.key_vault_secret_uri_prefix}/${data.azurerm_key_vault_secret.slack_webhook_url.name}"
    identity = azurerm_user_assigned_identity.functions_app_identity.id
  }
  secret {
    name  = "alert-to-slack-function-key"
    value = random_string.function_key.result
  }
  secret {
    name = "appinsights-api-key"
    value = azurerm_application_insights_api_key.appi_api_key.api_key
  }

  ingress {
    external_enabled = true
    target_port      = 80 # Azure Functions' port
    transport        = "auto"
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "functions"
      image  = "ghcr.io/office-of-digital-services/cdt-ods-disaster-recovery-functions:${var.container_tag}" # pull out the common part of the image name to use it for web app too
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = var.application_insights_connection_string
      }
      env {
        name  = "AzureWebJobsStorage"
        value = var.storage_account_primary_connection_string
      }
      env {
        name        = "SLACK_WEBHOOK_URL"
        secret_name = data.azurerm_key_vault_secret.slack_webhook_url.name
      }
      # The Function's runtime key for the 'alert_to_slack' function.
      env {
        name        = "AZURE_FUNCTION_KEY"
        secret_name = "alert-to-slack-function-key"
      }
      env {
        name        = "APPINSIGHTS_API_KEY"
        secret_name = "appinsights-api-key"
      }
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

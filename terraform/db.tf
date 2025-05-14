locals {
  # Define secret names for clarity
  postgres_admin_login                = "postgres_admin"
  postgres_admin_password_secret_name = "postgres-admin-password"
}

# Generate a random password for PostgreSQL
resource "random_password" "postgres_admin_password" {
  length           = 32
  min_lower        = 4
  min_upper        = 4
  min_numeric      = 4
  min_special      = 4
  special          = true
  override_special = "_%@!-"
}

# Create the secret for PostgreSQL Admin Password using the generated password
resource "azurerm_key_vault_secret" "postgres_admin_password" {
  name         = local.postgres_admin_password_secret_name
  value        = random_password.postgres_admin_password.result
  key_vault_id = azurerm_key_vault.main.id
  content_type = "password"
  depends_on = [
    azurerm_key_vault.main,
    random_password.postgres_admin_password # Ensure password is generated first
  ]
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                = lower("adb-cdt-pub-vip-ddrc-${local.env_letter}-db")
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location
  sku_name            = "B_Standard_B1ms"
  storage_mb          = 32 * 1024
  storage_tier        = "P4"
  version             = "16"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  authentication {
    active_directory_auth_enabled = false
    password_auth_enabled         = true
  }
  public_network_access_enabled = true
  administrator_login           = local.postgres_admin_login
  administrator_password        = azurerm_key_vault_secret.postgres_admin_password.value

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "azure" {
  # https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-firewall-rules#programmatically-manage-firewall-rules
  # a firewall rule setting with a starting and ending address equal to 0.0.0.0 does the equivalent of the
  # 'Allow public access from any Azure service within Azure to this server' option
  name             = lower("adb-cdt-pub-vip-ddrc-${local.env_letter}-firewall-azure")
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_container_app" "pgweb" {
  name                         = lower("aca-cdt-pub-vip-ddrc-${local.env_letter}-pgweb")
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = data.azurerm_resource_group.main.name
  revision_mode                = "Single"
  max_inactive_revisions       = 10

  # external, auto port 8081
  ingress {
    external_enabled = true
    target_port      = 8081
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
      name   = "pgweb"
      image  = "sosedoff/pgweb:latest"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "PGWEB_SESSIONS"
        value = "1"
      }
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_postgresql_flexible_server.main
  ]
}

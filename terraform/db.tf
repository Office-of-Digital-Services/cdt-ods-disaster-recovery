resource "azurerm_container_app" "db" {
  name                         = lower("aca-cdt-pub-vip-ddrc-${local.env_letter}-db")
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = data.azurerm_resource_group.main.name
  revision_mode                = "Single"
  max_inactive_revisions       = 10

  identity {
    identity_ids = []
    type         = "SystemAssigned"
  }

  secret {
    name                = "postgres-db"
    key_vault_secret_id = "${local.secret_http_prefix}/postgres-db"
    identity            = "System"
  }
  secret {
    name                = "postgres-user"
    key_vault_secret_id = "${local.secret_http_prefix}/postgres-user"
    identity            = "System"
  }
  secret {
    name                = "postgres-password"
    key_vault_secret_id = "${local.secret_http_prefix}/postgres-password"
    identity            = "System"
  }

  # internal only, TCP port 5432
  ingress {
    external_enabled = false
    exposed_port     = 5432
    target_port      = 5432
    transport        = "tcp"
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "postgres"
      image  = "postgres:17"
      cpu    = 0.5
      memory = "1Gi"

      # Environment variables using secrets for PostgreSQL initialization
      env {
        name        = "POSTGRES_DB"
        secret_name = "postgres-db"
      }
      env {
        name        = "POSTGRES_USER"
        secret_name = "postgres-user"
      }
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = "postgres-password"
      }
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }
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
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_container_app.db
  ]
}

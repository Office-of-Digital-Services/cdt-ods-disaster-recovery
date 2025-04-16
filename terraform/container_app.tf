resource "azurerm_container_app_environment" "main" {
  name                       = "CAE-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  location                   = data.azurerm_resource_group.main.location
  resource_group_name        = data.azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_container_app" "db" {
  name                         = lower("aca-cdt-pub-vip-ddrc-${local.env_letter}-db")
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = data.azurerm_resource_group.main.name
  revision_mode                = "Single"
  max_inactive_revisions       = 10
  workload_profile_name        = "Consumption"

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

    # define the persistent volume using Azure File Share
    volume {
      name         = "pgdata-volume"
      storage_type = "AzureFile"
      storage_name = azurerm_storage_share.postgres.name
    }

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
      env {
        name = "PGDATA"
        # Standard location within the volume mount
        value = "/var/lib/postgresql/data/pgdata"
      }

      # Mount the persistent volume
      volume_mounts {
        # Must match the volume name defined above
        name = "pgdata-volume"
        # Standard PostgreSQL data directory
        path = "/var/lib/postgresql/data"
      }
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_storage_account.main,
    azurerm_storage_share.postgres
  ]
}

resource "azurerm_container_app" "web" {
  name                         = lower("aca-cdt-pub-vip-ddrc-${local.env_letter}-web") # has to be lowercase
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = data.azurerm_resource_group.main.name
  revision_mode                = "Single"
  max_inactive_revisions       = 10

  identity {
    identity_ids = []
    type         = "SystemAssigned"
  }

  secret {
    name                = "django-allowed-hosts"
    key_vault_secret_id = "${local.secret_http_prefix}/django-allowed-hosts"
    identity            = "System"
  }
  secret {
    name                = "django-db-name"
    key_vault_secret_id = "${local.secret_http_prefix}/django-db-name"
    identity            = "System"
  }
  secret {
    name                = "django-db-user"
    key_vault_secret_id = "${local.secret_http_prefix}/django-db-user"
    identity            = "System"
  }
  secret {
    name                = "django-db-password"
    key_vault_secret_id = "${local.secret_http_prefix}/django-db-password"
    identity            = "System"
  }
  secret {
    name                = "django-debug"
    key_vault_secret_id = "${local.secret_http_prefix}/django-debug"
    identity            = "System"
  }
  secret {
    name                = "django-log-level"
    key_vault_secret_id = "${local.secret_http_prefix}/django-log-level"
    identity            = "System"
  }
  secret {
    name                = "django-secret-key"
    key_vault_secret_id = "${local.secret_http_prefix}/django-secret-key"
    identity            = "System"
  }
  secret {
    name                = "django-trusted-origins"
    key_vault_secret_id = "${local.secret_http_prefix}/django-trusted-origins"
    identity            = "System"
  }

  # external, auto port 8000
  ingress {
    client_certificate_mode = "ignore"
    external_enabled        = true
    target_port             = 8000
    transport               = "auto"
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  template {
    min_replicas = 1
    max_replicas = 3
    http_scale_rule {
      concurrent_requests = "10"
      name                = "http-scaler"
    }

    container {
      name    = "web"
      command = []
      args    = []
      image   = "${var.container_registry}/${var.container_repository}:${var.container_tag}"
      cpu     = 0.5
      memory  = "1Gi"

      # Requests
      env {
        name  = "REQUESTS_CONNECT_TIMEOUT"
        value = "5"
      }
      env {
        name  = "REQUESTS_READ_TIMEOUT"
        value = "20"
      }
      # Django settings
      env {
        name        = "DJANGO_ALLOWED_HOSTS"
        secret_name = "django-allowed-hosts"
      }
      env {
        name        = "DJANGO_DB_NAME"
        secret_name = "django-db-name"
      }
      env {
        name        = "DJANGO_DB_USER"
        secret_name = "django-db-user"
      }
      env {
        name        = "DJANGO_DB_PASSWORD"
        secret_name = "django-db-password"
      }
      env {
        name = "POSTGRES_HOSTNAME"
        # Use the FQDN of the internal database container app
        value = azurerm_container_app.db.latest_revision_fqdn
      }
      env {
        name        = "DJANGO_DEBUG"
        secret_name = local.is_prod ? null : "django-debug"
        value       = local.is_prod ? "False" : null
      }
      env {
        name        = "DJANGO_LOG_LEVEL"
        secret_name = "django-log-level"
      }
      env {
        name        = "DJANGO_SECRET_KEY"
        secret_name = "django-secret-key"
      }
      env {
        name        = "DJANGO_TRUSTED_ORIGINS"
        secret_name = "django-trusted-origins"
      }
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_container_app.db
  ]
}

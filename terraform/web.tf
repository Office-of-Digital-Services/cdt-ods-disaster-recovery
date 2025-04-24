resource "azurerm_container_app" "web" {
  name                         = lower("aca-cdt-pub-vip-ddrc-${local.env_letter}-web")
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
    name                = "django-db-reset"
    key_vault_secret_id = "${local.secret_http_prefix}/django-db-reset"
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
    name                = "django-superuser-username"
    key_vault_secret_id = "${local.secret_http_prefix}/django-superuser-username"
    identity            = "System"
  }
  secret {
    name                = "django-superuser-email"
    key_vault_secret_id = "${local.secret_http_prefix}/django-superuser-email"
    identity            = "System"
  }
  secret {
    name                = "django-superuser-password"
    key_vault_secret_id = "${local.secret_http_prefix}/django-superuser-password"
    identity            = "System"
  }
  secret {
    name                = "django-trusted-origins"
    key_vault_secret_id = "${local.secret_http_prefix}/django-trusted-origins"
    identity            = "System"
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
    max_replicas = 1

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
        # reference the internal name of the database container app
        value = azurerm_container_app.db.latest_revision_name
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

      volume_mounts {
        name = "config"
        path = "/cdt/app/config"
      }
    }

    volume {
      name         = "config"
      storage_name = azurerm_storage_share.web.name
      storage_type = "AzureFile"
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_container_app.db
  ]
}

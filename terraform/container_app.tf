resource "azurerm_container_app_environment" "main" {
  name                       = "CAE-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  location                   = data.azurerm_resource_group.main.location
  resource_group_name        = data.azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_container_app" "web" {
  name                         = lower("aca-cdt-pub-vip-ddrc-${local.env_letter}-web") # has to be lowercase
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = data.azurerm_resource_group.main.name
  revision_mode                = "Single"
  max_inactive_revisions       = 10
  workload_profile_name        = "Consumption"

  secret {
    name                = "requests-connect-timeout"
    key_vault_secret_id = "${local.secret_http_prefix}/requests-connect-timeout"
    identity            = "System"
  }
  secret {
    name                = "requests-read-timeout"
    key_vault_secret_id = "${local.secret_http_prefix}/requests-read-timeout"
    identity            = "System"
  }
  secret {
    name                = "django-allowed-hosts"
    key_vault_secret_id = "${local.secret_http_prefix}/django-allowed-hosts"
    identity            = "System"
  }
  secret {
    name                = "django-storage-dir"
    key_vault_secret_id = "${local.secret_http_prefix}/django-storage-dir"
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
  secret {
    name                = "healthcheck-user-agents"
    key_vault_secret_id = "${local.secret_http_prefix}/healthcheck-user-agents"
    identity            = "System"
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
      readiness_probe {
        path      = "/healthcheck"
        port      = 8000
        timeout   = 5
        transport = "HTTP"
      }
      # Requests
      env {
        name        = "REQUESTS_CONNECT_TIMEOUT"
        secret_name = "requests-connect-timeout"
      }
      env {
        name        = "REQUESTS_READ_TIMEOUT"
        secret_name = "requests-read-timeout"
      }
      # Django settings
      env {
        name        = "DJANGO_ALLOWED_HOSTS"
        secret_name = "django-allowed-hosts"
      }
      env {
        name        = "DJANGO_STORAGE_DIR"
        secret_name = "django-storage-dir"
      }
      env {
        name        = "DJANGO_DEBUG"
        secret_name = local.is_prod ? null : "django-debug"
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
      env {
        name        = "HEALTHCHECK_USER_AGENTS"
        secret_name = local.is_dev ? null : "healthcheck-user-agents"
      }
    }
  }

  ingress {
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
    external_enabled = true
    target_port      = 8000
    transport        = "auto"
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

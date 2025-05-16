# Create a User-Assigned Managed Identity for the Web App
resource "azurerm_user_assigned_identity" "web_app_identity" {
  name                = lower("umi-aca-web-${local.env_name}")
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_container_app" "web" {
  name                         = lower("aca-cdt-pub-vip-ddrc-${local.env_letter}-web")
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = data.azurerm_resource_group.main.name
  revision_mode                = "Single"
  max_inactive_revisions       = 10

  identity {
    identity_ids = [azurerm_user_assigned_identity.web_app_identity.id]
    type         = "UserAssigned"
  }

  # Django
  secret {
    name                = "django-allowed-hosts"
    key_vault_secret_id = "${local.secret_http_prefix}/django-allowed-hosts"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-db-name"
    key_vault_secret_id = "${local.secret_http_prefix}/django-db-name"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-db-user"
    key_vault_secret_id = "${local.secret_http_prefix}/django-db-user"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-db-password"
    key_vault_secret_id = "${local.secret_http_prefix}/django-db-password"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-db-fixtures"
    key_vault_secret_id = "${local.secret_http_prefix}/django-db-fixtures"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-debug"
    key_vault_secret_id = "${local.secret_http_prefix}/django-debug"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-log-level"
    key_vault_secret_id = "${local.secret_http_prefix}/django-log-level"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-secret-key"
    key_vault_secret_id = "${local.secret_http_prefix}/django-secret-key"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-superuser-username"
    key_vault_secret_id = "${local.secret_http_prefix}/django-superuser-username"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-superuser-email"
    key_vault_secret_id = "${local.secret_http_prefix}/django-superuser-email"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-superuser-password"
    key_vault_secret_id = "${local.secret_http_prefix}/django-superuser-password"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "django-trusted-origins"
    key_vault_secret_id = "${local.secret_http_prefix}/django-trusted-origins"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  # Postgres
  secret {
    name                = "postgres-db"
    key_vault_secret_id = "${local.secret_http_prefix}/postgres-db"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = azurerm_key_vault_secret.postgres_admin_password.name
    key_vault_secret_id = "${local.secret_http_prefix}/${azurerm_key_vault_secret.postgres_admin_password.name}"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  # Tasks
  secret {
    name                = "tasks-db-name"
    key_vault_secret_id = "${local.secret_http_prefix}/tasks-db-name"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "tasks-db-user"
    key_vault_secret_id = "${local.secret_http_prefix}/tasks-db-user"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  secret {
    name                = "tasks-db-password"
    key_vault_secret_id = "${local.secret_http_prefix}/tasks-db-password"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
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

    init_container {
      name    = "web-init"
      command = ["bin/setup.sh"]
      image   = "${var.container_registry}/${var.container_repository}:${var.container_tag}"
      cpu     = 0.25
      memory  = "0.5Gi"

      # Django
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
        name        = "DJANGO_DB_FIXTURES"
        secret_name = "django-db-fixtures"
      }
      env {
        name        = "DJANGO_SUPERUSER_USERNAME"
        secret_name = "django-superuser-username"
      }
      env {
        name        = "DJANGO_SUPERUSER_EMAIL"
        secret_name = "django-superuser-email"
      }
      env {
        name        = "DJANGO_SUPERUSER_PASSWORD"
        secret_name = "django-superuser-password"
      }
      # Postgres
      env {
        name        = "POSTGRES_DB"
        secret_name = "postgres-db"
      }
      env {
        name  = "POSTGRES_USER"
        value = local.postgres_admin_login
      }
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = azurerm_key_vault_secret.postgres_admin_password.name
      }
      env {
        name = "POSTGRES_HOSTNAME"
        # reference the database server
        value = azurerm_postgresql_flexible_server.main.fqdn
      }
      # Tasks
      env {
        name        = "TASKS_DB_NAME"
        secret_name = "tasks-db-name"
      }
      env {
        name        = "TASKS_DB_USER"
        secret_name = "tasks-db-user"
      }
      env {
        name        = "TASKS_DB_PASSWORD"
        secret_name = "tasks-db-password"
      }

      volume_mounts {
        name = "config"
        path = "/cdt/app/config"
      }
    }

    container {
      name    = "web"
      command = []
      args    = []
      image   = "${var.container_registry}/${var.container_repository}:${var.container_tag}"
      cpu     = 0.5
      memory  = "1Gi"

      # Django
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
      # Postgres
      env {
        name = "POSTGRES_HOSTNAME"
        # reference the database server
        value = azurerm_postgresql_flexible_server.main.fqdn
      }
      # Requests
      env {
        name  = "REQUESTS_CONNECT_TIMEOUT"
        value = "5"
      }
      env {
        name  = "REQUESTS_READ_TIMEOUT"
        value = "20"
      }
      # Tasks
      env {
        name        = "TASKS_DB_NAME"
        secret_name = "tasks-db-name"
      }
      env {
        name        = "TASKS_DB_USER"
        secret_name = "tasks-db-user"
      }
      env {
        name        = "TASKS_DB_PASSWORD"
        secret_name = "tasks-db-password"
      }

      volume_mounts {
        name = "config"
        path = "/cdt/app/config"
      }
    }

    volume {
      name         = "config"
      storage_name = azurerm_storage_share.config.name
      storage_type = "AzureFile"
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_postgresql_flexible_server.main,
    azurerm_key_vault_secret.postgres_admin_password,
    azurerm_user_assigned_identity.web_app_identity
  ]
}

# https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references?tabs=azure-cli#granting-your-app-access-to-key-vault
resource "azurerm_key_vault_access_policy" "container_app_web_access" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_user_assigned_identity.web_app_identity.principal_id

  secret_permissions = ["Get", "List"]

  depends_on = [
    azurerm_key_vault.main,
    azurerm_user_assigned_identity.web_app_identity
  ]
}

resource "azurerm_container_app" "worker" {
  name                         = lower("aca-cdt-pub-vip-ddrc-${local.env_letter}-worker")
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = data.azurerm_resource_group.main.name
  revision_mode                = "Single"
  max_inactive_revisions       = 10

  identity {
    identity_ids = []
    type         = "SystemAssigned"
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
    name                = "django-email-host"
    key_vault_secret_id = "${local.secret_http_prefix}/django-email-host"
    identity            = "System"
  }
  secret {
    name                = "django-email-user"
    key_vault_secret_id = "${local.secret_http_prefix}/django-email-user"
    identity            = "System"
  }
  secret {
    name                = "django-email-password"
    key_vault_secret_id = "${local.secret_http_prefix}/django-email-password"
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
    name                = "tasks-db-name"
    key_vault_secret_id = "${local.secret_http_prefix}/tasks-db-name"
    identity            = "System"
  }
  secret {
    name                = "tasks-db-user"
    key_vault_secret_id = "${local.secret_http_prefix}/tasks-db-user"
    identity            = "System"
  }
  secret {
    name                = "tasks-db-password"
    key_vault_secret_id = "${local.secret_http_prefix}/tasks-db-password"
    identity            = "System"
  }
  secret {
    name                = "vital-records-email-from"
    key_vault_secret_id = "${local.secret_http_prefix}/vital-records-email-from"
    identity            = "System"
  }
  secret {
    name                = "vital-records-email-to"
    key_vault_secret_id = "${local.secret_http_prefix}/vital-records-email-to"
    identity            = "System"
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name    = "worker"
      command = []
      args    = ["bin/worker.sh"]
      image   = "${var.container_registry}/${var.container_repository}:${var.container_tag}"
      cpu     = 0.5
      memory  = "1Gi"

      # Django settings
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
        name        = "DJANGO_EMAIL_HOST"
        secret_name = "django-email-host"
      }
      env {
        name        = "DJANGO_EMAIL_USER"
        secret_name = "django-email-user"
      }
      env {
        name        = "DJANGO_EMAIL_PASSWORD"
        secret_name = "django-email-password"
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
        name = "DJANGO_STORAGE_DIR"
        # match the volume mount path below
        value = "/cdt/app/requests"
      }
      env {
        name = "POSTGRES_HOSTNAME"
        # reference the internal name of the database container app
        value = azurerm_postgresql_flexible_server.main.fqdn
      }
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
      env {
        name        = "VITAL_RECORDS_EMAIL_FROM"
        secret_name = "vital-records-email-from"
      }
      env {
        name        = "VITAL_RECORDS_EMAIL_TO"
        secret_name = "vital-records-email-to"
      }

      volume_mounts {
        # match the name of the volume below
        name = "requests"
        # match the DJANGO_STORAGE_DIR env above
        path = "/cdt/app/requests"
      }
    }

    volume {
      # match the name of the volume mount above
      name         = "requests"
      storage_name = azurerm_storage_share.requests.name
      storage_type = "AzureFile"
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_postgresql_flexible_server.main
  ]
}

# https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references?tabs=azure-cli#granting-your-app-access-to-key-vault
resource "azurerm_key_vault_access_policy" "container_app_worker_access" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_container_app.worker.identity[0].principal_id

  secret_permissions = ["Get"]

  depends_on = [
    azurerm_key_vault.main,
    azurerm_container_app.worker
  ]
}

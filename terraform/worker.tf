locals {
  # Define secret names for clarity
  tasks_db_password_name = "tasks-db-password"
}

# Generate a random password for the Tasks DB
resource "random_password" "tasks_db" {
  length           = 32
  min_lower        = 4
  min_upper        = 4
  min_numeric      = 4
  min_special      = 4
  special          = true
}

# Create the secret for Tasks DB password using the generated secret
resource "azurerm_key_vault_secret" "tasks_db_password" {
  name         = local.tasks_db_password_name
  value        = random_password.tasks_db.result
  key_vault_id = azurerm_key_vault.main.id
  content_type = "password"
  depends_on = [
    azurerm_key_vault.main,
    random_password.tasks_db # Ensure password is generated first
  ]
}

# Create a User-Assigned Managed Identity for the Worker App
resource "azurerm_user_assigned_identity" "worker_app_identity" {
  name                = lower("umi-aca-worker-${local.env_name}")
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_container_app" "worker" {
  name                         = lower("aca-cdt-pub-vip-ddrc-${local.env_letter}-worker")
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = data.azurerm_resource_group.main.name
  revision_mode                = "Single"
  max_inactive_revisions       = 10

  identity {
    identity_ids = [azurerm_user_assigned_identity.worker_app_identity.id]
    type         = "UserAssigned"
  }

  # Django
  secret {
    name                = "django-db-name"
    key_vault_secret_id = "${local.secret_http_prefix}/django-db-name"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = "django-db-user"
    key_vault_secret_id = "${local.secret_http_prefix}/django-db-user"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = azurerm_key_vault_secret.django_db_password.name
    key_vault_secret_id = "${local.secret_http_prefix}/${azurerm_key_vault_secret.django_db_password.name}"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = "django-email-host"
    key_vault_secret_id = "${local.secret_http_prefix}/django-email-host"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = "django-email-user"
    key_vault_secret_id = "${local.secret_http_prefix}/django-email-user"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = "django-email-password"
    key_vault_secret_id = "${local.secret_http_prefix}/django-email-password"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = "django-log-level"
    key_vault_secret_id = "${local.secret_http_prefix}/django-log-level"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = azurerm_key_vault_secret.django_secret_key.name
    key_vault_secret_id = "${local.secret_http_prefix}/${azurerm_key_vault_secret.django_secret_key.name}"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  # Tasks
  secret {
    name                = "tasks-db-name"
    key_vault_secret_id = "${local.secret_http_prefix}/tasks-db-name"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = "tasks-db-user"
    key_vault_secret_id = "${local.secret_http_prefix}/tasks-db-user"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = azurerm_key_vault_secret.tasks_db_password.name
    key_vault_secret_id = "${local.secret_http_prefix}/${azurerm_key_vault_secret.tasks_db_password.name}"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  # Vital records
  secret {
    name                = "vital-records-email-from"
    key_vault_secret_id = "${local.secret_http_prefix}/vital-records-email-from"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = "vital-records-email-to"
    key_vault_secret_id = "${local.secret_http_prefix}/vital-records-email-to"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
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
        secret_name = azurerm_key_vault_secret.django_db_password.name
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
        secret_name = azurerm_key_vault_secret.django_secret_key.name
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
    azurerm_postgresql_flexible_server.main,
    azurerm_key_vault_secret.django_db_password,
    azurerm_key_vault_secret.django_secret_key,
    azurerm_key_vault_secret.tasks_db_password,
    azurerm_user_assigned_identity.worker_app_identity
  ]
}

# https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references?tabs=azure-cli#granting-your-app-access-to-key-vault
resource "azurerm_key_vault_access_policy" "container_app_worker_access" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_user_assigned_identity.worker_app_identity.principal_id

  secret_permissions = ["Get", "List"]

  depends_on = [
    azurerm_key_vault.main,
    azurerm_user_assigned_identity.worker_app_identity
  ]
}

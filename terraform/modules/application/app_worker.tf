# The background tasks worker app
resource "azurerm_container_app" "worker" {
  name                         = "${var.container_app_prefix}-worker"
  container_app_environment_id = azurerm_container_app_environment.worker.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  max_inactive_revisions       = 10
  workload_profile_name        = "Consumption"

  identity {
    identity_ids = [azurerm_user_assigned_identity.worker_app_identity.id]
    type         = "UserAssigned"
  }

  # Static secret definitions referencing secrets created in this or other modules

  # Email
  secret {
    name                = var.email_connection_string_secret_name
    key_vault_secret_id = "${var.key_vault_secret_uri_prefix}/${var.email_connection_string_secret_name}"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  secret {
    name                = var.from_email_secret_name
    key_vault_secret_id = "${var.key_vault_secret_uri_prefix}/${var.from_email_secret_name}"
    identity            = azurerm_user_assigned_identity.worker_app_identity.id
  }
  # Dynamic secret defintions from this module
  dynamic "secret" {
    # Loop over the same set of names used to create the secrets
    for_each = local.generated_secrets

    content {
      # 'secret.key' here will be "django-db-password", "django-secret-key", etc.
      name                = azurerm_key_vault_secret.main[secret.key].name
      key_vault_secret_id = azurerm_key_vault_secret.main[secret.key].id
      identity            = azurerm_user_assigned_identity.worker_app_identity.id
    }
  }
  # Dynamic secret defintions using the input map
  dynamic "secret" {
    for_each = var.worker_app_config_secrets
    content {
      name                = secret.value
      key_vault_secret_id = "${var.key_vault_secret_uri_prefix}/${secret.value}"
      identity            = azurerm_user_assigned_identity.worker_app_identity.id
    }
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name    = "worker"
      command = []
      args    = ["bin/worker.sh"]
      image   = "${var.container_registry}/${var.container_repository}:${var.container_tag}"
      cpu     = var.worker_app_cpu
      memory  = var.worker_app_memory

      # Django
      env {
        name        = "DJANGO_DB_NAME"
        secret_name = var.worker_app_config_secrets.DjangoDbName
      }
      env {
        name        = "DJANGO_DB_USER"
        secret_name = var.worker_app_config_secrets.DjangoDbUser
      }
      env {
        name        = "DJANGO_DB_PASSWORD"
        secret_name = "django-db-password"
      }
      env {
        name        = "DJANGO_LOG_LEVEL"
        secret_name = var.worker_app_config_secrets.DjangoLogLevel
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
      # Email
      env {
        name        = "AZURE_COMMUNICATION_CONNECTION_STRING"
        secret_name = var.email_connection_string_secret_name
      }
      env {
        name        = "DEFAULT_FROM_EMAIL"
        secret_name = var.from_email_secret_name
      }
      env {
        name        = "VITAL_RECORDS_EMAIL_TO"
        secret_name = var.worker_app_config_secrets.VitalRecordsEmailTo
      }
      # Postgres
      env {
        name  = "POSTGRES_HOSTNAME"
        value = var.database_fqdn
      }
      env {
        name        = "TASKS_DB_NAME"
        secret_name = var.worker_app_config_secrets.TasksDbName
      }
      env {
        name        = "TASKS_DB_USER"
        secret_name = var.worker_app_config_secrets.TasksDbUser
      }
      env {
        name        = "TASKS_DB_PASSWORD"
        secret_name = "tasks-db-password"
      }

      volume_mounts {
        name = var.storage_share_names.requests
        # match the DJANGO_STORAGE_DIR env above
        path = "/cdt/app/requests"
      }
    }

    volume {
      name         = var.storage_share_names.requests
      storage_name = var.storage_share_names.requests
      storage_type = "AzureFile"
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_container_app_environment_storage.requests
  ]
}

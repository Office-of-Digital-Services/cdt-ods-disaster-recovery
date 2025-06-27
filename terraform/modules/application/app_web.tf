# The primary web app
resource "azurerm_container_app" "web" {
  name                         = "${var.container_app_prefix}-web"
  container_app_environment_id = azurerm_container_app_environment.public.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  max_inactive_revisions       = 10
  workload_profile_name        = "Consumption"

  identity {
    identity_ids = [azurerm_user_assigned_identity.web_app_identity.id]
    type         = "UserAssigned"
  }

  # Static secret definitions referencing secrets created in this or other modules
  # Postgres
  secret {
    name                = var.postgres_admin_password_secret_name
    key_vault_secret_id = "${var.key_vault_secret_uri_prefix}/${var.postgres_admin_password_secret_name}"
    identity            = azurerm_user_assigned_identity.web_app_identity.id
  }
  # Dynamic secret defintions from this module
  dynamic "secret" {
    # Loop over the same set of names used to create the secrets
    for_each = local.generated_secrets

    content {
      # 'secret.key' here will be "django-db-password", "django-secret-key", etc.
      name                = azurerm_key_vault_secret.main[secret.key].name
      key_vault_secret_id = azurerm_key_vault_secret.main[secret.key].id
      identity            = azurerm_user_assigned_identity.web_app_identity.id
    }
  }
  # Dynamic secret defintions using the input map
  dynamic "secret" {
    for_each = var.web_app_config_secrets
    content {
      name                = secret.value
      key_vault_secret_id = "${var.key_vault_secret_uri_prefix}/${secret.value}"
      identity            = azurerm_user_assigned_identity.web_app_identity.id
    }
  }

  ingress {
    external_enabled           = true
    allow_insecure_connections = true
    target_port                = 8000 # Django's port
    transport                  = "auto"
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
        secret_name = var.web_app_config_secrets.DjangoDbName
      }
      env {
        name        = "DJANGO_DB_USER"
        secret_name = var.web_app_config_secrets.DjangoDbUser
      }
      env {
        name        = "DJANGO_DB_PASSWORD"
        secret_name = "django-db-password"
      }
      env {
        name        = "DJANGO_DB_FIXTURES"
        secret_name = var.web_app_config_secrets.DjangoDbFixtures
      }
      env {
        name        = "DJANGO_SUPERUSER_USERNAME"
        secret_name = var.web_app_config_secrets.DjangoSuperuserUsername
      }
      env {
        name        = "DJANGO_SUPERUSER_EMAIL"
        secret_name = var.web_app_config_secrets.DjangoSuperuserEmail
      }
      env {
        name        = "DJANGO_SUPERUSER_PASSWORD"
        secret_name = "django-superuser-password"
      }
      # Postgres
      env {
        name        = "POSTGRES_DB"
        secret_name = var.web_app_config_secrets.PostgresDbName
      }
      env {
        name  = "POSTGRES_USER"
        value = var.postgres_admin_login
      }
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = var.postgres_admin_password_secret_name
      }
      env {
        name  = "POSTGRES_HOSTNAME"
        value = var.database_fqdn
      }
      # Tasks
      env {
        name        = "TASKS_DB_NAME"
        secret_name = var.web_app_config_secrets.TasksDbName
      }
      env {
        name        = "TASKS_DB_USER"
        secret_name = var.web_app_config_secrets.TasksDbUser
      }
      env {
        name        = "TASKS_DB_PASSWORD"
        secret_name = "tasks-db-password"
      }

      volume_mounts {
        name = var.storage_share_names.config
        path = "/cdt/app/config"
      }
    }

    container {
      name    = "web"
      command = []
      args    = []
      image   = "${var.container_registry}/${var.container_repository}:${var.container_tag}"
      cpu     = var.web_app_cpu
      memory  = var.web_app_memory

      # Django
      env {
        name        = "DJANGO_ALLOWED_HOSTS"
        secret_name = var.web_app_config_secrets.DjangoAllowedHosts
      }
      env {
        name        = "DJANGO_DB_NAME"
        secret_name = var.web_app_config_secrets.DjangoDbName
      }
      env {
        name        = "DJANGO_DB_USER"
        secret_name = var.web_app_config_secrets.DjangoDbUser
      }
      env {
        name        = "DJANGO_DB_PASSWORD"
        secret_name = "django-db-password"
      }
      env {
        name        = "DJANGO_DEBUG"
        secret_name = var.is_prod ? null : var.web_app_config_secrets.DjangoDebug
        value       = var.is_prod ? "False" : null
      }
      env {
        name        = "DJANGO_LOG_LEVEL"
        secret_name = var.web_app_config_secrets.DjangoLogLevel
      }
      env {
        name        = "DJANGO_SECRET_KEY"
        secret_name = "django-secret-key"
      }
      env {
        name        = "DJANGO_TRUSTED_ORIGINS"
        secret_name = var.web_app_config_secrets.DjangoTrustedOrigins
      }
      # Google SSO
      env {
        name        = "GOOGLE_SSO_ALLOWABLE_DOMAINS"
        secret_name = var.web_app_config_secrets.GoogleSsoAllowableDomains
      }
      env {
        name        = "GOOGLE_SSO_CLIENT_ID"
        secret_name = var.web_app_config_secrets.GoogleSsoClientId
      }
      env {
        name        = "GOOGLE_SSO_CLIENT_SECRET"
        secret_name = var.web_app_config_secrets.GoogleSsoClientSecret
      }
      env {
        name        = "GOOGLE_SSO_PROJECT_ID"
        secret_name = var.web_app_config_secrets.GoogleSsoProjectId
      }
      env {
        name        = "GOOGLE_SSO_SUPERUSER_LIST"
        secret_name = var.web_app_config_secrets.GoogleSsoSuperuserList
      }
      # Postgres
      env {
        name = "POSTGRES_HOSTNAME"
        # reference the database server
        value = var.database_fqdn
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
        secret_name = var.web_app_config_secrets.TasksDbName
      }
      env {
        name        = "TASKS_DB_USER"
        secret_name = var.web_app_config_secrets.TasksDbUser
      }
      env {
        name        = "TASKS_DB_PASSWORD"
        secret_name = "tasks-db-password"
      }

      volume_mounts {
        name = var.storage_share_names.config
        path = "/cdt/app/config"
      }
    }

    volume {
      name         = var.storage_share_names.config
      storage_name = var.storage_share_names.config
      storage_type = "AzureFile"
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_container_app_environment_storage.config
  ]
}

# The pgweb appliciation
resource "azurerm_container_app" "pgweb" {
  name                         = "${var.container_app_prefix}-pgweb"
  container_app_environment_id = azurerm_container_app_environment.public.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  max_inactive_revisions       = 10
  workload_profile_name        = "Consumption"

  ingress {
    external_enabled           = true
    allow_insecure_connections = true
    target_port                = 8081 # pgweb's port
    transport                  = "auto"
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
      image  = "sosedoff/pgweb:${var.pgweb_image_tag}"
      cpu    = 0.25
      memory = "0.5Gi"

      # This argument tells pgweb to serve all assets from the /pgweb subpath,
      # since the container app is served from the app gateway at that subpath.
      # NOTE: the / should not be part of the prefix value
      args = ["--prefix", "pgweb"]

      env {
        name  = "PGWEB_SESSIONS"
        value = "1"
      }
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

# Imports all the submodules and wires together necessary input/outputs
locals {
  application_insights_name        = "AI-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  communication_service_name       = "ACS-PUB-VIP-DDRC-${local.env_letter}-001"
  container_app_environment_prefix = "CAE-CDT-PUB-VIP-DDRC-${local.env_letter}"
  container_app_prefix             = lower("aca-cdt-pub-vip-ddrc-${local.env_letter}")
  database_server_name             = lower("adb-cdt-pub-vip-ddrc-${local.env_letter}-db")
  diagnostic_setting_prefix        = lower("MDS-CDT-PUB-VIP-DDRC-${local.env_letter}")
  key_vault_name                   = "KV-CDT-PUB-DDRC-${local.env_letter}-001"
  key_vault_allowed_ips = [
    # Central United States
    "20.37.158.0/23",
    # West Central United States
    "52.150.138.0/24",
    # East United States
    "20.42.5.0/24",
    # East 2 United States
    "20.41.6.0/23",
    # North United States
    "40.80.187.0/24",
    # South United States
    "40.119.10.0/24",
    # West United States
    "40.82.252.0/24",
    # West 2 United States
    "20.42.134.0/23",
    # West 3 United States
    "20.125.155.0/24"
  ]
  key_vault_secret_uri_prefix       = "https://${local.key_vault_name}.vault.azure.net/secrets"
  location                          = data.azurerm_resource_group.main.location
  log_analytics_workspace_name      = "CDT-OET-PUB-DDRC-${local.env_letter}-001"
  nat_gateway_name                  = lower("nat-cdt-pub-vip-ddrc-${local.env_letter}-001")
  nsg_prefix                        = "NSG-CDT-PUB-VIP-DDRC-${local.env_letter}"
  private_endpoint_prefix           = lower("pe-cdt-pub-vip-ddrc-${local.env_letter}")
  private_service_connection_prefix = lower("psc-cdt-pub-vip-ddrc-${local.env_letter}")
  public_ip_prefix                  = lower("pip-cdt-pub-vip-ddrc-${local.env_letter}")
  resource_group_name               = data.azurerm_resource_group.main.name
  storage_account_name              = lower("sacdtddrc${local.env_letter}001")
  subnet_prefix                     = "SNET-CDT-PUB-VIP-DDRC-${local.env_letter}"
  tenant_id                         = data.azurerm_client_config.current.tenant_id
  vnet_name                         = "VNET-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
}

module "network" {
  source                     = "./modules/network"
  resource_group_name        = local.resource_group_name
  location                   = local.location
  env_letter                 = local.env_letter
  is_prod                    = local.is_prod
  diagnostic_setting_prefix  = local.diagnostic_setting_prefix
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  nat_gateway_name           = local.nat_gateway_name
  nsg_prefix                 = local.nsg_prefix
  public_ip_prefix           = local.public_ip_prefix
  subnet_prefix              = local.subnet_prefix
  vnet_name                  = local.vnet_name
}

module "monitoring" {
  source                       = "./modules/monitoring"
  resource_group_name          = local.resource_group_name
  location                     = local.location
  log_analytics_workspace_name = local.log_analytics_workspace_name
  application_insights_name    = local.application_insights_name
  action_group_name            = "Slack channel email"
  action_group_short_name      = "slack-notify"
  notification_email_address   = var.SLACK_NOTIFY_EMAIL
}

module "key_vault" {
  source              = "./modules/key_vault"
  resource_group_name = local.resource_group_name
  location            = local.location
  tenant_id           = local.tenant_id
  allowed_ip_rules    = concat(var.KEY_VAULT_ALLOWED_IPS, local.key_vault_allowed_ips)
  base_access_policy_object_ids = {
    engineering_group = var.ENGINEERING_GROUP_OBJECT_ID
    devsecops_group   = var.DEVSECOPS_OBJECT_ID
  }
  diagnostic_setting_prefix         = local.diagnostic_setting_prefix
  env_letter                        = local.env_letter
  key_vault_name                    = local.key_vault_name
  key_vault_subnet_id               = module.network.subnet_ids.key_vault
  log_analytics_workspace_id        = module.monitoring.log_analytics_workspace_id
  private_endpoint_prefix           = local.private_endpoint_prefix
  private_service_connection_prefix = local.private_service_connection_prefix
  virtual_network_id                = module.network.vnet_id
}

module "email" {
  source                     = "./modules/email"
  resource_group_name        = local.resource_group_name
  communication_service_name = local.communication_service_name
  diagnostic_setting_prefix  = local.diagnostic_setting_prefix
  key_vault_id               = module.key_vault.key_vault_id
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
}

module "storage" {
  source                            = "./modules/storage"
  resource_group_name               = local.resource_group_name
  location                          = local.location
  env_letter                        = local.env_letter
  diagnostic_setting_prefix         = local.diagnostic_setting_prefix
  log_analytics_workspace_id        = module.monitoring.log_analytics_workspace_id
  storage_account_name              = local.storage_account_name
  private_endpoint_prefix           = local.private_endpoint_prefix
  private_service_connection_prefix = local.private_service_connection_prefix
  storage_subnet_id                 = module.network.subnet_ids.storage
  virtual_network_id                = module.network.vnet_id
}

module "database" {
  source                            = "./modules/database"
  resource_group_name               = local.resource_group_name
  location                          = local.location
  env_letter                        = local.env_letter
  db_subnet_id                      = module.network.subnet_ids.db
  diagnostic_setting_prefix         = local.diagnostic_setting_prefix
  key_vault_id                      = module.key_vault.key_vault_id
  log_analytics_workspace_id        = module.monitoring.log_analytics_workspace_id
  private_endpoint_prefix           = local.private_endpoint_prefix
  private_service_connection_prefix = local.private_service_connection_prefix
  server_name                       = local.database_server_name
  virtual_network_id                = module.network.vnet_id
}

module "application" {
  source                              = "./modules/application"
  resource_group_name                 = local.resource_group_name
  location                            = local.location
  env_letter                          = local.env_letter
  env_name                            = local.env_name
  is_prod                             = local.is_prod
  hostname                            = local.hostname
  virtual_network_id                  = module.network.vnet_id
  container_app_environment_prefix    = local.container_app_environment_prefix
  container_app_prefix                = local.container_app_prefix
  container_tag                       = var.container_tag
  database_fqdn                       = module.database.server_fqdn
  email_connection_string_secret_name = module.email.connection_string_secret_name
  from_email_secret_name              = module.email.from_email_secret_name
  key_vault_id                        = module.key_vault.key_vault_id
  key_vault_secret_uri_prefix         = local.key_vault_secret_uri_prefix
  log_analytics_workspace_id          = module.monitoring.log_analytics_workspace_id
  postgres_admin_login                = "postgres_admin"
  postgres_admin_password_secret_name = module.database.admin_password_secret_name
  storage_account_name                = local.storage_account_name
  storage_account_primary_access_key  = module.storage.storage_account_primary_access_key
  storage_share_names                 = module.storage.share_names
  subnet_ids                          = module.network.subnet_ids
  # pre-existing secrets not managed via Terraform, to reference in the web app
  web_app_config_secrets = {
    DjangoAllowedHosts        = "django-allowed-hosts"
    DjangoDbName              = "django-db-name"
    DjangoDbUser              = "django-db-user"
    DjangoDbFixtures          = "django-db-fixtures"
    DjangoDebug               = "django-debug"
    DjangoLogLevel            = "django-log-level"
    DjangoSuperuserUsername   = "django-superuser-username"
    DjangoSuperuserEmail      = "django-superuser-email"
    DjangoTrustedOrigins      = "django-trusted-origins"
    GoogleSsoAllowableDomains = "google-sso-allowable-domains"
    GoogleSsoClientId         = "google-sso-client-id"
    GoogleSsoClientSecret     = "google-sso-client-secret"
    GoogleSsoProjectId        = "google-sso-project-id"
    GoogleSsoSuperuserList    = "google-sso-superuser-list"
    PostgresDbName            = "postgres-db-name"
    TasksDbName               = "tasks-db-name"
    TasksDbUser               = "tasks-db-user"
  }
  # pre-existing secrets not managed via Terraform, to reference in the worker app
  worker_app_config_secrets = {
    DjangoDbName        = "django-db-name"
    DjangoDbUser        = "django-db-user"
    DjangoLogLevel      = "django-log-level"
    TasksDbName         = "tasks-db-name"
    TasksDbUser         = "tasks-db-user"
    VitalRecordsEmailTo = "vital-records-email-to"
  }
}

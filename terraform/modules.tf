# Imports all the submodules and wires together necessary input/outputs
locals {
  application_insights_name         = "AI-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  communication_service_name        = "ACS-PUB-VIP-DDRC-${local.env_letter}-001"
  diagnostic_setting_prefix         = lower("MDS-CDT-PUB-VIP-DDRC-${local.env_letter}")
  key_vault_name                    = "KV-CDT-PUB-DDRC-${local.env_letter}-001"
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

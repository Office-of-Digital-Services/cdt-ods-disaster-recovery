# Imports all the submodules and wires together necessary input/outputs
locals {
  location                          = data.azurerm_resource_group.main.location
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
  nat_gateway_name           = local.nat_gateway_name
  nsg_prefix                 = local.nsg_prefix
  public_ip_prefix           = local.public_ip_prefix
  subnet_prefix              = local.subnet_prefix
  vnet_name                  = local.vnet_name
}

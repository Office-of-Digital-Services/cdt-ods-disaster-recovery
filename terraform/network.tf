locals {
  # VNet uses a shared Resource Group, different from App Service Resource Group we use for DDRC stuff
  network_resource_group_name = "RG-CDT-PUB-SHRD-W-P-001"
  vnet_name                   = "VNET-CDT-PUB-SHRD-W-P-001"
  subnet_name                 = "SNET-CDT-PUB-DDRC-${local.env_letter}-001"

  # use the subnet ID rather than referencing it as a data source to work around permissions issues
  subnet_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${local.network_resource_group_name}/providers/Microsoft.Network/virtualNetworks/${local.vnet_name}/subnets/${local.subnet_name}"
}

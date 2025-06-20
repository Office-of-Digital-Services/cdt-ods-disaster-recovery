locals {
  vnet_name          = "VNET-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  subnet_name_prefix = "SNET-CDT-PUB-VIP-DDRC-${local.env_letter}"
}

# The primary VNet (per environment)
resource "azurerm_virtual_network" "main" {
  name                = local.vnet_name
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  address_space       = ["10.0.0.0/16"]

  lifecycle {
    ignore_changes = [tags]
  }
}

# The primary subnet for public (Internet) access
resource "azurerm_subnet" "public" {
  name                 = "${local.subnet_name_prefix}-public"
  virtual_network_name = azurerm_virtual_network.main.name
  resource_group_name  = data.azurerm_resource_group.main.name
  address_prefixes     = ["10.0.1.0/24"]
  delegation {
    name = "Microsoft.App/environments"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
  default_outbound_access_enabled = false
}

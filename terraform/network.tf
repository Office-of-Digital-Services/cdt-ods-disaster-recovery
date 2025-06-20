locals {
  vnet_name                         = "VNET-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  subnet_name_prefix                = "SNET-CDT-PUB-VIP-DDRC-${local.env_letter}"
  nsg_prefix                        = "NSG-CDT-PUB-VIP-DDRC-${local.env_letter}"
  private_endpoint_prefix           = lower("pe-cdt-pub-vip-ddrc-${local.env_letter}")
  private_service_connection_prefix = lower("psc-cdt-pub-vip-ddrc-${local.env_letter}")
  public_ip_prefix                  = lower("pip-cdt-pub-vip-ddrc-${local.env_letter}")
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

# NAT Gateway routes private->public traffic from inside the VNet/subnets to the Internet

resource "azurerm_nat_gateway" "main" {
  name                = lower("nat-cdt-pub-vip-ddrc-${local.env_letter}-001")
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  sku_name            = "Standard"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_public_ip" "nat_gateway_ip" {
  name                = "${local.public_ip_prefix}-nat"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_nat_gateway_public_ip_association" "main" {
  nat_gateway_id       = azurerm_nat_gateway.main.id
  public_ip_address_id = azurerm_public_ip.nat_gateway_ip.id
}

resource "azurerm_subnet_nat_gateway_association" "public_subnet" {
  subnet_id      = azurerm_subnet.public.id
  nat_gateway_id = azurerm_nat_gateway.main.id
}

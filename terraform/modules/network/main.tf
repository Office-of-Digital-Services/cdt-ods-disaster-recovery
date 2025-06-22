# This module is responsible for the foundational network topology.

# The primary VNet (per environment)
resource "azurerm_virtual_network" "main" {
  name                = var.vnet_name
  location            = var.location
  resource_group_name = var.resource_group_name
  address_space       = var.vnet_address_space

  lifecycle {
    ignore_changes = [tags]
  }
}

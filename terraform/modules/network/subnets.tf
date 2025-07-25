resource "azurerm_subnet" "main" {
  # This for_each loop creates a subnet for each item in the map variable.
  for_each = var.subnet_addresses

  name                 = "${var.subnet_prefix}-${each.key}"
  virtual_network_name = azurerm_virtual_network.main.name
  resource_group_name  = var.resource_group_name
  address_prefixes     = each.value

  default_outbound_access_enabled = false
  private_link_service_network_policies_enabled = contains(var.private_link_service_policy_subnets, each.key)

  # Delegate the app environment subnets to Container App Environments
  dynamic "delegation" {
    for_each = contains(var.app_env_subnets, each.key) ? [1] : []
    content {
      name = "Microsoft.App/environments"
      service_delegation {
        name    = "Microsoft.App/environments"
        actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
      }
    }
  }

  # For certain subnets, we need to disable private endpoint network policies.
  # Recommended Azure practice to ensure traffic is not blocked from reaching the subnets' private endpoint
  private_endpoint_network_policies = contains(["db", "key_vault", "storage"], each.key) ? "Disabled" : null
}

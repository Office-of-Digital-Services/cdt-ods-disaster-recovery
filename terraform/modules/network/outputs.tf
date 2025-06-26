# ./modules/network/outputs.tf

output "vnet_id" {
  description = "The ID of the created Virtual Network."
  value       = azurerm_virtual_network.main.id
}

output "subnet_ids" {
  description = "A map of all created subnet IDs, keyed by name (e.g., 'public', 'db')."
  # This assumes the subnets are created with a for_each loop over the var.subnet_addresses map.
  # e.g., resource "azurerm_subnet" "main" { for_each = var.subnet_addresses ... }
  value = {
    for key, subnet in azurerm_subnet.main : key => subnet.id
  }
}

output "security_group_ids" {
  description = "A map of the public and worker NSG objects for adding rules externally."
  # This assumes the NSGs are also created with a for_each loop or are otherwise mapped.
  # The root module needs the NSG's name and resource group name to attach rules.
  value = {
    app_gateway = azurerm_network_security_group.app_gateway
    public      = azurerm_network_security_group.public
    worker      = azurerm_network_security_group.worker
  }
}

output "subnet_address_prefixes" {
  description = "A map of all created subnet address prefixes, keyed by name."
  value = {
    for key, subnet in azurerm_subnet.main : key => subnet.address_prefixes
  }
}

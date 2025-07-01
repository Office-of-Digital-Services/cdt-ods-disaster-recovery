resource "azurerm_private_dns_zone" "key_vault" {
  name                = "privatelink.vaultcore.azure.net"
  resource_group_name = var.resource_group_name

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_private_dns_zone_virtual_network_link" "key_vault" {
  name                  = "keyvault-link-${var.env_letter}"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.key_vault.name
  virtual_network_id    = var.virtual_network_id

  lifecycle {
    ignore_changes = [tags]
  }
}

# Private endpoint for the Key Vault
resource "azurerm_private_endpoint" "key_vault" {
  name                = "${var.private_endpoint_prefix}-kv"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.key_vault_subnet_id

  private_service_connection {
    name                           = "${var.private_service_connection_prefix}-kv"
    is_manual_connection           = false
    private_connection_resource_id = local.normalized_key_vault_id
    subresource_names              = ["vault"]
  }

  private_dns_zone_group {
    name                 = azurerm_private_dns_zone.key_vault.name
    private_dns_zone_ids = [azurerm_private_dns_zone.key_vault.id]
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

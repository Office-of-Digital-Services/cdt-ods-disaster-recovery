locals {
  # This map is the single source of truth for creating all related resources.
  # The key is the sub-resource name, and the value is its full private DNS zone name.
  storage_subresources = {
    blob = "privatelink.blob.core.windows.net"
    file = "privatelink.file.core.windows.net"
  }
}

resource "azurerm_private_dns_zone" "storage" {
  for_each = local.storage_subresources

  name                = each.value
  resource_group_name = var.resource_group_name

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_private_dns_zone_virtual_network_link" "storage" {
  for_each = local.storage_subresources

  name                  = "storage-${each.key}-link-${var.env_letter}"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.storage[each.key].name
  virtual_network_id    = var.virtual_network_id

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_private_endpoint" "storage" {
  for_each = local.storage_subresources

  name                = "${var.private_endpoint_prefix}-storage-${each.key}"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.storage_subnet_id

  private_service_connection {
    name                           = "${var.private_service_connection_prefix}-storage-${each.key}"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_storage_account.main.id
    subresource_names              = [each.key]
  }

  private_dns_zone_group {
    name                 = "storage-${each.key}-dns-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.storage[each.key].id]
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

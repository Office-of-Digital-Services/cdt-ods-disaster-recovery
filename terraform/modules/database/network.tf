resource "azurerm_private_dns_zone" "db" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = var.resource_group_name

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_private_dns_zone_virtual_network_link" "db" {
  name                  = "db-link-${var.env_letter}"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.db.name
  virtual_network_id    = var.virtual_network_id

  lifecycle {
    ignore_changes = [tags]
  }
}

# Private endpoint for the database
resource "azurerm_private_endpoint" "db" {
  name                = "${var.private_endpoint_prefix}-db"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.db_subnet_id

  private_service_connection {
    name                           = "${var.private_service_connection_prefix}-db"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_postgresql_flexible_server.main.id
    subresource_names              = ["postgresqlServer"]
  }

  private_dns_zone_group {
    name                 = azurerm_private_dns_zone.db.name
    private_dns_zone_ids = [azurerm_private_dns_zone.db.id]
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

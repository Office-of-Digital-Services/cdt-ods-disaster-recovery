locals {
  # Define secret names for clarity
  postgres_admin_login                = "postgres_admin"
  postgres_admin_password_secret_name = "postgres-admin-password"
}

# Subnet for the database
resource "azurerm_subnet" "db" {
  name                            = "${local.subnet_name_prefix}-db"
  virtual_network_name            = azurerm_virtual_network.main.name
  resource_group_name             = data.azurerm_resource_group.main.name
  address_prefixes                = ["10.0.4.0/27"]
  default_outbound_access_enabled = false
  # Recommended Azure practice to ensure traffic is not blocked from reaching private endpoint
  private_endpoint_network_policies = "Disabled"
}

resource "azurerm_private_dns_zone" "db" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = data.azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "db" {
  name                  = "db-link-${local.env_letter}"
  resource_group_name   = data.azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.db.name
  virtual_network_id    = azurerm_virtual_network.main.id
}

# Generate a random password for PostgreSQL
resource "random_password" "postgres_admin_password" {
  length           = 32
  min_lower        = 4
  min_upper        = 4
  min_numeric      = 4
  min_special      = 4
  special          = true
  override_special = "_%@!-"
}

# Create the secret for PostgreSQL Admin Password using the generated password
resource "azurerm_key_vault_secret" "postgres_admin_password" {
  name         = local.postgres_admin_password_secret_name
  value        = random_password.postgres_admin_password.result
  key_vault_id = azurerm_key_vault.main.id
  content_type = "password"
  depends_on = [
    azurerm_key_vault.main,
    random_password.postgres_admin_password # Ensure password is generated first
  ]
}

# The database resource
resource "azurerm_postgresql_flexible_server" "main" {
  name                = lower("adb-cdt-pub-vip-ddrc-${local.env_letter}-db")
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location
  sku_name            = "B_Standard_B1ms"
  storage_mb          = 32 * 1024
  storage_tier        = "P4"
  version             = "16"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  authentication {
    active_directory_auth_enabled = false
    password_auth_enabled         = true
  }
  public_network_access_enabled = false
  administrator_login           = local.postgres_admin_login
  administrator_password        = azurerm_key_vault_secret.postgres_admin_password.value

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_subnet.db
  ]
}

# Private endpoint for the database
resource "azurerm_private_endpoint" "db" {
  name                = "${local.private_endpoint_prefix}-db"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.db.id

  private_service_connection {
    name                           = "${local.private_service_connection_prefix}-db"
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

  depends_on = [
    azurerm_private_dns_zone.db,
    azurerm_postgresql_flexible_server.main
  ]
}

resource "azurerm_private_dns_zone" "storage_blob" {
  name                = "privatelink.blob.core.windows.net"
  resource_group_name = data.azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone" "storage_file" {
  name                = "privatelink.file.core.windows.net"
  resource_group_name = data.azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "storage_blob" {
  name                  = "storage-blob-link-${local.env_letter}"
  resource_group_name   = data.azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.storage_blob.name
  virtual_network_id    = azurerm_virtual_network.main.id
}

resource "azurerm_private_dns_zone_virtual_network_link" "storage_file" {
  name                  = "storage-file-link-${local.env_letter}"
  resource_group_name   = data.azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.storage_file.name
  virtual_network_id    = azurerm_virtual_network.main.id
}

resource "azurerm_private_endpoint" "storage" {
  name                = "${local.private_endpoint_prefix}-storage"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.storage.id

  private_service_connection {
    name                           = "${local.private_service_connection_prefix}-storage"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_storage_account.main.id
    subresource_names              = ["blob", "file"]
  }

  private_dns_zone_group {
    name = "storage-dns-group"
    private_dns_zone_ids = [
      azurerm_private_dns_zone.storage_blob.id,
      azurerm_private_dns_zone.storage_file.id
    ]
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_storage_account" "main" {
  name                             = "sacdtddrc${lower(local.env_letter)}001"
  location                         = data.azurerm_resource_group.main.location
  resource_group_name              = data.azurerm_resource_group.main.name
  account_tier                     = "Standard"
  account_replication_type         = "RAGRS"
  cross_tenant_replication_enabled = false

  blob_properties {
    last_access_time_enabled = true
    versioning_enabled       = true

    container_delete_retention_policy {
      days = 7
    }

    delete_retention_policy {
      days = 7
    }
  }

  network_rules {
    default_action = "Deny"
    # Allow AzureServices to connect directly, avoiding private endpoint
    # temporary so e.g. Terraform can connect from Azure DevOps
    # until we figure out a more robust (IP based?) ACL
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = []
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_storage_share" "config" {
  name               = "config"
  storage_account_id = azurerm_storage_account.main.id
  quota              = 1
  access_tier        = "Cool"
}

resource "azurerm_storage_share" "requests" {
  name               = "requests"
  storage_account_id = azurerm_storage_account.main.id
  quota              = 5
}

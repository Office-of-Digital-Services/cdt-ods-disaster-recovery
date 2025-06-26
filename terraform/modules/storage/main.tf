# Creates the storage account, the required file shares, and all the private networking components needed to make it
# securely available within the virtual network.

resource "azurerm_storage_account" "main" {
  name                             = var.storage_account_name
  resource_group_name              = var.resource_group_name
  location                         = var.location
  account_tier                     = var.account_tier
  account_replication_type         = var.account_replication_type
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

# This resource block creates all file shares defined in the input map.
resource "azurerm_storage_share" "main" {
  for_each = var.share_configurations

  name               = each.key
  storage_account_id = azurerm_storage_account.main.id
  quota              = each.value.quota_gb
  access_tier        = each.value.access_tier
}

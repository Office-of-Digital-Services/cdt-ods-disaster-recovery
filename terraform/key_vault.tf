locals {
  # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault#certificate_permissions
  all_certificate_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "ManageContacts",
    "ManageIssuers",
    "GetIssuers",
    "ListIssuers",
    "SetIssuers",
    "DeleteIssuers",
  ]
  all_key_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "GetRotationPolicy",
    "SetRotationPolicy",
    "Rotate",
  ]
  all_secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
  ]
  # Normalize key_vault_id to always start with a single slash
  # This checks if azurerm_key_vault.main.id already starts with a slash.
  # If it does, it uses it as is. If not, it prepends a slash.
  normalized_key_vault_id = substr(azurerm_key_vault.main.id, 0, 1) == "/" ? azurerm_key_vault.main.id : "/${azurerm_key_vault.main.id}"
}

resource "azurerm_key_vault" "main" {
  name                     = "KV-CDT-PUB-DDRC-${local.env_letter}-001"
  location                 = data.azurerm_resource_group.main.location
  resource_group_name      = data.azurerm_resource_group.main.name
  sku_name                 = "standard"
  tenant_id                = data.azurerm_client_config.current.tenant_id
  purge_protection_enabled = true

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      tags,
      access_policy # IMPORTANT: Tell Terraform to ignore changes to access policies here since we aren't using inline policies
    ]
  }
}

# Access policy for ENGINEERING_GROUP
resource "azurerm_key_vault_access_policy" "engineering_group_policy" {
  key_vault_id = local.normalized_key_vault_id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.ENGINEERING_GROUP_OBJECT_ID

  certificate_permissions = local.all_certificate_permissions
  key_permissions         = local.all_key_permissions
  secret_permissions      = local.all_secret_permissions

  depends_on = [azurerm_key_vault.main]
}

# Access policy for DEVSECOPS_GROUP
resource "azurerm_key_vault_access_policy" "devsecops_group_policy" {
  key_vault_id = local.normalized_key_vault_id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.DEVSECOPS_OBJECT_ID

  key_permissions    = local.all_key_permissions
  secret_permissions = local.all_secret_permissions

  depends_on = [azurerm_key_vault.main]
}

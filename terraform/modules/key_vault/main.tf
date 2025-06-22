# This module deploys the Azure Key Vault, its private networking components, and the base access policies for administrative groups.

locals {
  # Normalize key_vault_id to always start with a single slash.
  # This checks if azurerm_key_vault.main.id already starts with a slash.
  # If it does, it uses it as is. If not, it prepends a slash.

  # Workaround some weirdness between different envs, where sometimes the slash is present and other times not...
  normalized_key_vault_id = substr(azurerm_key_vault.main.id, 0, 1) == "/" ? azurerm_key_vault.main.id : "/${azurerm_key_vault.main.id}"
}

# The Key Vault resource
resource "azurerm_key_vault" "main" {
  name                     = var.key_vault_name
  location                 = var.location
  resource_group_name      = var.resource_group_name
  sku_name                 = "standard"
  tenant_id                = var.tenant_id
  purge_protection_enabled = true

  network_acls {
    default_action = "Deny"
    bypass         = "None"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      tags,
      access_policy # IMPORTANT: Tell Terraform to ignore changes to access policies here since we aren't using inline policies
    ]
  }
}

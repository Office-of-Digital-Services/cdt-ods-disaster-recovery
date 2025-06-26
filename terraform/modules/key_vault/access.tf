# Create access policies for all entries in the input map.
resource "azurerm_key_vault_access_policy" "base" {
  for_each = var.base_access_policy_object_ids

  key_vault_id = local.normalized_key_vault_id
  tenant_id    = var.tenant_id
  object_id    = each.value

  certificate_permissions = var.all_certificate_permissions
  key_permissions         = var.all_key_permissions
  secret_permissions      = var.all_secret_permissions

  # This ensures the Key Vault itself is created before trying to attach a policy.
  depends_on = [azurerm_key_vault.main]
}

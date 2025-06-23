# https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references?tabs=azure-cli#granting-your-app-access-to-key-vault
resource "azurerm_key_vault_access_policy" "container_app_worker_access" {
  key_vault_id = local.normalized_key_vault_id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_user_assigned_identity.worker_app_identity.principal_id

  secret_permissions = ["Get", "List"]

  depends_on = [
    azurerm_key_vault.main,
    azurerm_user_assigned_identity.worker_app_identity
  ]
}

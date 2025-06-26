locals {
  azure_communication_connection_string_name = "azure-communication-connection-string"
  azure_communication_from_email_name        = "azure-communication-from-email"
}

resource "azurerm_key_vault_secret" "azure_communication_connection_string" {
  name         = local.azure_communication_connection_string_name
  value        = azurerm_communication_service.main.primary_connection_string
  key_vault_id = var.key_vault_id
  content_type = "password"
}

resource "azurerm_key_vault_secret" "azure_communication_from_email" {
  name         = local.azure_communication_from_email_name
  value        = "DoNotReply@${azurerm_email_communication_service_domain.azure_managed.mail_from_sender_domain}"
  key_vault_id = var.key_vault_id
}

locals {
  azure_communication_connection_string_name = "azure-communication-connection-string"
  azure_communication_from_email_name        = "azure-communication-from-email"
  # Determine the correct sender domain based on the environment.
  # If is_prod is true, use the custom domain; otherwise, use the Azure-managed domain.
  sender_domain = var.is_prod ? azurerm_email_communication_service_domain.custom[0].mail_from_sender_domain : azurerm_email_communication_service_domain.azure_managed[0].mail_from_sender_domain
  sender_email = "DoNotReply@${local.sender_domain}"
}

resource "azurerm_key_vault_secret" "azure_communication_connection_string" {
  name         = local.azure_communication_connection_string_name
  value        = azurerm_communication_service.main.primary_connection_string
  key_vault_id = var.key_vault_id
  content_type = "password"
}

resource "azurerm_key_vault_secret" "azure_communication_from_email" {
  name         = local.azure_communication_from_email_name
  value        = local.sender_email
  key_vault_id = var.key_vault_id

  # This resource depends on the creation of one of the two possible domains.
  depends_on = [
    azurerm_email_communication_service_domain.azure_managed[0],
    azurerm_email_communication_service_domain.custom[0]
  ]
}

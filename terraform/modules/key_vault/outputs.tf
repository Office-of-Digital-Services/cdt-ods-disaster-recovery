output "key_vault_id" {
  description = "The unique ID of the created Key Vault. Required for other resources that need to create a secret or access policy."
  value       = local.normalized_key_vault_id
}

output "private_endpoint_ip_address" {
  description = "The private IP address of the Key Vault's private endpoint. Required by NSG rules."
  value       = azurerm_private_endpoint.key_vault.private_service_connection[0].private_ip_address
}

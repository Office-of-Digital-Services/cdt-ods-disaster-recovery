output "app_gateway_id" {
  description = "The unique ID of the Application Gateway."
  value       = azurerm_application_gateway.main.id
}

output "identity_principal_id" {
  description = "The Principal ID of the gateway's managed identity, for assigning access policies."
  value       = azurerm_user_assigned_identity.app_gateway.principal_id
}

output "public_ip_address" {
  description = "The public IP address assigned to the gateway, which is the public entry point for users."
  value       = azurerm_public_ip.app_gateway.ip_address
}

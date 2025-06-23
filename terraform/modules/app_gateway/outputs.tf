output "app_gateway_id" {
  description = "The unique ID of the Application Gateway."
  value       = azurerm_application_gateway.main.id
}

output "public_ip_address" {
  description = "The public IP address assigned to the gateway, which is the public entry point for users."
  value       = azurerm_public_ip.app_gateway.ip_address
}

output "server_id" {
  description = "The unique ID of the PostgreSQL server."
  value       = azurerm_postgresql_flexible_server.main.id
}

output "server_fqdn" {
  description = "The Fully Qualified Domain Name of the server for application connections."
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "private_endpoint_ip_address" {
  description = "The private IP address of the database, needed by root module NSG rules."
  value       = azurerm_private_endpoint.db.private_service_connection[0].private_ip_address
}

output "admin_password_secret_name" {
  description = "The name of the created admin password secret in Key Vault."
  value       = azurerm_key_vault_secret.postgres_admin_password.name
}

output "connection_string_secret_name" {
  description = "The name of the connection string secret that the module created in Key Vault."
  value       = local.azure_communication_connection_string_name
}

output "from_email_secret_name" {
  description = "The name of the 'from email' secret that the module created in Key Vault."
  value       = local.azure_communication_from_email_name
}

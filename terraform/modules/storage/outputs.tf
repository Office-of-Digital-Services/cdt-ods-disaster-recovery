output "storage_account_id" {
  description = "The unique ID of the storage account."
  value       = azurerm_storage_account.main.id
}

output "storage_account_primary_access_key" {
  description = "The primary access key for the storage account, needed by the application module."
  value       = azurerm_storage_account.main.primary_access_key
  sensitive   = true
}

output "share_names" {
  description = "A map of the created file share names."
  # This assumes the shares are created with a for_each loop over var.share_configurations
  value = {
    for key, share in azurerm_storage_share.main : key => share.name
  }
}

output "private_endpoint_ip_addresses" {
  description = "A map of private IP addresses for the storage endpoints, keyed by sub-resource (blob, file)."
  # This 'for' loop iterates over the 'azurerm_private_endpoint.storage' resource,
  # which was created with for_each. It builds a map where the key is the
  # sub-resource name (e.g., "blob") and the value is its private IP address.
  value = {
    for key, endpoint in azurerm_private_endpoint.storage : key => endpoint.private_service_connection[0].private_ip_address
  }
}

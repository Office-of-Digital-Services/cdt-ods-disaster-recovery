output "app_fqdns" {
  description = "A map of the stable, non-revision-specific Fully Qualified Domain Names for the container apps."
  value = {
    web         = "${azurerm_container_app.web.name}.${azurerm_container_app_environment.public.default_domain}"
    functions   = "${azurerm_container_app.functions.name}.${azurerm_container_app_environment.worker.default_domain}"
  }
}

output "default_domains" {
  description = "A map of the default domains of each Container App Environment."
  value = {
    public = azurerm_container_app_environment.public.default_domain
    worker = azurerm_container_app_environment.worker.default_domain
  }
}

output "identity_object_ids" {
  description = "A map of the Object IDs for the application managed identities."
  value = {
    web       = azurerm_user_assigned_identity.web_app_identity.principal_id
    worker    = azurerm_user_assigned_identity.worker_app_identity.principal_id
    functions = azurerm_user_assigned_identity.functions_app_identity.principal_id
  }
}

output "azurerm_container_app_environment_public_id" {
  description = "The Container App Environment for public-facing web app(s)"
  value       = azurerm_container_app_environment.public.id
}

output "functions_app_hostkey" {
  description = "The host key of the Functions App."
  value       = random_password.main["alert-to-slack-function-key"].result
  sensitive   = true
}

output "app_fqdns" {
  description = "A map of the stable, non-revision-specific Fully Qualified Domain Names for the container apps."
  value = {
    web   = "${azurerm_container_app.web.name}.${azurerm_container_app_environment.public.default_domain}"
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
    web    = azurerm_user_assigned_identity.web_app_identity.principal_id
    worker = azurerm_user_assigned_identity.worker_app_identity.principal_id
  }
}

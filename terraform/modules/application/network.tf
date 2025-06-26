resource "azurerm_private_dns_zone" "container_apps" {
  name                = azurerm_container_app_environment.public.default_domain
  resource_group_name = var.resource_group_name

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_container_app_environment.public
  ]
}

resource "azurerm_private_dns_a_record" "cae_wildcard" {
  name                = "*"
  zone_name           = azurerm_private_dns_zone.container_apps.name
  resource_group_name = var.resource_group_name
  ttl                 = 300
  records             = [azurerm_container_app_environment.public.static_ip_address]

  depends_on = [
    azurerm_private_dns_zone.container_apps
  ]
}

resource "azurerm_private_dns_zone_virtual_network_link" "container_apps_to_vnet" {
  name                  = lower("cae-dns-link-${var.env_letter}")
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.container_apps.name
  virtual_network_id    = var.virtual_network_id

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_private_dns_zone.container_apps
  ]
}

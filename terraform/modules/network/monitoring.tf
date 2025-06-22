# This resource block creates diagnostic settings for all three NSGs
# defined in security_groups.tf: app_gateway, public, and worker.
resource "azurerm_monitor_diagnostic_setting" "nsg" {
  # Loop over the NSG resources
  for_each = {
    app_gateway = azurerm_network_security_group.app_gateway
    public      = azurerm_network_security_group.public
    worker      = azurerm_network_security_group.worker
  }

  name                       = "${var.diagnostic_setting_prefix}-nsg-${each.key}"
  target_resource_id         = each.value.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category_group = "allLogs"
  }
}

# Create a User-Assigned Managed Identity for the web App
resource "azurerm_user_assigned_identity" "app_gateway" {
  name                = "umi-${var.app_gateway_name}"
  resource_group_name = var.resource_group_name
  location            = var.location

  lifecycle {
    ignore_changes = [tags]
  }
}

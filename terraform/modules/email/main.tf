# This module encapsulates all components needed to provide email services.

resource "azurerm_communication_service" "main" {
  name                = var.communication_service_name
  resource_group_name = var.resource_group_name
  data_location       = var.data_location

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_email_communication_service" "main" {
  name                = var.communication_service_name
  resource_group_name = var.resource_group_name
  data_location       = var.data_location

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_email_communication_service_domain" "azure_managed" {
  count = var.is_prod ? 0 : 1

  # when domain_management="AzureManaged",
  # the name has to be "AzureManagedDomain"
  # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/email_communication_service_domain#name-19
  name                             = "AzureManagedDomain"
  email_service_id                 = azurerm_email_communication_service.main.id
  domain_management                = "AzureManaged"
  user_engagement_tracking_enabled = true

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_communication_service_email_domain_association" "azure_managed" {
  count = var.is_prod ? 0 : 1

  communication_service_id = azurerm_communication_service.main.id
  email_service_domain_id  = azurerm_email_communication_service_domain.azure_managed[0].id
}

# This domain is only created when var.is_prod is true.
resource "azurerm_email_communication_service_domain" "custom" {
  count = var.is_prod ? 1 : 0

  name                             = var.custom_domain_name
  email_service_id                 = azurerm_email_communication_service.main.id
  domain_management                = "CustomerManaged"
  user_engagement_tracking_enabled = true

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_communication_service_email_domain_association" "custom" {
  count = var.is_prod ? 1 : 0

  communication_service_id = azurerm_communication_service.main.id
  email_service_domain_id  = azurerm_email_communication_service_domain.custom[0].id
}

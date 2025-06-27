locals {
  # https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references?tabs=azure-cli#granting-your-app-access-to-key-vault
  key_vault_policy_secret_permissions = ["Get", "List"]
}

# for the App Gateway
resource "azurerm_key_vault_access_policy" "app_gateway_cert_access" {
  key_vault_id = module.key_vault.key_vault_id
  tenant_id    = local.tenant_id
  object_id    = module.app_gateway.identity_principal_id

  certificate_permissions = ["Get"]
  secret_permissions = ["Get"]
}

# for the web app
resource "azurerm_key_vault_access_policy" "container_app_web_access" {
  key_vault_id = module.key_vault.key_vault_id
  tenant_id    = local.tenant_id
  object_id    = module.application.identity_object_ids.web

  secret_permissions = local.key_vault_policy_secret_permissions
}

# for the worker app
resource "azurerm_key_vault_access_policy" "container_app_worker_access" {
  key_vault_id = module.key_vault.key_vault_id
  tenant_id    = local.tenant_id
  object_id    = module.application.identity_object_ids.worker

  secret_permissions = local.key_vault_policy_secret_permissions
}

# These rules are for the 'app_gateway' NSG created in the network module.
# They allow outbound traffic to private IP addresses of the key vault.
resource "azurerm_network_security_rule" "app_gateway_to_kv" {
  name                        = "AllowOutbound-kv"
  priority                    = 100
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "443"
  source_address_prefix       = "*"
  resource_group_name         = local.resource_group_name
  network_security_group_name = module.network.security_group_ids.app_gateway.name
  destination_address_prefix  = module.key_vault.private_endpoint_ip_address
}

# These rules are for the 'public' NSG created in the network module.
# They allow outbound traffic to private IP addresses of the database, key vault, and storage account.
resource "azurerm_network_security_rule" "public_to_db" {
  name                        = "AllowOutbound-db"
  priority                    = 300
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "5432"
  source_address_prefix       = "*"
  resource_group_name         = local.resource_group_name
  network_security_group_name = module.network.security_group_ids.public.name
  destination_address_prefix  = module.database.private_endpoint_ip_address
}

resource "azurerm_network_security_rule" "public_to_kv" {
  name                        = "AllowOutbound-kv"
  priority                    = 310
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "443"
  source_address_prefix       = "*"
  resource_group_name         = local.resource_group_name
  network_security_group_name = module.network.security_group_ids.public.name
  destination_address_prefix  = module.key_vault.private_endpoint_ip_address
}

resource "azurerm_network_security_rule" "public_to_storage_blob" {
  name                        = "AllowOutbound-storage-blob"
  priority                    = 320
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "443"
  source_address_prefix       = "*"
  resource_group_name         = local.resource_group_name
  network_security_group_name = module.network.security_group_ids.public.name
  destination_address_prefix  = module.storage.private_endpoint_ip_addresses.blob
}

resource "azurerm_network_security_rule" "public_to_storage_file" {
  name                        = "AllowOutbound-storage-file"
  priority                    = 330
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "445" # Must be 445 for SMB/Azure Files
  source_address_prefix       = "*"
  resource_group_name         = local.resource_group_name
  network_security_group_name = module.network.security_group_ids.public.name
  destination_address_prefix  = module.storage.private_endpoint_ip_addresses.file
}

# These rules are for the 'worker' NSG created in the network module.
# They allow outbound traffic to the private IP addresses of the database,
# key vault, and storage account.

resource "azurerm_network_security_rule" "worker_to_db" {
  name                        = "AllowOutbound-db"
  priority                    = 200
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "5432"
  source_address_prefix       = "*"
  resource_group_name         = local.resource_group_name
  network_security_group_name = module.network.security_group_ids.worker.name
  destination_address_prefix  = module.database.private_endpoint_ip_address
}

resource "azurerm_network_security_rule" "worker_to_kv" {
  name                        = "AllowOutbound-kv"
  priority                    = 210
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "443"
  source_address_prefix       = "*"
  resource_group_name         = local.resource_group_name
  network_security_group_name = module.network.security_group_ids.worker.name
  destination_address_prefix  = module.key_vault.private_endpoint_ip_address
}

resource "azurerm_network_security_rule" "worker_to_storage_blob" {
  name                        = "AllowOutbound-storage-blob"
  priority                    = 220
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "443"
  source_address_prefix       = "*"
  resource_group_name         = local.resource_group_name
  network_security_group_name = module.network.security_group_ids.worker.name
  destination_address_prefix  = module.storage.private_endpoint_ip_addresses.blob
}

resource "azurerm_network_security_rule" "worker_to_storage_file" {
  name                        = "AllowOutbound-storage-file"
  priority                    = 230
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "445" # Must be 445 for SMB/Azure Files
  source_address_prefix       = "*"
  resource_group_name         = local.resource_group_name
  network_security_group_name = module.network.security_group_ids.worker.name
  destination_address_prefix  = module.storage.private_endpoint_ip_addresses.file
}

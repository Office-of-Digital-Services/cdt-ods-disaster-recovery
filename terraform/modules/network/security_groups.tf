# Creates the Network Security Groups and defines the foundational security rules for traffic flow.

# NSG for the public subnet (where container apps run).
# Note: Rules with external dependencies (db, kv, storage) are omitted here.
resource "azurerm_network_security_group" "public" {
  name                = "${var.nsg_prefix}-public"
  location            = var.location
  resource_group_name = var.resource_group_name

  lifecycle {
    ignore_changes = [tags]
  }
}

# Foundational rules for the Public NSG. Added externally since there are other
# external rules not defined in this module.

# Allow health probes and traffic from the VNet's internal load balancer
resource "azurerm_network_security_rule" "public_allow_inbound_load_balancer" {
  name                        = "AllowInbound-AzureLoadBalancer"
  priority                    = 110
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "AzureLoadBalancer"
  destination_address_prefix  = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.public.name
}

# Allow the Container Apps control plane to manage the environment
resource "azurerm_network_security_rule" "public_allow_inbound_container_apps_mgmt" {
  name                        = "AllowInbound-ContainerAppsManagement"
  priority                    = 120
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "ContainerApps"
  destination_address_prefix  = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.public.name
}

# NSG for the Worker Subnet.
# Note: Rules with external dependencies (db, kv, storage) are omitted here.
resource "azurerm_network_security_group" "worker" {
  name                = "${var.nsg_prefix}-worker"
  location            = var.location
  resource_group_name = var.resource_group_name

  lifecycle {
    ignore_changes = [tags]
  }
}

# Foundational rules for the worker NSG. Added externally since there are other
# external rules not defined in this module.

# Rule to deny inbound to the worker
resource "azurerm_network_security_rule" "worker_deny_inbound" {
  name                        = "DenyInbound"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Deny"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.worker.name
}

# subnet to NSG Associations

resource "azurerm_subnet_network_security_group_association" "public" {
  subnet_id                 = azurerm_subnet.main["public"].id
  network_security_group_id = azurerm_network_security_group.public.id
}
resource "azurerm_subnet_network_security_group_association" "worker" {
  subnet_id                 = azurerm_subnet.main["worker"].id
  network_security_group_id = azurerm_network_security_group.worker.id
}

# Creates the Network Security Groups and defines the foundational security rules for traffic flow.

# NSG for the Application Gateway subnet.
resource "azurerm_network_security_group" "app_gateway" {
  name                = "${var.nsg_prefix}-app-gateway"
  location            = var.location
  resource_group_name = var.resource_group_name

  lifecycle {
    ignore_changes = [tags]
  }
}

# Foundational rules for the Application Gateway NSG.

# Rule to allow health and management probes from the Application Gateway service. This is required.
resource "azurerm_network_security_rule" "app_gateway_allow_inbound_manager" {
  name                        = "AllowInbound-GatewayManager"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "65200-65535"
  source_address_prefix       = "GatewayManager"
  destination_address_prefix  = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.app_gateway.name
}

# Rules to allow inbound traffic from the Azure FrontDoor to the gateway listener.
# Separate rules for 80, 443 were necessary as a combined rule wasn't taking effect.
resource "azurerm_network_security_rule" "app_gateway_allow_inbound_frontdoor_http" {
  name                        = "AllowInbound-FrontDoor-HTTP"
  priority                    = 110
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "80"
  source_address_prefix       = "AzureFrontDoor.Backend"
  destination_address_prefix  = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.app_gateway.name
}
resource "azurerm_network_security_rule" "app_gateway_allow_inbound_frontdoor_https" {
  name                        = "AllowInbound-FrontDoor-HTTPS"
  priority                    = 115
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "443"
  source_address_prefix       = "AzureFrontDoor.Backend"
  destination_address_prefix  = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.app_gateway.name
}

# Allow inbound from the general Internet.
# Separate rules for 80, 443 were necessary as a combined rule wasn't taking effect.
resource "azurerm_network_security_rule" "app_gateway_allow_inbound_internet_http" {
  name                        = "AllowInbound-Internet-HTTP"
  priority                    = 120
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "80"
  source_address_prefix       = "Internet"
  destination_address_prefix  = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.app_gateway.name
}
resource "azurerm_network_security_rule" "app_gateway_allow_inbound_internet_https" {
  name                        = "AllowInbound-Internet-HTTPS"
  priority                    = 125
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "443"
  source_address_prefix       = "Internet"
  destination_address_prefix  = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.app_gateway.name
}

# This rule allows the gateway to resolve internal FQDNs via the Azure DNS service.
resource "azurerm_network_security_rule" "app_gateway_allow_outbound_dns_private" {
  name                        = "AllowOutbound-DNS"
  priority                    = 150
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "*" # DNS uses both TCP and UDP
  source_port_range           = "*"
  destination_port_range      = "53"
  source_address_prefix       = "*"
  # Using the specific IP for Azure's internal DNS resolver
  # A globally consistent, reserved address that facilitates communication between apps and core Azure platform services.
  destination_address_prefix  = "168.63.129.16"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.app_gateway.name
}

# This rule allows the gateway to resolve public FQDNs for its own operational needs.
resource "azurerm_network_security_rule" "app_gateway_allow_outbound_dns_public" {
  name                        = "AllowOutbound-DNS-Public"
  priority                    = 151
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "53"
  source_address_prefix       = "*"
  destination_address_prefix  = "Internet"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.app_gateway.name
}

# Rule to allow the gateway to send traffic (including health probes) to the backend apps
resource "azurerm_network_security_rule" "app_gateway_allow_outbound_apps" {
  name                        = "AllowOutbound-ToApps"
  priority                    = 200
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_ranges     = ["8000", "8081"]
  source_address_prefix       = azurerm_subnet.main["app_gateway"].address_prefixes[0]
  destination_address_prefix  = azurerm_subnet.main["public"].address_prefixes[0]
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.app_gateway.name
}

# Rule to allow the gateway to send traffic to the Internet
resource "azurerm_network_security_rule" "app_gateway_allow_outbound_internet" {
  name                        = "AllowOutbound-Internet"
  priority                    = 210
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "443"
  source_address_prefix       = "*"
  destination_address_prefix  = "Internet"
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.app_gateway.name
}

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

# Allow traffic from the Application Gateway's subnet
resource "azurerm_network_security_rule" "public_allow_inbound_app_gateway" {
  name                        = "AllowInbound-AppGateway"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_ranges     = ["8000", "8081"] # web and pgweb ports
  source_address_prefix       = azurerm_subnet.main["app_gateway"].address_prefixes[0]
  destination_address_prefix  = azurerm_subnet.main["public"].address_prefixes[0]
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.public.name
}

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

# Explicitly allow outbound traffic from the apps back to the Application Gateway subnet.
# This rule should not be necessary due to stateful NSG rules, but is added to resolve persistent timeouts.
resource "azurerm_network_security_rule" "public_allow_outbound_to_app_gateway" {
  name                        = "AllowOutbound-ToAppGateway"
  priority                    = 130
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = azurerm_subnet.main["public"].address_prefixes[0]
  destination_address_prefix  = azurerm_subnet.main["app_gateway"].address_prefixes[0]
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

resource "azurerm_subnet_network_security_group_association" "app_gateway" {
  subnet_id                 = azurerm_subnet.main["app_gateway"].id
  network_security_group_id = azurerm_network_security_group.app_gateway.id
}
resource "azurerm_subnet_network_security_group_association" "public" {
  subnet_id                 = azurerm_subnet.main["public"].id
  network_security_group_id = azurerm_network_security_group.public.id
}
resource "azurerm_subnet_network_security_group_association" "worker" {
  subnet_id                 = azurerm_subnet.main["worker"].id
  network_security_group_id = azurerm_network_security_group.worker.id
}

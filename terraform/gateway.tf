# Application Gateway routes public->private traffic from the Internet to inside the VNet/subnet

locals {
  backend_address_pool_name      = "${azurerm_virtual_network.main.name}-pool"
  frontend_port_name             = "${azurerm_virtual_network.main.name}-public-port"
  frontend_ip_configuration_name = "${azurerm_virtual_network.main.name}-public-ip"
  http_setting_name              = "${azurerm_virtual_network.main.name}-settings"
  listener_name                  = "${azurerm_virtual_network.main.name}-listener"
  probe_name                     = "${azurerm_virtual_network.main.name}-probe"
  request_routing_rule_name      = "${azurerm_virtual_network.main.name}-rule"
}

resource "azurerm_subnet" "gateway" {
  name                 = "${local.subnet_name_prefix}-gateway"
  virtual_network_name = azurerm_virtual_network.main.name
  resource_group_name  = data.azurerm_resource_group.main.name
  address_prefixes     = ["10.0.0.0/24"]
}

resource "azurerm_public_ip" "gateway" {
  name                = "${local.public_ip_prefix}-gateway"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_security_group" "gateway" {
  name                = "${local.nsg_prefix}-gateway"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name

  # Rule to allow health and management probes from the Application Gateway service. This is required.
  security_rule {
    name                       = "AllowInbound-GatewayManager"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "65200-65535"
    source_address_prefix      = "GatewayManager"
    destination_address_prefix = "*"
  }
  # Rule to allow inbound traffic from the Azure FrontDoor to the gateway listener.
  security_rule {
    name                       = "AllowInbound-FrontDoor"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80" # Matches the frontend_port
    source_address_prefix      = "AzureFrontDoor.Backend"
    destination_address_prefix = "*"
  }
  # Rule to allow the gateway to send traffic (including health probes) to the backend apps
  security_rule {
    name                       = "AllowOutbound-ToApps"
    priority                   = 300
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000,8081" # Matches the web and pgweb backend ports
    source_address_prefix      = azurerm_subnet.gateway.address_prefixes[0]
    destination_address_prefix = azurerm_subnet.public.address_prefixes[0]
  }
  # Low-priority catch-all Deny for In/Outbound traffic to be more explicit
  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "DenyAllOutbound"
    priority                   = 4096
    direction                  = "Outbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "gateway" {
  subnet_id                 = azurerm_subnet.gateway.id
  network_security_group_id = azurerm_network_security_group.gateway.id
}

resource "azurerm_network_security_group" "public" {
  name                = "${local.nsg_prefix}-public"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name

  # Rule to allow traffic from the Application Gateway's subnet
  security_rule {
    name                       = "AllowInbound-AppGateway"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000,8081" # the web and pgweb ports
    source_address_prefix      = azurerm_subnet.gateway.address_prefixes[0]
    destination_address_prefix = "*"
  }
  # Rule to allow outbound traffic to the internet for API calls
  security_rule {
    name                       = "AllowOutbound-Internet"
    priority                   = 100
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "Internet"
  }
  # Rule to allow outbound to the database
  security_rule {
    name                       = "AllowOutbound-db"
    priority                   = 300
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_address_prefix      = "*"
    destination_address_prefix = azurerm_private_endpoint.db.private_service_connection[0].private_ip_address
  }
  # Rule to allow outbound to the key vault
  security_rule {
    name                       = "AllowOutbound-kv"
    priority                   = 310
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = azurerm_private_endpoint.keyvault.private_service_connection[0].private_ip_address
  }
  # Rule to allow outbound to the storage account
  security_rule {
    name                       = "AllowOutbound-Storage"
    priority                   = 320
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "445" # Port for Azure Files (SMB)
    source_address_prefix      = "*"
    destination_address_prefix = azurerm_private_endpoint.storage.private_service_connection[0].private_ip_address
  }
}

resource "azurerm_subnet_network_security_group_association" "public" {
  subnet_id                 = azurerm_subnet.public.id
  network_security_group_id = azurerm_network_security_group.public.id
}

resource "azurerm_application_gateway" "main" {
  name                = "AGW-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location

  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }

  gateway_ip_configuration {
    name      = "gateway-ip-configuration"
    subnet_id = azurerm_subnet.gateway.id
  }

  frontend_port {
    name = local.frontend_port_name
    port = 80
  }
  frontend_ip_configuration {
    name                 = local.frontend_ip_configuration_name
    public_ip_address_id = azurerm_public_ip.gateway.id
  }

  backend_address_pool {
    name  = local.backend_address_pool_name
    fqdns = ["${azurerm_container_app.web.name}.${azurerm_container_app_environment.main.default_domain}"]
  }
  backend_address_pool {
    name  = "${local.backend_address_pool_name}-pgweb"
    fqdns = ["${azurerm_container_app.pgweb.name}.${azurerm_container_app_environment.main.default_domain}"]
  }

  backend_http_settings {
    name                                = local.backend_address_pool_name
    cookie_based_affinity               = "Disabled"
    path                                = "/"
    pick_host_name_from_backend_address = true
    port                                = 8000
    probe_name                          = local.probe_name
    protocol                            = "Http"
    request_timeout                     = 20
  }
  backend_http_settings {
    name                                = "${local.http_setting_name}-pgweb"
    cookie_based_affinity               = "Disabled"
    path                                = "/"
    pick_host_name_from_backend_address = true
    port                                = 8081 # pgweb's target port
    protocol                            = "Http"
    request_timeout                     = 20
  }

  http_listener {
    name                           = local.listener_name
    frontend_ip_configuration_name = local.frontend_ip_configuration_name
    frontend_port_name             = local.frontend_port_name
    protocol                       = "Http"
    host_name                      = local.hostname
  }

  probe {
    name                                      = local.probe_name
    interval                                  = 30
    path                                      = "/healthcheck"
    protocol                                  = "Http"
    timeout                                   = 15
    unhealthy_threshold                       = 3
    pick_host_name_from_backend_http_settings = true
  }

  url_path_map {
    name                               = "${local.request_routing_rule_name}-pathmap"
    default_backend_address_pool_name  = local.backend_address_pool_name
    default_backend_http_settings_name = local.http_setting_name

    path_rule {
      name                       = "pgweb-rule"
      paths                      = ["/pgweb", "/pgweb/*"]
      backend_address_pool_name  = "${local.backend_address_pool_name}-pgweb"
      backend_http_settings_name = "${local.http_setting_name}-pgweb"
    }
  }

  request_routing_rule {
    name               = local.request_routing_rule_name
    rule_type          = "PathBasedRouting"
    http_listener_name = local.listener_name
    url_path_map_name  = "${local.request_routing_rule_name}-pathmap"
    priority           = 100
  }

  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }

  lifecycle {
    ignore_changes = [tags]
  }

  depends_on = [
    azurerm_subnet.gateway,
    azurerm_public_ip.gateway,
    azurerm_container_app_environment.main,
    azurerm_container_app.web,
    azurerm_container_app.pgweb,
  ]
}

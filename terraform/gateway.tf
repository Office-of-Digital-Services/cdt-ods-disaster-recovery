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

  request_routing_rule {
    name               = local.request_routing_rule_name
    rule_type          = "Basic"
    http_listener_name = local.listener_name
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
  ]
}

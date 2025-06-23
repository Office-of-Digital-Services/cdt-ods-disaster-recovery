# This module manages the public-facing Application Gateway and WAF.

locals {
  backend_address_pool_name      = "${var.app_gateway_name}-pool"
  frontend_port_name             = "${var.app_gateway_name}-public-port"
  frontend_ip_configuration_name = "${var.app_gateway_name}-public-ip"
  http_setting_name              = "${var.app_gateway_name}-settings"
  listener_name                  = "${var.app_gateway_name}-listener"
  probe_name                     = "${var.app_gateway_name}-probe"
  request_routing_rule_name      = "${var.app_gateway_name}-rule"
}

resource "azurerm_public_ip" "app_gateway" {
  name                = "${var.public_ip_prefix}-app-gateway"
  resource_group_name = var.resource_group_name
  location            = var.location
  allocation_method   = "Static"
  sku                 = "Standard"
  domain_name_label   = "${var.public_ip_prefix}-app-gateway"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_application_gateway" "main" {
  name                = var.app_gateway_name
  resource_group_name = var.resource_group_name
  location            = var.location

  sku {
    name     = var.sku_name
    tier     = var.sku_tier
    capacity = 2
  }

  gateway_ip_configuration {
    name      = "gateway-ip-configuration"
    subnet_id = var.app_gateway_subnet_id
  }

  frontend_port {
    name = local.frontend_port_name
    port = 80
  }
  frontend_ip_configuration {
    name                 = local.frontend_ip_configuration_name
    public_ip_address_id = azurerm_public_ip.app_gateway.id
  }

  backend_address_pool {
    name  = "${local.backend_address_pool_name}-web"
    fqdns = [var.backend_fqdns.web]
  }
  backend_address_pool {
    name  = "${local.backend_address_pool_name}-pgweb"
    fqdns = [var.backend_fqdns.pgweb]
  }

  backend_http_settings {
    name                                = "${local.http_setting_name}-web"
    cookie_based_affinity               = "Disabled"
    host_name                           = var.backend_fqdns.web
    path                                = "/"
    port                                = 80
    probe_name                          = "${local.probe_name}-web"
    protocol                            = "Http"
    request_timeout                     = 20
  }
  backend_http_settings {
    name                                = "${local.http_setting_name}-pgweb"
    host_name                           = var.backend_fqdns.pgweb
    cookie_based_affinity               = "Disabled"
    path                                = "/"
    port                                = 80
    probe_name                          = "${local.probe_name}-pgweb"
    protocol                            = "Http"
    request_timeout                     = 20
  }

  http_listener {
    name                           = local.listener_name
    frontend_ip_configuration_name = local.frontend_ip_configuration_name
    frontend_port_name             = local.frontend_port_name
    protocol                       = "Http"
    # host_name setting configures the public-facing side of the Application Gateway.
    # It tells the gateway which domain names it should listen to from the end-user's browser.
    # Null configures a "basic" listener, the gateway responds to any request sent to its IP address or its default Azure FQDN
    host_name                      = var.is_prod ? var.hostname : null
  }

  probe {
    name                                      = "${local.probe_name}-web"
    interval                                  = 30
    path                                      = var.probe_path
    protocol                                  = "Http"
    timeout                                   = 15
    unhealthy_threshold                       = 3
    host                                      = var.backend_fqdns.web
    match {
      status_code = ["200-399"]
    }
  }
  probe {
    name                                      = "${local.probe_name}-pgweb"
    interval                                  = 30
    path                                      = "/"
    protocol                                  = "Http"
    timeout                                   = 15
    unhealthy_threshold                       = 3
    host                                      = var.backend_fqdns.pgweb
    match {
      status_code = ["200-399"]
    }
  }

  url_path_map {
    name                               = "${local.request_routing_rule_name}-pathmap"
    default_backend_address_pool_name  = "${local.backend_address_pool_name}-web"
    default_backend_http_settings_name = "${local.http_setting_name}-web"

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
}

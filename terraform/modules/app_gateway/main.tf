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

resource "azurerm_key_vault_certificate" "app_gateway_auto" {
  name         = "${var.app_gateway_name}-cert-auto"
  key_vault_id = var.key_vault_id

  certificate_policy {
    issuer_parameters {
      name = "Self"
    }
    key_properties {
      exportable = true
      key_size   = 4096
      key_type   = "RSA"
      reuse_key  = false
    }
    lifetime_action {
      action {
        action_type = "AutoRenew"
      }
      trigger {
        days_before_expiry = 30
      }
    }
    secret_properties {
      content_type = "application/x-pkcs12"
    }
    x509_certificate_properties {
      subject            = "CN=${azurerm_public_ip.app_gateway.fqdn}"
      validity_in_months = 12
      key_usage = [
        "digitalSignature",
        "keyEncipherment",
      ]
      extended_key_usage = [
        # Replaced "serverAuth" with its numerical OID to avoid an error
        "1.3.6.1.5.5.7.3.1",
      ]
    }
  }
}

resource "azurerm_application_gateway" "main" {
  name                = var.app_gateway_name
  resource_group_name = var.resource_group_name
  location            = var.location

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.app_gateway.id]
  }

  ssl_certificate {
    name                = azurerm_key_vault_certificate.app_gateway_auto.name
    key_vault_secret_id = azurerm_key_vault_certificate.app_gateway_auto.secret_id
  }

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
  frontend_port {
    name = "${local.frontend_port_name}-443"
    port = 443
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
    # Always override the host header.
    pick_host_name_from_backend_address = false
    # In prod, use the custom hostname.
    # In non-prod, use the App Gateway's default FQDN.
    host_name                           = var.is_prod ? var.hostname : azurerm_public_ip.app_gateway.fqdn
    path                                = "/"
    port                                = 80
    probe_name                          = "${local.probe_name}-web"
    protocol                            = "Http"
    request_timeout                     = 20
  }
  backend_http_settings {
    name                                = "${local.http_setting_name}-pgweb"
    cookie_based_affinity               = "Disabled"
    host_name                           = var.backend_fqdns.pgweb
    # needs a trailing slash
    path                                = "/pgweb/"
    port                                = 80
    probe_name                          = "${local.probe_name}-pgweb"
    protocol                            = "Http"
    request_timeout                     = 20
  }

  # For non-prod, create simple "basic" listeners that respond to the default Azure domain.
  dynamic "http_listener" {
    for_each = var.is_prod ? [] : [1] # Using dynamic block since count isn't available
    content {
      name                           = local.listener_name
      frontend_ip_configuration_name = local.frontend_ip_configuration_name
      frontend_port_name             = local.frontend_port_name
      protocol                       = "Http"
      host_name                      = azurerm_public_ip.app_gateway.fqdn
    }
  }
  dynamic "http_listener" {
    for_each = var.is_prod ? [] : [1] # Using dynamic block since count isn't available
    content {
      name                           = "${local.listener_name}-https"
      frontend_ip_configuration_name = local.frontend_ip_configuration_name
      frontend_port_name             = "${local.frontend_port_name}-443"
      protocol                       = "Https"
      ssl_certificate_name           = azurerm_key_vault_certificate.app_gateway_auto.name
      host_name                      = azurerm_public_ip.app_gateway.fqdn
    }
  }

  # For prod, create specific listeners to handle the custom domain (HTTP-only) and the default domain (HTTP->HTTPS).
  dynamic "http_listener" {
    # Prod listener for the production domain (e.g., *.ca.gov) on HTTP.
    for_each = var.is_prod ? [1] : [] # Using dynamic block since count isn't available
    content {
      name                           = "${local.listener_name}-prod-http"
      frontend_ip_configuration_name = local.frontend_ip_configuration_name
      frontend_port_name             = local.frontend_port_name
      protocol                       = "Http"
      host_name                      = var.hostname
    }
  }
  dynamic "http_listener" {
    # Prod listener for the default Azure domain on HTTP, used for redirection.
    for_each = var.is_prod ? [1] : [] # Using dynamic block since count isn't available
    content {
      name                           = "${local.listener_name}-default-http"
      frontend_ip_configuration_name = local.frontend_ip_configuration_name
      frontend_port_name             = local.frontend_port_name
      protocol                       = "Http"
      host_name                      = azurerm_public_ip.app_gateway.fqdn
    }
  }
  dynamic "http_listener" {
    # Prod listener for the default Azure domain on HTTPS, using the self-signed cert.
    for_each = var.is_prod ? [1] : [] # Using dynamic block since count isn't available
    content {
      name                           = "${local.listener_name}-default-https"
      frontend_ip_configuration_name = local.frontend_ip_configuration_name
      frontend_port_name             = "${local.frontend_port_name}-443"
      protocol                       = "Https"
      ssl_certificate_name           = azurerm_key_vault_certificate.app_gateway_auto.name
      host_name                      = azurerm_public_ip.app_gateway.fqdn
    }
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
    # needs a trailing slash
    path                                      = "/pgweb/"
    protocol                                  = "Http"
    interval                                  = 30
    timeout                                   = 15
    unhealthy_threshold                       = 3
    host                                      = var.backend_fqdns.pgweb
    match {
      status_code = ["200"]
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

  redirect_configuration {
    name                 = "http-to-https-redirect"
    redirect_type        = "Permanent"
    target_listener_name = var.is_prod ? "${local.listener_name}-default-https" : "${local.listener_name}-https"
    include_path         = true
    include_query_string = true
  }

  # Non-prod routing rules
  dynamic "request_routing_rule" {
    for_each = var.is_prod ? [] : [1] # Using dynamic block since count isn't available
    content {
      name                        = "${local.request_routing_rule_name}-redirect"
      rule_type                   = "Basic"
      http_listener_name          = local.listener_name
      redirect_configuration_name = "http-to-https-redirect"
      priority                    = 10
    }
  }
  dynamic "request_routing_rule" {
    for_each = var.is_prod ? [] : [1] # Using dynamic block since count isn't available
    content {
      name               = local.request_routing_rule_name
      rule_type          = "PathBasedRouting"
      http_listener_name = "${local.listener_name}-https"
      url_path_map_name  = "${local.request_routing_rule_name}-pathmap"
      priority           = 100
    }
  }

  # Production routing rules
  dynamic "request_routing_rule" {
    # Rule for the custom domain: serves content directly over HTTP (no redirect).
    for_each = var.is_prod ? [1] : [] # Using dynamic block since count isn't available
    content {
      name               = "${local.request_routing_rule_name}-prod-http"
      rule_type          = "PathBasedRouting"
      http_listener_name = "${local.listener_name}-prod-http"
      url_path_map_name  = "${local.request_routing_rule_name}-pathmap"
      priority           = 100
    }
  }
  dynamic "request_routing_rule" {
    # Rule for the default domain: redirects from HTTP to HTTPS.
    for_each = var.is_prod ? [1] : [] # Using dynamic block since count isn't available
    content {
      name                        = "${local.request_routing_rule_name}-default-redirect"
      rule_type                   = "Basic"
      http_listener_name          = "${local.listener_name}-default-http"
      redirect_configuration_name = "http-to-https-redirect"
      priority                    = 10
    }
  }
  dynamic "request_routing_rule" {
    # Rule for the default domain: serves content over HTTPS.
    for_each = var.is_prod ? [1] : [] # Using dynamic block since count isn't available
    content {
      name               = "${local.request_routing_rule_name}-default-https"
      rule_type          = "PathBasedRouting"
      http_listener_name = "${local.listener_name}-default-https"
      url_path_map_name  = "${local.request_routing_rule_name}-pathmap"
      priority           = 101
    }
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

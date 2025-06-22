# NAT Gateway routes private->public traffic from inside the VNet/subnets to the Internet

# This is the NAT Gateway resource itself.
resource "azurerm_nat_gateway" "main" {
  name                = var.nat_gateway_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_name            = "Standard"

  lifecycle {
    ignore_changes = [tags]
  }
}

# This resource creates the static public IP that the NAT Gateway will use for outbound traffic.
resource "azurerm_public_ip" "nat_gateway" {
  name                = "${var.public_ip_prefix}-nat-gateway"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"

  lifecycle {
    ignore_changes = [tags]
  }
}

# This resource associates the public IP with the NAT Gateway.
resource "azurerm_nat_gateway_public_ip_association" "main" {
  nat_gateway_id       = azurerm_nat_gateway.main.id
  public_ip_address_id = azurerm_public_ip.nat_gateway.id
}

# This single resource block associates the NAT Gateway with multiple subnets.
resource "azurerm_subnet_nat_gateway_association" "main" {
  # Use for_each to loop over a set of subnet keys.
  for_each = toset(["public", "worker"])

  # The subnet_id references the subnets,
  # looking them up by their key (e.g., "public", "worker").
  subnet_id      = azurerm_subnet.main[each.key].id
  nat_gateway_id = azurerm_nat_gateway.main.id
}

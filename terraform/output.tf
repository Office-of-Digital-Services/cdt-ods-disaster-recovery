output "outbound_ip_ranges" {
  value       = sort([for ip in azurerm_linux_web_app.main.possible_outbound_ip_address_list : "${ip}/32"])
  description = "The IP address ranges (in CIDR notation) to use to filter requests from this App Service instance."
}

# Input variables for the app_gateway module

variable "resource_group_name" {
  description = "The name of the resource group for deployment."
  type        = string
}

variable "location" {
  description = "The Azure region for deployment."
  type        = string
}

variable "is_prod" {
  description = "A flag to indicate if the deployment is for the production environment."
  type        = bool
}

variable "app_gateway_name" {
  description = "The name for the Application Gateway resource."
  type        = string
}

variable "public_ip_prefix" {
  description = "The prefix for the name for the public IP resource associated with the gateway."
  type        = string
}

variable "app_gateway_subnet_id" {
  description = "The ID of the application gateway subnet from the network module."
  type        = string
}

variable "hostname" {
  description = "The custom hostname for the HTTP listener."
  type        = string
}

variable "backend_fqdns" {
  description = "A map of Fully Qualified Domain Names for the backend pools (e.g., { web = '...', pgweb = '...' })."
  type        = map(string)
}

variable "key_vault_id" {
  description = "The ID of the Key Vault to use for generating the certificate."
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "The unique ID of the Log Analytics Workspace, needed for NSG diagnostic settings."
  type        = string
}

variable "diagnostic_setting_prefix" {
  description = "The standard name prefix for diagnostic settings."
  type        = string
}

variable "sku_name" {
  description = "The name of the SKU for the Application Gateway."
  type        = string
  default     = "WAF_v2"
}

variable "sku_tier" {
  description = "The tier of the SKU for the Application Gateway."
  type        = string
  default     = "WAF_v2"
}

variable "probe_path" {
  description = "The health probe path for the primary backend."
  type        = string
  default     = "/healthcheck"
}

# Input variables for the database module

variable "resource_group_name" {
  description = "The name of the resource group for deployment."
  type        = string
}

variable "location" {
  description = "The Azure region for deployment."
  type        = string
}

variable "env_letter" {
  description = "The single character for the environment (e.g., 'P', 'T') used in naming conventions."
  type        = string
}

variable "server_name" {
  description = "The name for the PostgreSQL flexible server."
  type        = string
}

variable "key_vault_id" {
  description = "The ID of the Key Vault for storing the admin password secret."
  type        = string
}

variable "db_subnet_id" {
  description = "The ID of the database subnet from the network module."
  type        = string
}

variable "virtual_network_id" {
  description = "The ID of the main VNet, required for linking the private DNS zone."
  type        = string
}

variable "private_endpoint_prefix" {
  description = "The name prefix for private endpoints."
  type = string
}

variable "private_service_connection_prefix" {
  description = "The name prefix for private service connections."
  type = string
}

variable "log_analytics_workspace_id" {
  description = "The unique ID of the Log Analytics Workspace, needed for NSG diagnostic settings."
  type       = string
}

variable "diagnostic_setting_prefix" {
    description = "The standard name prefix for diagnostic settings."
    type  = string
}

variable "administrator_login" {
  description = "The admin username for the server."
  type        = string
  default     = "postgres_admin"
}

variable "sku_name" {
  description = "The SKU for the server."
  type        = string
  default     = "B_Standard_B1ms"
}

variable "storage_mb" {
  description = "The max storage allowed for the server in megabytes."
  type        = number
  default     = 32 * 1024  # 32GB
}

variable "storage_tier" {
  description = "The storage tier for the server."
  type        = string
  default     = "P4"
}

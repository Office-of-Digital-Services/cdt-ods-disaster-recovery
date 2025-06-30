# Input variables for the email module

variable "resource_group_name" {
  description = "The name of the resource group for deployment."
  type        = string
}

variable "is_prod" {
  description = "A boolean flag to indicate if the deployment is for the production environment."
  type        = bool
  default     = false
}

variable "custom_domain_name" {
  description = "The name of the custom domain to use in the production environment."
  type        = string
  default     = null
}


variable "communication_service_name" {
  description = "The name for the Azure Communication Service and Email Communication Service resources."
  type        = string
}

variable "key_vault_id" {
  description = "The ID of the Key Vault where the service's secrets will be stored."
  type        = string
}

variable "data_location" {
  description = "The geographic location for the data (e.g., 'United States')."
  type        = string
  default     = "United States"
}

variable "log_analytics_workspace_id" {
  description = "The unique ID of the Log Analytics Workspace, needed for diagnostic settings."
  type        = string
}

variable "diagnostic_setting_prefix" {
  description = "The standard name prefix for diagnostic settings."
  type        = string
}

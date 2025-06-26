# Input variables for the storage module

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

variable "storage_account_name" {
  description = "The name for the storage account."
  type        = string
}

variable "storage_subnet_id" {
  description = "The ID of the storage subnet from the network module."
  type        = string
}

variable "private_endpoint_prefix" {
  description = "The name prefix for private endpoints."
  type        = string
}

variable "private_service_connection_prefix" {
  description = "The name prefix for private service connections."
  type        = string
}

variable "virtual_network_id" {
  description = "The ID of the main VNet, required for linking the private DNS zones."
  type        = string
}

variable "account_tier" {
  description = "The performance tier for the storage account."
  type        = string
  default     = "Standard"
}

variable "account_replication_type" {
  description = "The replication strategy for the storage account."
  type        = string
  default     = "RAGRS"
}

variable "share_configurations" {
  description = "A map defining the properties of the file shares to be created."
  type = map(object({
    quota_gb    = number
    access_tier = string
  }))
  default = {
    config = {
      quota_gb    = 1
      access_tier = "Cool"
    }
    requests = {
      quota_gb    = 5
      access_tier = "Hot"
    }
  }
}

variable "log_analytics_workspace_id" {
  description = "The unique ID of the Log Analytics Workspace, needed for diagnostic settings."
  type        = string
}

variable "diagnostic_setting_prefix" {
  description = "The standard name prefix for diagnostic settings."
  type        = string
}

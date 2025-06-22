# Input variables for the key_vault module

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

variable "key_vault_name" {
  description = "The name for the Key Vault resource."
  type        = string
}

variable "tenant_id" {
  description = "The Azure Active Directory tenant ID that the Key Vault is associated with."
  type        = string
}

variable "key_vault_subnet_id" {
  description = "The ID of the dedicated key_vault subnet from the network module."
  type        = string
}

variable "virtual_network_id" {
  description = "The ID of the main VNet, required for linking the private DNS zone."
  type        = string
}

variable "base_access_policy_object_ids" {
  description = "A map of names to Azure AD Object IDs for the initial policies (e.g., engineering, devsecops)."
  type        = map(string)
}

variable "private_endpoint_prefix" {
  description = "The name prefix for private endpoints."
  type = string
}

variable "private_service_connection_prefix" {
  description = "The name prefix for private service connections."
  type = string
}

variable "all_secret_permissions" {
  description = "The list of all secret permissions to grant for base policies."
  type        = list(string)
  default = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
  ]
}

variable "all_key_permissions" {
  description = "The list of all key permissions to grant for base policies."
  type        = list(string)
  default = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "GetRotationPolicy",
    "SetRotationPolicy",
    "Rotate",
  ]
}

variable "all_certificate_permissions" {
  description = "The list of all certificate permissions to grant for base policies."
  type        = list(string)
  default = []
}

variable "log_analytics_workspace_id" {
  description = "The unique ID of the Log Analytics Workspace, needed for NSG diagnostic settings."
  type       = string
}

variable "diagnostic_setting_prefix" {
    description = "The standard name prefix for diagnostic settings."
    type  = string
}

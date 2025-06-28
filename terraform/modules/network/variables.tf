# Input variables for the network module

variable "resource_group_name" {
  description = "The name of the resource group where the network resources will be created."
  type        = string
}

variable "location" {
  description = "The Azure region for the resources."
  type        = string
}

variable "env_letter" {
  description = "The single character for the environment (e.g., 'P', 'T') used in naming conventions."
  type        = string
}

variable "is_prod" {
  description = "A flag to indicate if the environment is production, used for conditional resources."
  type        = bool
  default     = false
}

variable "vnet_name" {
  description = "The name for the virtual network."
  type        = string
}

variable "nsg_prefix" {
  description = "The standard name prefix for the Network Security Group (NSG) resources."
  type        = string
}

variable "public_ip_prefix" {
  description = "The standard name prefix for the public IP resources."
  type        = string
}

variable "subnet_prefix" {
  description = "The standard name prefix for the subnet resources."
  type        = string
}

variable "nat_gateway_name" {
  description = "The name for the NAT gateway."
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

variable "vnet_address_space" {
  description = "The address space for the VNet."
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_addresses" {
  description = "A map of subnet names to their address prefixes."
  type        = map(list(string))
  default = {
    # a /22 subnet provides 1024 IP addresses
    # a /27 subnet provides 32 IP addresses
    public       = ["10.0.4.0/22"]   # 10.0.4.0 to 10.0.7.255
    worker       = ["10.0.8.0/22"]   # 10.0.8.0 to 10.0.11.255
    db           = ["10.0.12.0/27"]  # 10.0.12.0 to 10.0.12.31
    key_vault    = ["10.0.12.32/27"] # 10.0.12.32 to 10.0.12.63
    storage      = ["10.0.12.64/27"] # 10.0.12.64 to 10.0.12.95
    public_infra = ["10.0.12.96/27"]  # 10.0.12.96 to 10.0.12.127
    worker_infra = ["10.0.12.128/27"] # 10.0.12.128 to 10.0.12.159
  }
}

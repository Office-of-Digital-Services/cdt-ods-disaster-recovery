# Input variables for the application module

# General & Naming
variable "resource_group_name" {
  description = "The name of the resource group for deployment."
  type        = string
}

variable "location" {
  description = "The Azure region for deployment."
  type        = string
}

variable "env_name" {
  description = "The name of the environment (e.g., 'dev', 'prod') for naming conventions."
  type        = string
}

variable "env_letter" {
  description = "The single character for the environment (e.g., 'P', 'T') for naming conventions."
  type        = string
}

variable "is_prod" {
  description = "Whether the resources are being built in production or not."
  type        = bool
}

variable "virtual_network_id" {
  description = "The ID of the main VNet, required for linking the private DNS zone."
  type        = string
}

variable "container_app_environment_prefix" {
  description = "The standard prefix for Container App Environment names."
  type        = string
}

variable "container_app_prefix" {
  description = "The standard prefix for Container App names."
  type        = string
}

variable "key_vault_secret_uri_prefix" {
  description = "The base URI for Key Vault secrets (e.g., 'https://myvault.vault.azure.net/secrets')."
  type        = string
}

# Inputs from other modules
variable "key_vault_id" {
  description = "The ID of the Key Vault from the key_vault module."
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "The ID of the Log Analytics Workspace from the monitoring module."
  type        = string
}

variable "public_subnet_id" {
  description = "The ID of the public subnet from the network module."
  type        = string
}

variable "worker_subnet_id" {
  description = "The ID of the worker subnet from the network module."
  type        = string
}

variable "database_fqdn" {
  description = "The FQDN of the PostgreSQL server from the database module."
  type        = string
}

variable "postgres_admin_login" {
  description = "The admin username for the postgres database."
  type        = string
}

variable "postgres_admin_password_secret_name" {
  description = "The name of the Key Vault secret for the postgres admin password."
  type        = string
}

variable "email_connection_string_secret_name" {
  description = "The name of the Key Vault secret for the email service connection string."
  type        = string
}

variable "from_email_secret_name" {
  description = "The name of the Key Vault secret for the 'from email' address."
  type        = string
}

variable "storage_account_name" {
  description = "The name of the storage account from the storage module."
  type        = string
}

variable "storage_account_primary_access_key" {
  description = "The primary access key for the storage account."
  type        = string
  sensitive   = true
}

variable "storage_share_names" {
  description = "A map of file share names from the storage module."
  type        = map(string)
}

# Container Image Details
variable "container_registry" {
  type        = string
  description = "The name of the container registry."
  default     = "ghcr.io"
}

variable "container_repository" {
  type        = string
  description = "The repository path within the registry."
  default     = "office-of-digital-services/cdt-ods-disaster-recovery"
}

variable "container_tag" {
  description = "The specific tag of the image to deploy (e.g., 'main')."
  type        = string
}

variable "pgweb_image_tag" {
  description = "The image tag (from sosedoff/pgweb) to use for the pgweb app"
  type        = string
  default     = "0.16.2"
}

# Application Configuration
variable "web_app_cpu" {
  description = "Numeric amount of CPU to assign to web app containers (e.g. 0.5, 1)"
  type        = number
  default     = 0.5
}

variable "web_app_memory" {
  description = "String amount of memory to assign to web app containers (e.g. 1Gi, 2Gi). Should be at least double the CPU number."
  type        = string
  default     = "1Gi"
}

variable "web_app_config_secrets" {
  description = "A map of pre-existing Key Vault secret names that the web app needs to mount (e.g., { DajngoDbName = 'django-db-name' })."
  type        = map(string)
}

variable "worker_app_cpu" {
  description = "Numeric amount of CPU to assign to worker app containers (e.g. 0.5, 1)"
  type        = number
  default     = 0.5
}

variable "worker_app_memory" {
  description = "String amount of memory to assign to worker app containers (e.g. 1Gi, 2Gi). Should be at least double the CPU number."
  type        = string
  default     = "1Gi"
}

variable "worker_app_config_secrets" {
  description = "A map of pre-existing Key Vault secret names that the worker app needs to mount (e.g., { DajngoDbName = 'django-db-name' })."
  type        = map(string)
}

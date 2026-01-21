# Input variables for the monitoring module

variable "resource_group_name" {
  description = "The name of the resource group for deployment."
  type        = string
}

variable "location" {
  description = "The Azure region for deployment."
  type        = string
}

variable "log_analytics_workspace_name" {
  description = "The name for the Log Analytics Workspace."
  type        = string
}

variable "monitor_workspace_name" {
  description = "The name for the Azure Monitor Workspace."
  type        = string
}

variable "application_insights_name" {
  description = "The name for the Application Insights instance."
  type        = string
}

variable "action_group_name" {
  description = "The name for the monitor action group."
  type        = string
  default     = "ddrc-notify Slack channel email"
}

variable "action_group_short_name" {
  description = "The short name for the action group."
  type        = string
  default     = "slack-notify"
}

variable "notification_email_address" {
  description = "The email address for the action group's receiver."
  type        = string
}

variable "functions_app_hostname" {
  description = "The hostname of the Functions App, typically in the format <functionappname>.azurewebsites.net"
  type        = string
}

variable "functions_app_hostkey" {
  description = "The host key of the Functions App."
  type        = string
}

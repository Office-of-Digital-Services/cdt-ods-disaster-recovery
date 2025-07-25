# needs to be uppercase "because Azure DevOps will always transform pipeline variables to uppercase environment variables"
# https://gaunacode.com/terraform-input-variables-using-azure-devops

variable "ARM_SUBSCRIPTION_ID" {
  description = "Subscription ID for the Production subscription"
  type        = string
}

variable "DEVSECOPS_OBJECT_ID" {
  description = "Object ID for the DevSecOps principal, which includes the Production service connection"
  type        = string
}

variable "ENGINEERING_GROUP_OBJECT_ID" {
  description = "Object ID for the DDRC engineering Active Directory Group"
  type        = string
}

variable "SLACK_NOTIFY_EMAIL" {
  description = "Slack channel email for the DDRC engineering team"
  type        = string
}

variable "PIPELINE_ALLOWED_IPS" {
  description = "List of IP addresses to grant ACL access for running Terraform (locally or in the cloud)."
  type        = list(string)
  default     = []
}

variable "container_tag" {
  type        = string
  description = "The tag of the container image (e.g. 'main', '2025.04.08-rc1', '2025.05.4')"
  default     = "main"
}

locals {
  is_prod    = terraform.workspace == "default"
  is_test    = terraform.workspace == "test"
  is_dev     = !(local.is_prod || local.is_test)
  env_name   = local.is_prod ? "prod" : terraform.workspace
  env_letter = upper(substr(local.env_name, 0, 1))
  hostname   = local.is_prod ? "recovery.cdt.ca.gov" : "${local.env_name}.recovery.cdt.ca.gov"
}

terraform {
  // see version in azure-pipelines.yml

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {
    # needs to match azure-pipelines.yml
    resource_group_name  = "RG-CDT-PUB-VIP-DDRC-P-001"
    storage_account_name = "sacdtddrcp001"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}

provider "azurerm" {
  subscription_id = var.ARM_SUBSCRIPTION_ID
  features {}
}

data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "main" {
  name = "RG-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
}

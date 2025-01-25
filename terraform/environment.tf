locals {
  is_prod             = terraform.workspace == "default"
  is_test             = terraform.workspace == "test"
  is_dev              = !(local.is_prod || local.is_test)
  env_name            = local.is_prod ? "prod" : terraform.workspace
  env_letter          = upper(substr(local.env_name, 0, 1))
  subscription_letter = local.is_prod ? "P" : "D"
  hostname            = local.is_prod ? "disasterrecovery.ca.gov" : "${local.env_name}.disasterrecovery.ca.gov"
  secret_prefix       = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-DDRC-${local.env_letter}-001;SecretName="
}

data "azurerm_resource_group" "main" {
  name = "RG-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
}

locals {
  generated_secrets = {
    "django-db-password"          = { special = true, content_type = "password" }
    "django-secret-key"           = { special = true, content_type = "password" }
    "django-superuser-password"   = { special = true, content_type = "password" }
    "alert-to-slack-function-key" = { special = false, content_type = "query string key" }
  }

}

# Generate random passwords and keys for query strings to secure endpoints for Azure functions
resource "random_password" "main" {
  for_each = local.generated_secrets

  length      = 32
  min_lower   = 4
  min_upper   = 4
  min_numeric = 4
  min_special = each.value.special ? 4 : null # set minimum only when special = true
  special     = each.value.special
}

# Create the secret for Django DB password and query string using the generated secret
resource "azurerm_key_vault_secret" "main" {
  for_each = local.generated_secrets

  name         = each.key
  value        = random_password.main[each.key].result
  key_vault_id = var.key_vault_id
  content_type = each.value.content_type
}

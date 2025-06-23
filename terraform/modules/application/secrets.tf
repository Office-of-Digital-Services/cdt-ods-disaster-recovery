locals {
  generated_secrets = toset([
    "django-db-password",
    "django-secret-key",
    "django-superuser-password",
    "tasks-db-password"
  ])
}

# Generate random passwords
resource "random_password" "main" {
  for_each = local.generated_secrets

  length      = 32
  min_lower   = 4
  min_upper   = 4
  min_numeric = 4
  min_special = 4
  special     = true
}

# Create the secret for Django DB password using the generated secret
resource "azurerm_key_vault_secret" "main" {
  for_each = local.generated_secrets

  name         = each.key
  value        = random_password.main[each.key].result
  key_vault_id = var.key_vault_id
  content_type = "password"
}

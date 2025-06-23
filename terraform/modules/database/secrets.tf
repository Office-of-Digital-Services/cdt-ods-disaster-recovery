locals {
  postgres_admin_password_secret_name = "postgres-admin-password"
}

# Generate a random password for PostgreSQL
resource "random_password" "postgres_admin_password" {
  length           = 32
  min_lower        = 4
  min_upper        = 4
  min_numeric      = 4
  min_special      = 4
  special          = true
  override_special = "_%@!-"
}

# Create the secret for PostgreSQL Admin Password using the generated password
resource "azurerm_key_vault_secret" "postgres_admin_password" {
  name         = local.postgres_admin_password_secret_name
  value        = random_password.postgres_admin_password.result
  key_vault_id = var.key_vault_id
  content_type = "password"
  depends_on = [
    random_password.postgres_admin_password # Ensure password is generated first
  ]
}

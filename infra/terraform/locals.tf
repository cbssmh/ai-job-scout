locals {
  validation_identifier = "iac-test"

  common_tags = merge(var.common_tags, {
    ValidationBoundary = var.environment_name
  })

  acr_pull_role_name               = "AcrPull"
  key_vault_secrets_user_role_name = "Key Vault Secrets User"
  application_port                 = 8000
  application_insights_env_name    = "APPLICATIONINSIGHTS_CONNECTION_STRING"
  nvidia_api_key_env_name          = "NVIDIA_API_KEY"
  key_vault_secret_uri             = "${azurerm_key_vault.validation.vault_uri}secrets/${var.nvidia_secret_name}"
}

resource "azurerm_role_assignment" "environment_acr_pull" {
  scope                            = azurerm_container_registry.validation.id
  role_definition_name             = local.acr_pull_role_name
  principal_id                     = azurerm_container_app_environment.validation.identity[0].principal_id
  principal_type                   = "ServicePrincipal"
  skip_service_principal_aad_check = true
  description                      = "Validation Container Apps Environment identity can pull only from the validation ACR."
}

resource "azurerm_role_assignment" "app_key_vault_secrets_user" {
  count = var.deploy_container_app ? 1 : 0

  scope                            = azurerm_key_vault.validation.id
  role_definition_name             = local.key_vault_secrets_user_role_name
  principal_id                     = azurerm_container_app.validation[0].identity[0].principal_id
  principal_type                   = "ServicePrincipal"
  skip_service_principal_aad_check = true
  description                      = "Validation Container App identity can read secrets only from the validation Key Vault."
}

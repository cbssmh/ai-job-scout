output "validation_resource_group_name" {
  description = "Name of the isolated validation Resource Group."
  value       = azurerm_resource_group.validation.name
}

output "validation_resource_group_id" {
  description = "Resource ID of the isolated validation Resource Group."
  value       = azurerm_resource_group.validation.id
}

output "acr_name" {
  description = "Name of the validation ACR."
  value       = azurerm_container_registry.validation.name
}

output "acr_login_server" {
  description = "Login server into which the validated image must be copied outside Terraform."
  value       = azurerm_container_registry.validation.login_server
}

output "log_analytics_workspace_name" {
  description = "Name of the validation Log Analytics Workspace."
  value       = azurerm_log_analytics_workspace.validation.name
}

output "application_insights_name" {
  description = "Name of the validation Application Insights component."
  value       = azurerm_application_insights.validation.name
}

output "container_app_environment_name" {
  description = "Name of the validation Container Apps Environment."
  value       = azurerm_container_app_environment.validation.name
}

output "container_app_environment_principal_id" {
  description = "Principal ID of the environment system-assigned identity."
  value       = azurerm_container_app_environment.validation.identity[0].principal_id
}

output "container_app_name" {
  description = "Name of the validation Container App, or null during the foundation stage."
  value       = var.deploy_container_app ? azurerm_container_app.validation[0].name : null
}

output "container_app_fqdn" {
  description = "Public FQDN of the validation Container App, or null during the foundation stage."
  value       = var.deploy_container_app ? azurerm_container_app.validation[0].ingress[0].fqdn : null
}

output "container_app_url" {
  description = "Public HTTPS URL of the validation Container App, or null during the foundation stage."
  value       = var.deploy_container_app ? "https://${azurerm_container_app.validation[0].ingress[0].fqdn}" : null
}

output "container_app_principal_id" {
  description = "Principal ID of the app system-assigned identity, or null during the foundation stage."
  value       = var.deploy_container_app ? azurerm_container_app.validation[0].identity[0].principal_id : null
}

output "key_vault_name" {
  description = "Name of the validation Key Vault."
  value       = azurerm_key_vault.validation.name
}

output "acr_pull_role_assignment_id" {
  description = "ID of the validation ACR-scoped AcrPull assignment."
  value       = azurerm_role_assignment.environment_acr_pull.id
}

output "key_vault_role_assignment_id" {
  description = "ID of the validation Key Vault-scoped role assignment, or null during the foundation stage."
  value       = var.deploy_container_app ? azurerm_role_assignment.app_key_vault_secrets_user[0].id : null
}

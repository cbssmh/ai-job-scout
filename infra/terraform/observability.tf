resource "azurerm_log_analytics_workspace" "validation" {
  name                = var.log_analytics_workspace_name
  location            = azurerm_resource_group.validation.location
  resource_group_name = azurerm_resource_group.validation.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

resource "azurerm_application_insights" "validation" {
  name                = var.application_insights_name
  location            = azurerm_resource_group.validation.location
  resource_group_name = azurerm_resource_group.validation.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.validation.id
  tags                = local.common_tags
}

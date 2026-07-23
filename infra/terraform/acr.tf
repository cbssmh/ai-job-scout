resource "azurerm_container_registry" "validation" {
  name                                         = var.acr_name
  resource_group_name                          = azurerm_resource_group.validation.name
  location                                     = azurerm_resource_group.validation.location
  sku                                          = "Basic"
  admin_enabled                                = false
  public_network_access_enabled                = true
  azuread_authentication_as_arm_policy_enabled = true
  tags                                         = local.common_tags
}

resource "azurerm_key_vault" "validation" {
  name                          = var.key_vault_name
  location                      = azurerm_resource_group.validation.location
  resource_group_name           = azurerm_resource_group.validation.name
  tenant_id                     = data.azurerm_client_config.current.tenant_id
  sku_name                      = "standard"
  rbac_authorization_enabled    = true
  public_network_access_enabled = true
  soft_delete_retention_days    = 7
  purge_protection_enabled      = false
  tags                          = local.common_tags
}

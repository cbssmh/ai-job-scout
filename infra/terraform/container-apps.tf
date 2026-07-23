resource "azurerm_container_app_environment" "validation" {
  name                       = var.container_app_environment_name
  location                   = azurerm_resource_group.validation.location
  resource_group_name        = azurerm_resource_group.validation.name
  logs_destination           = "log-analytics"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.validation.id
  public_network_access      = "Enabled"
  tags                       = local.common_tags

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_container_app" "validation" {
  count = var.deploy_container_app ? 1 : 0

  name                         = var.container_app_name
  container_app_environment_id = azurerm_container_app_environment.validation.id
  resource_group_name          = azurerm_resource_group.validation.name
  revision_mode                = "Single"
  tags                         = local.common_tags

  identity {
    type = "SystemAssigned"
  }

  registry {
    server   = azurerm_container_registry.validation.login_server
    identity = "system-environment"
  }

  dynamic "secret" {
    for_each = var.enable_key_vault_secret_reference ? [var.nvidia_secret_name] : []

    content {
      name                = secret.value
      identity            = "System"
      key_vault_secret_id = local.key_vault_secret_uri
    }
  }

  template {
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    container {
      name   = var.container_app_name
      image  = var.container_image
      cpu    = var.container_cpu
      memory = var.container_memory

      env {
        name  = local.application_insights_env_name
        value = azurerm_application_insights.validation.connection_string
      }

      dynamic "env" {
        for_each = var.enable_key_vault_secret_reference ? [var.nvidia_secret_name] : []

        content {
          name        = local.nvidia_api_key_env_name
          secret_name = env.value
        }
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = local.application_port
    transport        = "http"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  # The private image cannot be pulled until the environment identity has AcrPull.
  depends_on = [azurerm_role_assignment.environment_acr_pull]
}

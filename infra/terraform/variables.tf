variable "subscription_id" {
  type        = string
  description = "Azure subscription ID in which to create the isolated validation environment."

  validation {
    condition     = can(regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", var.subscription_id))
    error_message = "subscription_id must be a valid UUID."
  }
}

variable "location" {
  type        = string
  description = "Azure region for every regional validation resource."
  default     = "japanwest"

  validation {
    condition     = lower(trimspace(var.location)) == "japanwest"
    error_message = "The incident-recovery validation region is japanwest."
  }
}

variable "environment_name" {
  type        = string
  description = "Human-readable validation boundary used in tags and safety checks."
  default     = "iac-test"

  validation {
    condition     = can(regex("(^|-)iac-test($|-)", lower(var.environment_name)))
    error_message = "environment_name must contain the iac-test validation identifier."
  }
}

variable "resource_group_name" {
  type        = string
  description = "Name of the temporary validation Resource Group."
  default     = "rg-ai-jobscout-iac-test-jw"

  validation {
    condition = (
      lower(var.resource_group_name) != "rg-ai-jobscout-dev" &&
      can(regex("iac-test", lower(var.resource_group_name)))
    )
    error_message = "resource_group_name must contain iac-test and must never be rg-ai-jobscout-dev."
  }
}

variable "acr_name" {
  type        = string
  description = "Globally unique validation ACR name. Change the default if it is unavailable."
  default     = "aijobscoutiactestjw2026"

  validation {
    condition = (
      can(regex("^[a-z0-9]{5,50}$", var.acr_name)) &&
      can(regex("iactest", var.acr_name))
    )
    error_message = "acr_name must be 5-50 lowercase alphanumeric characters and contain iactest."
  }
}

variable "log_analytics_workspace_name" {
  type        = string
  description = "Name of the validation Log Analytics Workspace."
  default     = "law-ai-jobscout-iac-test-jw"

  validation {
    condition     = can(regex("iac-test", lower(var.log_analytics_workspace_name)))
    error_message = "log_analytics_workspace_name must contain iac-test."
  }
}

variable "application_insights_name" {
  type        = string
  description = "Name of the workspace-based validation Application Insights component."
  default     = "appi-ai-jobscout-iac-test-jw"

  validation {
    condition     = can(regex("iac-test", lower(var.application_insights_name)))
    error_message = "application_insights_name must contain iac-test."
  }
}

variable "container_app_environment_name" {
  type        = string
  description = "Name of the validation Azure Container Apps Environment."
  default     = "cae-ai-jobscout-iac-test-jw"

  validation {
    condition     = can(regex("iac-test", lower(var.container_app_environment_name)))
    error_message = "container_app_environment_name must contain iac-test."
  }
}

variable "container_app_name" {
  type        = string
  description = "Name of the validation Azure Container App and its only container."
  default     = "ca-ai-jobscout-iac-test-jw"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{0,30}[a-z0-9]$", var.container_app_name)) && can(regex("iac-test", var.container_app_name))
    error_message = "container_app_name must use lowercase letters, numbers, and hyphens, contain iac-test, and be at most 32 characters."
  }
}

variable "key_vault_name" {
  type        = string
  description = "Globally unique validation Key Vault name. Change the default if it is unavailable."
  default     = "kv-jobscout-iac-test-jw"

  validation {
    condition = (
      can(regex("^[a-z][a-z0-9-]{1,22}[a-z0-9]$", var.key_vault_name)) &&
      can(regex("iac-test", var.key_vault_name)) &&
      !can(regex("--", var.key_vault_name))
    )
    error_message = "key_vault_name must be 3-24 lowercase alphanumeric or hyphen characters, contain iac-test, and avoid consecutive hyphens."
  }
}

variable "container_image" {
  type        = string
  description = "Full immutable destination image reference in the validation ACR, including @sha256 digest."
  default     = "aijobscoutiactestjw2026.azurecr.io/ai-job-scout@sha256:0cf8c993afe2c5d6eeeceb0786d5d406f85b7773ecf6365ba347fbee2302d14a"

  validation {
    condition = (
      startswith(var.container_image, "${var.acr_name}.azurecr.io/") &&
      endswith(var.container_image, "@${var.container_image_digest}")
    )
    error_message = "container_image must target acr_name and end with @container_image_digest."
  }
}

variable "container_image_digest" {
  type        = string
  description = "Expected immutable digest copied into the validation ACR outside Terraform."
  default     = "sha256:0cf8c993afe2c5d6eeeceb0786d5d406f85b7773ecf6365ba347fbee2302d14a"

  validation {
    condition     = can(regex("^sha256:[0-9a-f]{64}$", var.container_image_digest))
    error_message = "container_image_digest must be a lowercase sha256 digest."
  }
}

variable "container_cpu" {
  type        = number
  description = "vCPU allocated to the application container."
  default     = 0.5

  validation {
    condition     = var.container_cpu > 0 && var.container_cpu <= 2
    error_message = "container_cpu must be greater than 0 and at most 2 for this validation workload."
  }
}

variable "container_memory" {
  type        = string
  description = "Memory allocated to the application container."
  default     = "1Gi"

  validation {
    condition     = can(regex("^[0-9]+(\\.[0-9]+)?Gi$", var.container_memory))
    error_message = "container_memory must be expressed in Gi, for example 1Gi."
  }
}

variable "min_replicas" {
  type        = number
  description = "Minimum application replicas. Zero preserves scale-to-zero behavior."
  default     = 0

  validation {
    condition     = var.min_replicas >= 0 && floor(var.min_replicas) == var.min_replicas
    error_message = "min_replicas must be a non-negative integer."
  }
}

variable "max_replicas" {
  type        = number
  description = "Maximum application replicas."
  default     = 10

  validation {
    condition     = var.max_replicas >= var.min_replicas && floor(var.max_replicas) == var.max_replicas
    error_message = "max_replicas must be an integer greater than or equal to min_replicas."
  }
}

variable "common_tags" {
  type        = map(string)
  description = "Common tags applied to every validation resource."
  default = {
    Project     = "AIJobScout"
    Environment = "IaCValidation"
    ManagedBy   = "Terraform"
    Purpose     = "TerraformReproducibility"
    CostCenter  = "Personal"
  }

  validation {
    condition = (
      lookup(var.common_tags, "Project", "") == "AIJobScout" &&
      lookup(var.common_tags, "Environment", "") == "IaCValidation" &&
      lookup(var.common_tags, "ManagedBy", "") == "Terraform" &&
      lookup(var.common_tags, "Purpose", "") == "TerraformReproducibility" &&
      trimspace(lookup(var.common_tags, "CostCenter", "")) != ""
    )
    error_message = "common_tags must retain the AIJobScout IaC validation Project, Environment, ManagedBy, Purpose, and a non-empty CostCenter."
  }
}

variable "nvidia_secret_name" {
  type        = string
  description = "Name of the externally injected Key Vault secret and Container Apps secret reference."
  default     = "nvidia-api-key"

  validation {
    condition     = can(regex("^[a-zA-Z0-9-]{1,127}$", var.nvidia_secret_name))
    error_message = "nvidia_secret_name must follow Azure Key Vault secret naming rules."
  }
}

variable "deploy_container_app" {
  type        = bool
  description = "Staged-convergence switch. False creates the foundation before the external image copy. Final steady state is true."
  default     = true
}

variable "enable_key_vault_secret_reference" {
  type        = bool
  description = "Staged-convergence switch. False creates the app identity without a Key Vault reference. Final steady state is true."
  default     = true

  validation {
    condition     = !var.enable_key_vault_secret_reference || var.deploy_container_app
    error_message = "enable_key_vault_secret_reference requires deploy_container_app to be true."
  }
}

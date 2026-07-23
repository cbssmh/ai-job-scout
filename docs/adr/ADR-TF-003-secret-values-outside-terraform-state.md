# ADR-TF-003 — Secret Values Remain Outside Terraform State

## Status

Accepted.

## Context

The runtime contract needs a Key Vault-backed `NVIDIA_API_KEY` reference, but Terraform records managed resource arguments and computed configuration in state. Managing the provider credential through Terraform would create an unnecessary durable copy.

## Decision

Terraform manages the Key Vault, system identity, least-privilege role assignment, versionless secret URI metadata, Container Apps secret definition, and environment `secretRef`. An operator injects a dummy validation value outside Terraform after RBAC is effective. No secret value enters configuration, variables, data sources, outputs, plans, or state by design.

## Alternatives

- `azurerm_key_vault_secret`: rejected because the value would be persisted in state.
- Sensitive Terraform variable: rejected because `sensitive` masks display but does not remove the value from state.
- Plain Container Apps secret: rejected because it does not reproduce the verified Key Vault path.
- Omit secret infrastructure: rejected because it would not reproduce the security architecture.

## Reason

This preserves the runtime identity and reference architecture while preventing Terraform from becoming a secret-distribution channel.

## Consequences

- Provisioning requires a documented external data-plane step.
- Final convergence is staged around app identity and RBAC creation.
- The versionless URI supports externally managed secret rotation.
- Terraform cannot prove the credential's provider validity.

## Risks

- An operator could accidentally pass a secret through `.tfvars` or a Terraform environment variable.
- RBAC propagation can delay reference resolution.
- A missing external secret prevents final revision convergence.

## Validation

Static review must find no `azurerm_key_vault_secret`, secret-value variable, secret data source, or secret output. Gate 3 must inspect only secret names and references and must not retrieve or print the injected value.

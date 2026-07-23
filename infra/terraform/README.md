# AI Job Scout Terraform Validation Environment

## Purpose

This root module represents the minimum isolated Azure desired state designed to test the AI Job Scout v2.1 infrastructure reproducibility addendum. It is retained as an unreleased implementation artifact under Conditional Closeout; live runtime and reproducibility were not verified.

## Lifecycle Status

- Project status: **CONDITIONAL CLOSEOUT**
- Release status: **v2.1.0 NOT RELEASED**
- Terraform implementation and static validation: complete
- Full Terraform provisioning and validation runtime: not completed
- Destroy and clean re-apply reproducibility: not completed
- Protected v2.0.0 environment: preserved and never imported

Two pre-Gate-2.5 execution attempts were retained as incident evidence. The first failed at Container Apps Environment creation on the East Asia regional limit. The second failed at the same resource type in Japan West on the subscription-global limit. Final administrative cleanup destroyed the five remaining Terraform-managed Japan West foundation resources, emptied local state, and left only the expected soft-deleted validation-vault retention record.

## Scope

Terraform manages one temporary validation Resource Group containing a Basic Azure Container Registry, Log Analytics Workspace, workspace-based Application Insights, Container Apps Environment, Container App, Key Vault, two system-assigned identities, and two narrowly scoped RBAC assignments.

Terraform does not build or copy the application image, manage a secret value, create a budget, configure GitHub OIDC, or manage remote state.

## Protected Existing Environment

`rg-ai-jobscout-dev` is protected. It must not be imported, referenced as managed infrastructure, changed, replaced, or destroyed by this configuration. The existing dev ACR may be read only during the later external image-copy step. No validation identity may receive a role on a dev resource.

Every managed resource name and tag carries the `iac-test` validation boundary. Before any future apply or destroy, confirm that the state and plan contain no `rg-ai-jobscout-dev` address or ID.

## Validation Region

The existing v2.0.0 runtime remains in East Asia.

The second historical validation attempt used Japan West after its regional usage endpoint reported 0 of limit 1. Azure nevertheless rejected creation of the Container Apps Environment with `MaxNumberOfGlobalEnvironmentsInSubExceeded`. Under the frozen Azure for Students and isolation constraints, no compliant execution route remains.

This is a validation-environment constraint, not a production migration. Japan West may have different latency from East Asia.

## Architecture

```text
Local Terraform state
→ Temporary validation Resource Group
  → Validation ACR
  → Log Analytics → Application Insights
  → Container Apps Environment system identity
      → AcrPull at validation ACR scope
  → Key Vault with Azure RBAC
  → Container App system identity
      → Key Vault Secrets User at validation Key Vault scope
      → versionless Key Vault reference
      → NVIDIA_API_KEY secretRef
      → APPLICATIONINSIGHTS_CONNECTION_STRING
      → public HTTP ingress on port 8000
```

## Terraform-managed Resources

- Resource Group
- Basic ACR with admin credentials disabled
- Log Analytics Workspace with 30-day retention
- Workspace-based Application Insights
- Container Apps Environment with a system-assigned identity
- ACR-scoped `AcrPull` assignment
- Key Vault using Azure RBAC
- Container App with a system-assigned identity, public ingress, and scale-to-zero settings
- Key Vault-scoped `Key Vault Secrets User` assignment
- Key Vault secret URI metadata and Container Apps `secretRef` configuration

AzureRM 4.81 manages every resource. Its installed schema describes `registry.identity` as a system or user managed identity and its versioned implementation passes the value directly to the Container Apps API. Microsoft documents `system-environment` as the exact environment-level system identity token.

Automatic Azure resource-provider registration is disabled. Gate 2 planning therefore performs no subscription-level provider-registration writes; required providers must already be registered before Gate 3.

## External Inputs

- Azure credentials authorized to plan and later manage the validation resources and RBAC assignments
- The existing validated image copied into the validation ACR outside Terraform
- An externally injected dummy NVIDIA secret for infrastructure-path validation
- The Azure subscription, tenant, subscription policy, and permitted region

No external input may contain or mutate Terraform-managed dev infrastructure.

## State Strategy

State is local because the validation is temporary and single-user. No backend block or Terraform Cloud configuration exists. `.terraform/`, state files, plan files, and non-example `.tfvars` files are Git-ignored. `.terraform.lock.hcl` is intentionally committed when Gate 2 changes are later committed.

Local state is not suitable for collaboration, CI, concurrent execution, or disaster recovery. It can contain identity IDs, resource IDs, generated endpoints, and the Application Insights connection string embedded in Container App configuration. Restrict filesystem access and handle the state as sensitive operational data even though the NVIDIA secret value is excluded.

## Secret Strategy

> Terraform provisions the Key Vault, managed identities, RBAC, and secret-reference infrastructure, while secret values remain outside Terraform state.

No `azurerm_key_vault_secret`, sensitive secret variable, secret data source, secret output, CLI secret variable, or dummy value is declared. The configured URI is versionless so Container Apps can resolve a newer externally injected secret version.

The NVIDIA value must be injected only after the vault exists and the app identity has `Key Vault Secrets User`. Never paste the value into Terraform, a `.tfvars` file, a plan command, an environment variable consumed by Terraform, or an output.

## Identity Strategy

```text
Environment identity → AcrPull → validation ACR
App identity → Key Vault Secrets User → validation Key Vault
```

The registry uses `system-environment`; it has no username or password. The application uses its own `system` identity for the Key Vault reference. Both role assignments use the narrow target resource as scope. No Contributor, Owner, AcrPush, Resource Group-wide data role, or dev-resource role is declared.

## Image Strategy

The source artifact is the verified image:

```text
aijobscoutms2026.azurecr.io/ai-job-scout@sha256:0cf8c993afe2c5d6eeeceb0786d5d406f85b7773ecf6365ba347fbee2302d14a
```

Terraform creates an empty validation ACR. A later gate copies this exact digest into that ACR outside Terraform, verifies the destination digest, and supplies the full destination `container_image` reference. Terraform neither builds nor imports the image. The validation Container App must never reference the dev ACR.

## Historical Intended Apply Sequence

The implementation retains the intended staged convergence sequence for review. It was not completed and is not authorized for further execution under the Conditional Closeout decision.

1. Precheck dev `/health`, Azure context, names, state path, and plan.
2. Set `deploy_container_app = false` and `enable_key_vault_secret_reference = false`; apply the foundation, including ACR, observability, environment identity, `AcrPull`, and Key Vault.
3. Copy the validated image digest into the new ACR outside Terraform and verify digest equality.
4. Set `deploy_container_app = true` while keeping `enable_key_vault_secret_reference = false`; apply the secretless app, create its system identity, and assign `Key Vault Secrets User`.
5. After RBAC is effective, inject a dummy secret externally into the validation Key Vault. Do not retrieve or record its value.
6. Set `enable_key_vault_secret_reference = true`; apply the final steady-state Container App configuration.
7. Verify the revision, traffic, identity paths, telemetry, and public `/health` in Gate 3.

The final steady state has both switches set to `true`. A one-pass apply from an empty subscription boundary is not expected because the destination image registry and the app system identity do not exist until earlier stages complete. Gate 3 must prove that later no-change planning converges cleanly.

## Static Validation

From this directory:

```text
terraform fmt -recursive
terraform fmt -check -recursive
terraform init
terraform validate
terraform providers
terraform plan -out=tfplan
```

Review the plan and remove the uncommitted `tfplan`. Never run `apply` or `destroy` during Gate 2.

## Historical Gate 3 Preconditions

Gate 3 entry is permanently denied under the approved Conditional Closeout constraints. The following list is retained to document the intended readiness standard, not to authorize another attempt.

- Valid Azure CLI authentication and the intended subscription selected
- `Microsoft.App`, `Microsoft.Authorization`, `Microsoft.ContainerRegistry`, `Microsoft.Insights`, `Microsoft.KeyVault`, and `Microsoft.OperationalInsights` registered outside this configuration
- Permission to create the frozen resources and the two scoped role assignments
- Japan West still permitted by Azure Policy and Microsoft.App managed-environment quota still has capacity
- Resource Group nonexistence and global ACR/Key Vault name availability rechecked
- Isolated local state path confirmed empty and dev-free
- Destination image-copy command and immutable digest prepared but not run before the ACR exists
- External dummy-secret injection method prepared without exposing the value
- Staged variable values reviewed for each phase
- Dev `/health` passes before provisioning
- Final plan is re-reviewed for additions only and no dev reference

## Destroy Safety

Destroy only from this directory and only after confirming the state contains exclusively validation resources. Review a destroy plan before execution. The validation ACR and Key Vault role assignments must be scoped only to validation resources. The AzureRM Key Vault feature explicitly sets `purge_soft_delete_on_destroy = false`; Key Vault deletion must leave the soft-deleted vault and it must not be purged without explicit authorization.

After destroy, verify that validation resources are absent and that dev `/health` remains unchanged. Never use a broad resource-group variable, imported state, or a state file from the dev environment.

The final Conditional Closeout destroy plan contained 0 additions, 0 changes, and 5 destroys. Terraform removed the Japan West Resource Group, ACR, Log Analytics workspace, Application Insights component, and Key Vault. State became empty, no active validation resource or role assignment remained, the Key Vault stayed soft-deleted under its seven-day retention policy, and protected dev remained healthy and unchanged.

## Existing Dev Protection Checks

- `resource_group_name` rejects `rg-ai-jobscout-dev` and requires `iac-test`.
- Every configurable resource name requires the validation identifier (`iactest` for ACR).
- The Container App registry server is derived from the new validation ACR.
- Both role scopes are derived from validation resource IDs.
- No dev data source, import block, backend, or resource ID exists.
- `container_image` must target `acr_name` and the expected immutable digest.
- Plans must be searched for `rg-ai-jobscout-dev` before approval.

## Design Decisions

- Single root module; no modules or environment directory hierarchy
- Local state for one temporary single-user validation
- Terraform `>= 1.10.0, < 2.0.0`
- AzureRM `>= 4.81.0, < 5.0.0`
- AzureRM provider schema and Microsoft Container Apps API semantics verified for `system-environment`
- AzureRM automatic resource-provider registration disabled with `resource_provider_registrations = "none"`
- Deterministic user-supplied globally unique names; no random provider
- Japan West historical retry default after the East Asia regional quota incident, with enforced `iac-test` naming
- Key Vault purge-on-destroy explicitly disabled
- Common validation tags on all taggable resources
- No remote backend, Terraform Cloud, or CI apply
- No secret resource or secret value
- No dev import or mutation
- Staged convergence rather than a duplicate bootstrap Container App
- No `ignore_changes`; Gate 3 must evaluate any real provider normalization drift

## Known Risks

- RBAC and managed identity replication may not be immediately effective.
- Missing Azure resource-provider registrations will fail planning or apply and must be resolved outside Terraform.
- Container Apps API normalization may surface a plan difference that Gate 3 must investigate rather than suppress.
- The external image and secret steps prevent a single uninterrupted apply.
- Global names can become unavailable after planning.
- Key Vault soft delete prevents immediate name reuse; use a new disposable validation name after cleanup.
- Local state loss prevents safe managed destruction.
- The Application Insights connection string is computed metadata stored in state.
- A scale-from-zero health request can exceed a short timeout.
- Regional usage evidence does not prove subscription-global admission capacity.

## Portfolio Claim Limitation

> Implemented and statically validated Terraform for an isolated Azure Container Apps architecture while preserving the existing development environment. Partial foundation provisioning and controlled destruction were verified; validation runtime, no-change convergence, clean re-apply, and reproducibility were not verified. v2.1.0 was not released.

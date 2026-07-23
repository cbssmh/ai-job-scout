# Gate 3 Validation Log

Gate 3 was attempted twice under the original process and never completed. East Asia failed on the regional Container Apps Environment limit; Japan West failed on the subscription-global limit. No validation runtime, image copy, secret injection, telemetry verification, no-change result, or Gate 4 clean re-apply was produced. Conditional Closeout cleanup later destroyed the five remaining Japan West foundation resources and emptied Terraform state.

## TF-EVIDENCE-001

### Purpose

Confirm repository, account, policy, name, and protected-boundary preconditions.

### Verification Method

Inspected Git state, the active Azure account, subscription policy assignments, validation Resource Group existence, configured provider registration behavior, and global-name availability.

### Expected Result

Only Gate 2 files are changed; Azure for Students is active; East Asia is permitted; validation names are available; the validation Resource Group is absent; automatic provider registration is disabled.

### Observed Result

PASS. Branch was `main` at `6d07b6c`; only Gate 2 Terraform, ADR, and `.gitignore` changes were present. Subscription was Azure for Students (`d05a...1d10`). East Asia was in the allowed-locations policy. Both global names were available, the validation Resource Group was absent, and `resource_provider_registrations = "none"` remained configured.

### Evidence Reference

Gate 3 preflight command output in the Codex task.

## TF-EVIDENCE-002

### Purpose

Verify the protected dev runtime before provisioning.

### Verification Method

Called the protected Container App `/health` endpoint with bounded retries and counted resources in `rg-ai-jobscout-dev`.

### Expected Result

HTTP 200 with the verified health body and a stable resource baseline.

### Observed Result

PASS. HTTP 200 returned `{"status":"ok","service":"ai-job-scout-api"}`. Cold-start-aware elapsed time was 23.129 seconds. The dev Resource Group contained seven resources.

### Evidence Reference

Pre-apply health and Azure resource-count output in the Codex task.

## TF-EVIDENCE-003

### Purpose

Confirm an empty isolated Terraform state before first apply.

### Verification Method

Searched for state and plan files, then ran `terraform state list`.

### Expected Result

No state, plan, or managed objects.

### Observed Result

PASS. No state or plan file existed and Terraform reported that no state file was found.

### Evidence Reference

Preflight filesystem and Terraform state output in the Codex task.

## TF-EVIDENCE-004

### Purpose

Review the Stage A foundation plan.

### Verification Method

Ran a saved full Terraform plan with both staging switches disabled and inspected its JSON representation.

### Expected Result

Seven validation creates, no changes, no destroys, no Container App, no secret resource, and no protected-dev reference.

### Observed Result

PASS. Plan was 7 add, 0 change, 0 destroy. It contained only the Resource Group, ACR, Log Analytics, Application Insights, Container Apps Environment, environment ACR role, and Key Vault. Dev references and `azurerm_key_vault_secret` count were zero.

### Evidence Reference

`gate3-stage-a.tfplan` review output; the binary plan was subsequently removed.

## TF-EVIDENCE-005

### Purpose

Apply the reviewed Stage A foundation.

### Verification Method

Applied the saved Stage A plan without `-target`.

### Expected Result

All seven foundation resources created successfully.

### Observed Result

FAIL. The Resource Group, ACR, Log Analytics Workspace, Application Insights, and Key Vault were created. Container Apps Environment creation failed with `MaxNumberOfRegionalEnvironmentsInSubExceeded`: the subscription permits only one Container Apps Environment in East Asia. The environment ACR role could not be created because its principal did not exist.

### Evidence Reference

Terraform Stage A apply output and Gate 3 incident log.

## TF-EVIDENCE-006

### Purpose

Record exact partial state after the failed apply.

### Verification Method

Listed Terraform state and Azure resources in the validation Resource Group.

### Expected Result

An exact, recoverable inventory with no manual deletion.

### Observed Result

Terraform tracks the Resource Group, ACR, Log Analytics Workspace, Application Insights, Key Vault, and the read-only client-config data source. Azure shows four workload resources inside the validation Resource Group. No Container Apps Environment, role assignment, Container App, image copy, or secret exists.

### Evidence Reference

Post-failure Terraform state and Azure inventory output.

## TF-EVIDENCE-007

### Purpose

Determine the remaining declarative work after partial failure.

### Verification Method

Ran a fresh full Stage A plan and inspected the result.

### Expected Result

No changes or destruction of the successfully created foundation subset.

### Observed Result

PASS. Recovery plan showed 2 adds, 0 changes, and 0 destroys: the blocked Container Apps Environment and its validation-ACR-scoped `AcrPull` assignment. Protected-dev reference count was zero.

### Evidence Reference

`gate3-recovery.tfplan` review output; the binary plan was subsequently removed.

## TF-EVIDENCE-008

### Purpose

Confirm protected-dev preservation after the partial failure.

### Verification Method

Repeated the dev `/health` request, resource count, and Container Apps Environment inventory.

### Expected Result

Dev remains healthy and unchanged.

### Observed Result

PASS. Dev returned HTTP 200 with the verified body in 22.152 seconds, still contained seven resources, and its existing East Asia Container Apps Environment remained Succeeded. No dev object appears in Terraform state or the recovery plan.

### Evidence Reference

Post-failure dev-health, resource-count, environment-inventory, state, and plan outputs.

## TF-EVIDENCE-009

### Purpose

Protect local state after partial provisioning.

### Verification Method

Verified Git ignore rules, inspected file permissions, restricted the state file, and removed binary plans.

### Expected Result

State remains local and ignored, has owner-only permissions, and plan artifacts are absent.

### Observed Result

PASS. `terraform.tfstate` and `terraform.tfvars` are Git-ignored. State permissions were changed from 0644 to 0600. Both Gate 3 binary plans were removed. No actual NVIDIA value exists in configuration or state.

### Evidence Reference

Filesystem, `git check-ignore`, permission, and plan-removal output.

## TF-EVIDENCE-010

### Purpose

Record downstream Gate 3 execution status.

### Verification Method

Applied the failure-and-containment stop rule after Stage A.

### Expected Result

No additional mutation after a material partial-apply failure.

### Observed Result

PASS for containment. Image copy, digest verification, Stage B, secretless health, dummy-secret injection, Stage C, validation runtime, telemetry, and post-apply no-change verification were not run.

### Evidence Reference

Gate 3 task command history and incident record.

## TF-EVIDENCE-011

### Purpose

Recover the partial Stage A deployment through retained Terraform state.

### Verification Method

Compared state to Azure inventory, reviewed a saved destroy plan, applied that exact plan, and verified the active Resource Group and current state were empty.

### Expected Result

Validation-only cleanup with no dev reference, addition, change, replacement, or manual deletion.

### Observed Result

PASS for active-resource cleanup. Destroy plan was 0 add, 0 change, 5 destroy. Terraform removed the five state-managed validation resources, the validation Resource Group became absent, state became empty, and no validation role assignment remained.

### Evidence Reference

TF-RECOVERY-001 through TF-RECOVERY-004.

## TF-EVIDENCE-012

### Purpose

Verify protected-dev preservation through cleanup.

### Verification Method

Repeated health, resource count, environment state, and Activity Log checks.

### Expected Result

Dev remains healthy with no cleanup mutation.

### Observed Result

PASS. Dev remained HTTP 200 with the expected body, retained seven resources, its Container Apps Environment remained Succeeded, and no dev write or delete event appeared.

### Evidence Reference

TF-RECOVERY-002 and TF-RECOVERY-006.

## TF-EVIDENCE-013

### Purpose

Verify an eligible regional retry location.

### Verification Method

Intersected Azure Policy with provider-reported service locations and queried Microsoft.App regional usage for every alternative.

### Expected Result

At least one policy-permitted, service-supported region with one available managed-environment slot.

### Observed Result

PASS. Central India, UAE North, Malaysia West, and Japan West each reported managed-environment usage 0 of limit 1 and supported every required resource type. Japan West was selected based on proximity to Korea.

### Evidence Reference

TF-RECOVERY-007.

## TF-EVIDENCE-014

### Purpose

Review the replacement Stage A plan without applying it.

### Verification Method

Updated validation-only location and names, formatted and validated Terraform, then inspected the saved plan as JSON.

### Expected Result

Seven Japan West creates, no changes or destroys, no dev or old partial references, no secret resource, and hardened provider behavior.

### Observed Result

PASS. Plan was 7 add, 0 change, 0 destroy; location was consistently japanwest; dev, old-name, and secret-resource counts were zero; provider auto-registration was none; and Key Vault purge-on-destroy was false. The plan was not applied and was removed.

### Evidence Reference

TF-RECOVERY-008 and TF-RECOVERY-009.

## TF-EVIDENCE-015

### Purpose

Record the cleanup-side-effect incident.

### Verification Method

Queried Azure Activity Log after the deleted-vault inventory returned empty and inspected the pinned AzureRM 4.81 provider source.

### Expected Result

Soft-deleted validation vault retained without purge.

### Observed Result

FAIL. AzureRM issued a successful deleted-vault purge action because its implicit provider default was true. The empty validation vault was irreversibly purged. No secret or dev resource was involved. The provider configuration now explicitly disables future purge-on-destroy.

### Evidence Reference

TF-RECOVERY-005 and the Gate 3 incident log.

## TF-EVIDENCE-016

### Purpose

Recheck every Japan West retry precondition immediately before apply.

### Verification Method

Verified repository state, Azure account, empty dev-free Terraform state, owner-only state permissions, provider safeguards, Resource Group absence, regional usage, global-name availability, and protected-dev health.

### Expected Result

Japan West usage 0 of limit 1, validation names available, dev HTTP 200, and no existing validation infrastructure.

### Observed Result

PASS. The intended Azure for Students subscription was active. Current state was empty, provider auto-registration was none, Key Vault purge-on-destroy was false, the replacement Resource Group was absent, both names were available, Japan West regional usage was 0 of 1, and dev returned HTTP 200 with seven resources.

### Evidence Reference

Regional retry preflight command output in the Codex task.

## TF-EVIDENCE-017

### Purpose

Review the regenerated Japan West Stage A plan.

### Verification Method

Ran formatting, initialization, validation, a saved full plan, and machine-readable plan checks.

### Expected Result

Seven Japan West creates, zero changes and destroys, no dev or secret resource, and both provider safeguards intact.

### Observed Result

PASS. Plan was 7 add, 0 change, 0 destroy. Location was consistently Japan West, protected-dev and secret-resource counts were zero, provider auto-registration was none, and Key Vault purge-on-destroy was false.

### Evidence Reference

gate3-jw-stage-a.tfplan review output; the binary plan was subsequently removed.

## TF-EVIDENCE-018

### Purpose

Apply the reviewed Japan West foundation.

### Verification Method

Applied the exact saved Stage A plan without targeting.

### Expected Result

All seven frozen foundation resources provision successfully.

### Observed Result

FAIL. The Resource Group, ACR, Log Analytics Workspace, Application Insights, and Key Vault were created. Container Apps Environment creation returned HTTP 409 MaxNumberOfGlobalEnvironmentsInSubExceeded. The subscription cannot have more than one Container Apps Environment globally, and dev already owns that environment. The dependent ACR role was not created.

### Evidence Reference

Stage A apply output and incident log.

## TF-EVIDENCE-019

### Purpose

Contain the partial retry deployment safely.

### Verification Method

Stopped all later stages, retained state, inventoried Azure resources, generated a fresh full plan, removed binary plan files, and rechecked dev.

### Expected Result

Exact partial inventory, no cleanup or later-stage mutation, and preserved dev.

### Observed Result

PASS for containment. State tracks the five created validation resources plus the read-only data source. Azure inventory matches. The recovery plan is 2 add, 0 change, 0 destroy. No image, Container App, role, secret, telemetry request, or cleanup occurred. Dev remained HTTP 200 with seven resources.

### Evidence Reference

Regional retry containment output and runtime evidence.

## TF-EVIDENCE-020

### Purpose

Classify the quota discrepancy.

### Verification Method

Compared the regional Microsoft.App usage response with the Azure create error and subscription-wide Container Apps Environment inventory.

### Expected Result

Regional capacity accurately predicts subscription ability to create the isolated environment.

### Observed Result

FAIL. Japan West reported regional usage 0 of limit 1, but Azure separately enforced a global subscription limit of one environment. Subscription inventory contains only the protected East Asia dev environment. The regional usage endpoint did not expose or predict the global cap.

### Evidence Reference

Quota preflight, Stage A error, and subscription-wide environment inventory.

## TF-EVIDENCE-021

### Purpose

Record final Conditional Closeout cleanup and protected-dev preservation.

### Verification Method

Reviewed a saved Terraform destroy plan, applied that exact plan, reconciled empty state with Azure inventory, checked validation names and role scopes subscription-wide, and repeated protected-dev resource, revision, activity, and `/health` checks.

### Expected Result

Exactly five validation resources destroyed, empty Terraform state, no active validation orphan, and no protected-dev change.

### Observed Result

PASS. The destroy plan was 0 add, 0 change, 5 destroy. Terraform removed the Japan West Resource Group, ACR, Log Analytics workspace, Application Insights component, and Key Vault. `terraform state list` returned no addresses; both validation Resource Groups were absent; no active validation-tagged resource or validation-scoped role assignment remained. The validation Key Vault remained only as an expected seven-day soft-deleted record and was not purged. Protected dev retained seven resources and revision `ca-ai-jobscout-dev--0000012`, remained Healthy and Provisioned at 100% traffic, returned HTTP 200 with the expected body, and recorded no write or delete event during cleanup.

### Evidence Reference

Final Cleanup task Terraform apply output and post-destroy Azure verification.

# Gate 3 Incident Log

## Incident Record

| Field | Value |
| --- | --- |
| Incident | Gate 3 Stage A Container Apps Environment quota failure |
| Detected | 2026-07-22T13:38:09Z |
| Severity | Blocking validation deployment; no protected-dev impact |
| Status | Conditionally closed; validation resources cleaned up; no protected-dev impact |
| Qualifying policy | Apply blocked by a material subscription/design constraint |

## Trigger

The reviewed Stage A Terraform apply attempted to create `cae-ai-jobscout-iac-test` in East Asia. Azure returned HTTP 409 with `MaxNumberOfRegionalEnvironmentsInSubExceeded`, stating that the subscription cannot have more than one Container Apps Environment in East Asia.

Read-only inventory confirmed that the existing protected `cae-ai-jobscout-dev` environment is the current East Asia environment and is in Succeeded state.

## Impact

The following validation resources were created before the failure:

* `rg-ai-jobscout-iac-test`
* `aijobscoutiactest2026`
* `law-ai-jobscout-iac-test`
* `appi-ai-jobscout-iac-test`
* `kv-ai-jobscout-iac-test`

The following were not created:

* validation Container Apps Environment;
* environment system identity;
* validation ACR `AcrPull` assignment;
* Container App;
* app identity or Key Vault role;
* copied image;
* dummy secret;
* Key Vault-backed secret reference.

No secret was exposed. The protected dev environment remained healthy and retained its seven-resource baseline.

## Containment

Execution stopped immediately after the partial failure. Terraform state and Azure inventory were recorded. A fresh plan showed only two remaining creates and no changes or destroys. No manual resource deletion, Terraform destroy, image copy, secret injection, role broadening, architecture change, Stage B, Stage C, or Gate 4 action was performed.

Binary plan artifacts were removed and local state permissions were restricted to 0600.

## Root Cause

The Azure for Students subscription has a one-Container-Apps-Environment limit in East Asia. Gate 1 confirmed East Asia as an allowed region but did not establish sufficient regional Container Apps Environment quota for an isolated second environment.

## Recovery Disposition

The retained state was inspected and matched Azure inventory. A validation-only destroy plan containing 0 adds, 0 changes, and 5 destroys was applied successfully. The active validation Resource Group is absent, Terraform state is empty, validation role assignments are absent, and dev preservation passed.

Read-only policy, service-location, and quota checks verified Japan West for the regional retry. Microsoft.App reports managed-environment usage 0 of limit 1 there. New ACR and Key Vault names are currently available, and the replacement Stage A plan is 7 adds, 0 changes, and 0 destroys. It was not applied.

## Cleanup-side-effect Incident

During the reviewed cleanup, AzureRM deleted and automatically purged the empty validation Key Vault. Activity Log confirmed a successful Microsoft.KeyVault deleted-vault purge action.

The purge was not visible as a standalone destroy target. The pinned AzureRM 4.81 implementation defines key_vault.purge_soft_delete_on_destroy with a default of true; the prior empty features block therefore enabled purge implicitly.

Impact:

* validation-only empty vault irreversibly purged;
* no secret value existed, was retrieved, or was exposed;
* no dev resource was affected;
* the old global name was released rather than retained.

Corrective action:

* explicitly set key_vault.purge_soft_delete_on_destroy to false;
* verify the setting in replacement-plan JSON;
* continue using a new disposable Japan West Key Vault name.

## Remaining Resolution

No compliant Gate 3 execution route exists under the frozen project constraints. Gate 2.5 is final, the project entered Conditional Closeout, and v2.1.0 is not released. Runtime, telemetry, no-change convergence, and reproducibility remain explicitly unverified.

## Japan West Regional Retry Outcome

The retry preflight reconfirmed Japan West managed-environment usage 0 of limit 1, policy and service support, empty state, available names, provider safeguards, and healthy dev.

The reviewed Stage A plan contained 7 adds, 0 changes, and 0 destroys. During apply, Azure created the validation Resource Group, ACR, Log Analytics Workspace, Application Insights component, and Key Vault. Container Apps Environment creation then failed with MaxNumberOfGlobalEnvironmentsInSubExceeded.

## Global-quota Incident

The subscription permits only one Container Apps Environment globally, not merely one per region. The protected East Asia dev environment consumes that global allocation.

The Microsoft.App Japan West locations/usages endpoint reported regional ManagedEnvironmentCount usage 0 of limit 1. That endpoint did not expose the separate global cap, so the regional preflight produced a false-positive readiness result.

Containment:

* stopped immediately after Stage A failure;
* retained the local state and partial Japan West resources;
* ran a fresh full plan showing 2 adds, 0 changes, and 0 destroys;
* did not copy the image;
* did not create a Container App, role assignment, or secret;
* did not run Stages B or C;
* did not destroy or manually clean up;
* reconfirmed dev HTTP 200 and seven resources.

The frozen constraints prohibit changing the subscription boundary or reusing the protected dev environment. The global admission incident therefore closes as an accepted execution-context limitation rather than a completed runtime validation.

## Conditional Closeout Cleanup

The final saved Terraform destroy plan contained 0 additions, 0 changes, and 5 destroys. Terraform removed the Japan West Resource Group, ACR, Log Analytics workspace, Application Insights component, and Key Vault. State became empty, no active validation resource or role assignment remained, and the Key Vault retained its expected soft-deleted record rather than being purged.

Protected dev remained at seven resources with revision `ca-ai-jobscout-dev--0000012` Healthy, Provisioned, and serving 100% of traffic. `/health` returned HTTP 200 with the expected body, and no dev write or delete activity was recorded during cleanup.

## Current Incident States

* East Asia regional quota incident: Historical execution evidence; project conditionally closed.
* Global Container Apps Environment quota incident: Accepted execution-context constraint; Gate 3 not completed.
* Key Vault purge incident: Corrective control verified during final cleanup; the Japan West vault remained soft-deleted and was not purged.
* Active validation resources: None.
* Release: v2.1.0 not released.

# Gate 3 Incident Recovery Log

Recovery completed at 2026-07-22T14:07:11Z. The replacement regional plan was reviewed but not applied.

## TF-RECOVERY-001 — Retained State and Ownership

The retained local state had owner-only permissions and contained the validation Resource Group, ACR, Log Analytics Workspace, Application Insights component, Key Vault, and the read-only Azure client-config data source.

Protected-dev reference count was zero. Azure inventory matched the four workload resources inside rg-ai-jobscout-iac-test; the Resource Group itself was also state-managed. No unmanaged validation resource or failed environment artifact existed.

## TF-RECOVERY-002 — Protected Dev Before Cleanup

The protected app returned HTTP 200 with the expected health body in 20.507 seconds. The protected Resource Group contained seven resources.

## TF-RECOVERY-003 — Destroy Plan

    Resources to Add: 0
    Resources to Change: 0
    Resources to Destroy: 5
    Protected-dev References: 0
    Provider Auto-registration: none

Destroy targets were the validation Resource Group, ACR, Log Analytics Workspace, Application Insights component, and Key Vault. No role assignment, dev resource, addition, change, replacement, or provider unregister action was present.

## TF-RECOVERY-004 — Cleanup Apply

Terraform applied the reviewed plan successfully:

    Resources: 0 added, 0 changed, 5 destroyed

The active validation Resource Group is absent, current Terraform state is empty, no validation-scoped role assignment remains, and binary plan artifacts were removed.

## TF-RECOVERY-005 — Key Vault Cleanup Incident

Azure Activity Log showed that AzureRM 4.81 deleted and then purged kv-ai-jobscout-iac-test. The purge was not represented as a separate resource action in the reviewed plan. It occurred because the provider's features block default for key_vault.purge_soft_delete_on_destroy is true.

The vault was validation-only and contained no secret. No secret value was read or exposed. The purge was nevertheless contrary to the recovery instruction and is recorded as an incident.

Corrective configuration:

    features {
      key_vault {
        purge_soft_delete_on_destroy = false
      }
    }

The replacement plan JSON confirms this value is explicitly false.

## TF-RECOVERY-006 — Protected Dev After Cleanup

The protected app returned HTTP 200 with the expected body in 23.971 seconds. Its Resource Group still contained seven resources, its East Asia Container Apps Environment remained Succeeded, and Activity Log showed no dev write or delete event during cleanup.

## TF-RECOVERY-007 — Regional Candidate Analysis

Azure Policy permits East Asia, Central India, UAE North, Malaysia West, and Japan West. East Asia was excluded because Microsoft.App reports managed-environment usage 1 of limit 1.

All four alternatives support Microsoft.App managed environments, ACR, Key Vault, Log Analytics Workspaces, and Application Insights components.

| Region | Managed-environment Usage | Limit | Available | Result |
| --- | ---: | ---: | ---: | --- |
| Central India | 0 | 1 | 1 | Verified |
| UAE North | 0 | 1 | 1 | Verified |
| Malaysia West | 0 | 1 | 1 | Verified |
| Japan West | 0 | 1 | 1 | Verified; selected |

Japan West was selected as the closest verified alternative to Korea. This is a temporary validation-region constraint, not a production migration or claim of equivalent latency.

## TF-RECOVERY-008 — Disposable Names

The selected values are:

* rg-ai-jobscout-iac-test-jw
* aijobscoutiactestjw2026
* law-ai-jobscout-iac-test-jw
* appi-ai-jobscout-iac-test-jw
* cae-ai-jobscout-iac-test-jw
* ca-ai-jobscout-iac-test-jw
* kv-jobscout-iac-test-jw

Global ACR and Key Vault availability checks both returned available. These checks do not reserve the names.

## TF-RECOVERY-009 — Replacement Stage A Plan

Formatting and validation passed. The reviewed plan contained:

    Resources to Add: 7
    Resources to Change: 0
    Resources to Destroy: 0
    Location: japanwest
    Protected-dev References: 0
    Old Partial-resource References: 0
    Secret Resources: 0

The only planned role was AcrPull, derived from the new validation ACR scope. Provider auto-registration remained none, and Key Vault purge-on-destroy was explicitly false.

The replacement plan was not applied and its binary artifact was removed.

## TF-RECOVERY-010 — Regional Retry Reassessment

The approved Japan West retry was attempted after rechecking regional usage 0 of limit 1. Azure then returned MaxNumberOfGlobalEnvironmentsInSubExceeded during Container Apps Environment creation.

This establishes that the Azure for Students subscription has a separate global limit of one Container Apps Environment. The protected dev environment consumes that allocation. Regional Microsoft.App usage alone is insufficient readiness evidence for this subscription.

At the retry-containment point, the Japan West partial state was retained. A fresh plan showed only the blocked environment and its ACR-scoped role assignment as 2 additions, with no changes or destroys. No automatic cleanup was performed at that stage; TF-RECOVERY-011 records the later final cleanup.

Regional retry readiness was revoked. Gate 2.5 later established that no compliant execution route exists under the frozen project constraints.

## TF-RECOVERY-011 — Conditional Closeout Cleanup

After Conditional Closeout approval, the retained Japan West state was used for final administrative cleanup. The reviewed plan contained 0 additions, 0 changes, and 5 destroys with no protected-dev reference. Applying that plan destroyed the validation Resource Group, ACR, Log Analytics workspace, Application Insights component, and Key Vault.

Post-destroy verification found empty Terraform state, absent East Asia and Japan West validation Resource Groups, no active validation-tagged resources, and no validation-scoped role assignments. The Japan West Key Vault remained as an expected soft-deleted record scheduled for platform retention expiry; it was not purged.

Protected dev remained unchanged at seven resources. Revision `ca-ai-jobscout-dev--0000012` remained Healthy, Provisioned, and at 100% traffic; `/health` returned HTTP 200 with the expected body; and the cleanup window contained no dev write or delete activity.

The project lifecycle is **CONDITIONAL CLOSEOUT**. v2.1.0 is **NOT RELEASED**.

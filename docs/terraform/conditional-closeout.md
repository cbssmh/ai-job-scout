# AI Job Scout v2.1 — Conditional Closeout

## Final Lifecycle

| Field | Decision |
| --- | --- |
| Project status | **CONDITIONAL CLOSEOUT** |
| Release status | **v2.1.0 NOT RELEASED** |
| Terraform implementation | Retained |
| Static validation | Passed |
| Gate 3 | Attempted twice; not completed |
| Gate 4 | Not started |
| Gate 5 | Replaced by limited closeout |
| Protected v2.0.0 environment | Preserved and never imported |

## Closeout Reason

The frozen project required the protected development Container Apps Environment and a second, completely isolated validation environment to coexist. East Asia rejected the second environment under the regional limit. Japan West later rejected it with `MaxNumberOfGlobalEnvironmentsInSubExceeded`. Gate 2.5 established that no compliant execution context exists under the Azure for Students-only, no-alternate-subscription, no-paid-subscription, and strict-isolation constraints.

The engineering implementation remains technically valid, but the required live runtime and reproducibility evidence could not be produced. The execution environment failed to satisfy the frozen concurrency requirement; Terraform implementation and static validation did not fail.

## Final Cleanup

The saved final destroy plan contained:

```text
0 to add
0 to change
5 to destroy
```

Terraform destroyed:

* Japan West validation Resource Group
* Validation ACR
* Validation Log Analytics workspace
* Validation Application Insights component
* Validation Key Vault

Post-cleanup verification established:

* Terraform state contained no addresses before local runtime artifacts were removed.
* Both validation Resource Groups were absent.
* No active validation-tagged or validation-named Azure resource remained.
* No validation-scoped role assignment remained.
* The validation Key Vault remained only as an expected seven-day soft-deleted record and was not purged.
* Protected dev retained seven resources and revision `ca-ai-jobscout-dev--0000012`.
* The revision remained Healthy, Provisioned, and at 100% traffic.
* Protected dev `/health` returned HTTP 200 with the expected response.
* No protected-dev write or delete activity occurred during cleanup.

## Supported Claims

* Implemented and statically validated Terraform for an isolated Azure Container Apps architecture.
* Defined system-assigned identities, resource-scoped RBAC, Key Vault reference metadata, observability, and registry integration without managing secret values in Terraform.
* Preserved an existing healthy Azure environment outside Terraform state throughout planning, two failed execution attempts, and final cleanup.
* Partially provisioned and then safely destroyed five Terraform-managed validation foundation resources.
* Diagnosed distinct regional and subscription-global admission failures using control-plane and usage evidence.
* Reconciled Azure inventory with local Terraform state and completed an evidence-based Conditional Closeout.

## Unsupported Claims

The project must not claim that it:

* released v2.1.0;
* completed the Terraform-created architecture;
* created or verified a validation Container Apps Environment or Container App;
* verified validation runtime, `/health`, image digest, Managed Identity, RBAC, Key Vault delivery, or telemetry;
* achieved a no-change Terraform plan after complete provisioning;
* completed Gate 4 destroy and clean re-apply;
* demonstrated end-to-end Azure infrastructure reproducibility; or
* produced a production-ready Terraform release.

Existing evidence-backed v2.0.0 runtime claims remain separate and unaffected.

## Engineering Lessons Learned

* Static validity and a safe plan do not prove control-plane admission feasibility.
* Execution readiness must verify all critical limits at every applicable scope before provisioning.
* Regional capacity evidence must not be generalized to subscription-global capacity.
* A protected environment changes the required concurrent topology even when it remains outside project ownership.
* Critical unknowns require a blocking decision gate rather than an optimistic retry.
* Attempt failure, gate status, artifact completion, runtime proof, and reproducibility proof must remain separate evidence categories.
* Destructive cleanup must use reconciled ownership state and verify the protected boundary before and after execution.
* Release and career claims must be limited to the strongest completed evidence, not the intended final architecture.

## Final Release Decision

v2.1.0 is not released. The Terraform implementation remains in the repository as an unreleased, statically validated, conditionally closed engineering artifact.

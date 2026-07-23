# ADR-TF-001 — Separate IaC Validation Environment

## Status

Accepted as an implementation decision; execution conditionally closed after regional and subscription-global admission failures.

## Context

The operational v2.0.0 environment in `rg-ai-jobscout-dev` is complete and protected. Importing it would create replacement and destroy risk, while sharing its ACR at runtime would require a new validation identity role on a dev resource.

## Decision

Create every Terraform-managed resource and validation-scoped role assignment in a distinct temporary `iac-test` Resource Group. The validation runtime uses a new ACR and does not reference the dev ACR after the external image copy.

## Alternatives

- Import and manage dev resources: rejected because it violates the protection boundary.
- Reuse the dev ACR at runtime: rejected because it creates a dev dependency and requires a new dev-scoped role assignment.
- Deploy a sample image: rejected because the validated application image is available.

## Reason

A separate boundary makes plan and destroy review unambiguous and proves that Azure resources can be created without converting the working environment into a Terraform experiment.

## Consequences

- Validation creates a second short-lived set of billable resources.
- A validated image must be copied into the new ACR outside Terraform.
- Resource names and tags visibly identify the temporary environment.
- State and destroy operations remain isolated from dev.
- The existing v2.0.0 runtime remains in East Asia. A historical Japan West retry was attempted after the East Asia regional failure, but the subscription-global environment limit also blocked it.
- The regional retry was validation evidence, not a production migration or architecture change.

## Risks

- Incorrect variable values or state reuse could defeat the boundary.
- Globally unique names can collide.
- Azure Policy may restrict the chosen region.
- Alternative-region latency may differ from East Asia.

## Validation

Gate 2 plan review showed only new `iac-test` resources. Both historical Gate 3 attempts preserved dev but failed before runtime creation. Final Conditional Closeout cleanup destroyed the five Japan West foundation resources through isolated Terraform state, left no active validation orphan, and preserved dev health. The separate ownership boundary remains validated; full runtime and reproducibility do not.

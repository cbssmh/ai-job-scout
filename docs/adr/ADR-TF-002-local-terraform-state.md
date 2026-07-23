# ADR-TF-002 — Local Terraform State for a Single-user Temporary Validation Environment

## Status

Accepted for the temporary validation gates.

## Context

The work has one operator, a short lifetime, and no approved remote-state service, Terraform Cloud, or CI apply workflow. Introducing a backend would add services and permissions that are unnecessary for the North Star.

## Decision

Use Terraform's local state in `infra/terraform`. Ignore state, plan, `.terraform`, and real `.tfvars` artifacts; retain `.terraform.lock.hcl` in version control.

## Alternatives

- Azure Storage backend: deferred because multi-user or automated execution is not required.
- Terraform Cloud: explicitly excluded.
- No retained state: rejected because Terraform needs state to review, update, and safely destroy managed resources.

## Reason

Local state is the minimum mechanism that supports one temporary, single-user lifecycle without expanding the Azure scope.

## Consequences

- The operator is solely responsible for availability, integrity, permissions, and cleanup of the state.
- There is no remote locking or recovery.
- Losing state can prevent a safe Terraform destroy.
- The provider lock file remains reviewable and reproducible.

## Risks

- State contains resource IDs, identity IDs, endpoints, and computed Application Insights connection metadata.
- Concurrent or copied state can produce unsafe plans.
- Accidental deletion can orphan resources.

## Validation

Git inspection must confirm state and plans are ignored while `.terraform.lock.hcl` remains visible. Before Gate 3, confirm the state path is isolated and contains no dev resource.

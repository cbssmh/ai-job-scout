# ADR-TF-004 — Reuse of an Existing Validated AI Job Scout Image

## Status

Accepted as an implementation decision; external copy was not performed before Conditional Closeout.

## Context

The dev ACR holds a health-verified application image at immutable digest `sha256:0cf8c993afe2c5d6eeeceb0786d5d406f85b7773ecf6365ba347fbee2302d14a`. Rebuilding could drift because application dependencies and the base image tag are not fully pinned. Using the dev ACR directly would weaken isolation.

## Decision

Create a new validation ACR with Terraform, then copy the existing validated digest into it outside Terraform. Terraform consumes only the full destination reference with the same digest. It does not build, push, copy, or import image content.

## Alternatives

- Validation app pulls directly from dev ACR: rejected because it requires dev-scoped `AcrPull` and leaves a runtime dependency.
- Rebuild from source: deferred because the resulting artifact might differ and image-build reproducibility is outside scope.
- Use an unrelated public sample image: rejected because the validated application image is usable.

## Reason

Digest reuse preserves the proven application artifact while ensuring the validation runtime and its permissions are contained in the temporary environment.

## Consequences

- Terraform's first foundation stage creates an empty ACR.
- Image copy and digest comparison are required before Container App creation.
- The portfolio claim covers infrastructure, not artifact publication.
- The dev ACR remains a read-only source only.

## Risks

- The source digest could be deleted before copying.
- A destination name collision could require changing both ACR and image inputs.
- Copy failure or digest mismatch blocks app provisioning.

## Validation

Gate 2 verified that Terraform planned no image resource or registry credential. Gate 3 stopped before image copy, so destination digest equality and validation-runtime image use remain unverified.

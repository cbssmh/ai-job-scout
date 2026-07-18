# Phase 2 Secret Rotation and Rollback Runbook

**Secret:** `nvidia-api-key`

**Runtime variable:** `NVIDIA_API_KEY`

**Key Vault:** `kv-ai-jobscout-dev`

**Container App:** `ca-ai-jobscout-dev`

**Current test status:** Live rotation not tested

## 1. Purpose

Rotate the NVIDIA bearer credential without changing application code,
environment-variable names, Container Apps secret names, managed identity,
RBAC, image, ingress, scale, or the GitHub deployment workflow.

This runbook uses the existing versionless Key Vault reference. Microsoft
documents that Container Apps checks versionless references for newer versions
within approximately 30 minutes and automatically restarts active revisions
that consume the secret through environment variables. A secret-version change
does not require a new application revision. See [Manage secrets in Azure
Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/manage-secrets).

## 2. Rotation Eligibility Gate

Do not start unless all conditions are true:

- A distinct, valid replacement NVIDIA credential exists.
- The previous NVIDIA credential will remain valid through the validation and
  rollback window.
- An authorized operator can add Key Vault secret versions without displaying
  or recording values.
- Revision state, traffic, and `/health` are healthy before rotation.
- The Container Apps secret reference is versionless.
- An operator is available for the full propagation window and rollback.

Do not create a new version containing the identical value merely to satisfy a
test checklist. It does not prove value adoption and may cause an unnecessary
restart.

## 3. Pre-Rotation Evidence

Record only non-secret information:

| Evidence | Required observation |
| --- | --- |
| Active revision | Name, Active/Healthy/Provisioned state, replica count |
| Traffic | Active revision percentage and older revision percentage |
| Health | Timestamp, HTTP status, response contract |
| Secret reference | Key Vault reference, system identity, versionless URI |
| Environment mapping | `NVIDIA_API_KEY` → `secretRef: nvidia-api-key` |
| Key Vault metadata | Current version identifier, enabled state, creation time |
| RBAC | Runtime identity has `Key Vault Secrets User`; deployment identity does not |
| Rollback owner | Named operational owner and available rollback window |

Never record the credential, authorization headers, secret-value length,
partial value, hash, or encoded representation.

## 4. Rotation Procedure

### 4.1 Prepare the replacement

1. Issue or obtain a distinct replacement credential through the approved
   NVIDIA account process.
2. Keep the previous credential active.
3. Validate the replacement through an approved, controlled provider request
   outside the production Container App when possible.
4. Do not paste the credential into chat, source files, tickets, shell history,
   logs, screenshots, or documentation.

### 4.2 Add the Key Vault version

1. In Azure Portal, open `kv-ai-jobscout-dev`.
2. Open **Objects → Secrets → nvidia-api-key**.
3. Select **New Version**.
4. Use manual secret input and enter the distinct replacement credential.
5. Set the new version to enabled.
6. Leave the previous version enabled.
7. Do not change the secret name, Key Vault reference, RBAC, or Container App
   environment mapping.
8. Record the new version identifier and creation timestamp, never the value.

### 4.3 Observe propagation

1. Start a 30-minute propagation observation window.
2. Monitor the active revision and replica state.
3. Expect the active revision to restart its replicas when Container Apps
   adopts the newer version.
4. Do not expect or require a new revision name solely for a secret-version
   update.
5. Record restart/replica timestamps and any transient health state.
6. Do not revoke the previous provider credential during this window.

If automatic adoption cannot be established after the documented interval,
restart the existing active revision through the supported Container Apps
revision restart control. Do not create a different image revision merely to
force secret refresh.

## 5. Validation

Validate in this order:

1. The existing revision returns to Active, Healthy, and Provisioned.
2. The expected replica count is running.
3. Traffic remains 100% on the intended revision.
4. HTTPS `/health` returns HTTP 200 with the unchanged response.
5. A controlled NVIDIA-backed application operation succeeds.
6. Logs show no missing-key, Key Vault authorization, or provider
   authentication error.
7. No secret value appears in logs, Portal output, Cloud Shell output, or
   evidence records.
8. Image, command, args, resources, probes, scale, ingress, and registry remain
   unchanged.

Health alone is insufficient for rotation acceptance because `/health` does
not call NVIDIA.

## 6. Successful Rotation Completion

After all validation passes and the rollback window expires:

1. Revoke the previous credential at the NVIDIA provider.
2. Disable the old Key Vault version.
3. Retain the disabled version according to Key Vault retention policy; do not
   purge it as routine cleanup.
4. Record provider revocation time, old/new version identifiers, propagation
   duration, restart behavior, validation result, and operator.
5. Confirm the latest revision remains healthy and receives intended traffic.

## 7. Rollback Procedure

Rollback immediately if Key Vault resolution, revision health, or the
controlled NVIDIA-backed operation fails.

1. Confirm the previous provider credential is still valid.
2. Create a new version of `nvidia-api-key` containing the retained previous
   credential. This makes the rollback credential the newest version while
   preserving the versionless Container Apps reference.
3. Keep the failed replacement version for evidence but disable it after the
   rollback version is created.
4. Wait for automatic adoption within the documented interval, or restart the
   existing active revision if recovery urgency requires it.
5. Verify Active/Healthy/Provisioned state, replica count, traffic, `/health`,
   and a controlled NVIDIA-backed operation.
6. Revoke the failed replacement credential at the provider after rollback is
   confirmed.
7. Record the incident and exact non-secret version identifiers/timestamps.

Do not roll back by editing application code, renaming the secret, placing a
literal value in Container Apps, moving traffic to an unverified revision, or
weakening RBAC.

## 8. Failure Conditions and Escalation

| Condition | Response |
| --- | --- |
| New version cannot be created | Stop; leave runtime unchanged; verify operator data-plane role |
| Key Vault authorization error | Verify system identity and `Key Vault Secrets User`; do not grant broad Contributor/Owner |
| Revision restart does not occur | Wait through documented interval, then restart existing revision if authorized |
| `/health` fails | Begin rollback; preserve revision/platform evidence |
| `/health` passes but NVIDIA operation fails | Begin rollback; health does not validate provider credentials |
| Secret appears in output or logs | Treat as disclosure; rotate/revoke credentials and open a security incident |
| Previous credential was revoked early | Do not disable the replacement blindly; obtain a new valid credential and escalate |

## 9. Rotation Evidence Template

| Field | Record |
| --- | --- |
| Change window | |
| Operator | |
| Previous Key Vault version identifier | |
| Replacement Key Vault version identifier | |
| Provider credential changed | Yes/No |
| Versionless reference retained | Yes/No |
| Adoption start/end | |
| Revision name before/after | |
| Replica restart observed | Yes/No and timestamp |
| Health result | |
| Controlled NVIDIA operation result | |
| Traffic result | |
| Old provider credential revoked | Yes/No and timestamp |
| Old Key Vault version disabled | Yes/No and timestamp |
| Rollback required | Yes/No |
| Secret value recorded anywhere | Must be No |

## 10. Current Phase 2 Rotation Record

| Field | Result |
| --- | --- |
| Live rotation performed | No |
| Reason | No distinct valid replacement NVIDIA credential was available |
| Same-value version test | Rejected as non-meaningful and unnecessarily risky |
| Runtime secret path | Implemented and verified independently of rotation |
| Deferred action | Execute this runbook when a distinct valid replacement credential exists |
| Phase 2 impact | CONDITIONAL PASS |

# Phase 2 Runtime Evidence

**Project:** AI Job Scout: Cloud Operations Edition

**Evidence window:** 2026-07-18 through 2026-07-19 (Asia/Seoul)

**Result:** CONDITIONAL PASS

## 1. Evidence Handling

This record contains resource names, secret names, role names, revision names,
status, and configuration relationships. It contains no secret value.

Evidence references use these source types:

- **CLI:** value-filtered Azure CLI or local command output observed during the
  implementation session.
- **Portal:** operator-observed Azure Portal configuration and status.
- **Cloud Shell:** operator-observed targeted Azure Cloud Shell operation.
- **Repository:** checked-in configuration or an unchanged file.

## 2. Implementation Evidence

| ID | Purpose | Verification method | Observed result | Evidence reference |
| --- | --- | --- | --- | --- |
| E-01 | Establish the Phase 1 Azure baseline before security changes | Value-filtered `az containerapp show` | App was in East Asia; identity was `None`; registry identity was `system-environment`; image, ingress, command, args, and latest ready revision were recorded | CLI session output, 2026-07-18 |
| E-02 | Confirm local approved credential availability without disclosure | Name/presence-only parse of ignored `.env` | `NVIDIA_API_KEY` reported present; value was not printed | Local shell presence check, 2026-07-18 |
| E-03 | Confirm deployment identity has no long-lived credential | Query Entra application credential counts and federated credential metadata | `ai-job-scout-gha` had zero password and key credentials; issuer, audience, repository, and `main` ref restriction matched Phase 1 | CLI session output, 2026-07-18 |
| E-04 | Confirm deployment/image-pull separation | Query role assignments for GitHub service principal and environment identity | GitHub identity retained `AcrPush` and `Container Apps Contributor`; environment identity retained registry-scoped `AcrPull` | CLI session output, 2026-07-18 |
| E-05 | Provide Azure-native secret storage | Create and inspect Key Vault in the existing resource group | `kv-ai-jobscout-dev` created through Azure Portal using Azure RBAC and the approved application/environment boundary | Portal completion record supplied by operator |
| E-06 | Give the workload a credential-free runtime identity | Enable system identity and verify identity properties | System-assigned identity enabled; principal and tenant identifiers populated; provisioning succeeded | Portal completion record supplied by operator |
| E-07 | Grant minimum runtime secret read access | Inspect Key Vault access control | Container App system identity assigned `Key Vault Secrets User` at `kv-ai-jobscout-dev` scope | Portal completion record supplied by operator |
| E-08 | Store only the approved runtime secret | Inspect Key Vault secret list/metadata without opening the value | Enabled secret `nvidia-api-key` exists; no value was documented | Portal completion record supplied by operator |
| E-09 | Connect Container Apps to Key Vault without copying a value | Inspect Container Apps application secret metadata | `nvidia-api-key` is a Key Vault reference using the system-assigned identity; Container Apps displays no value | Portal completion record supplied by operator |
| E-10 | Inject the secret through the existing application contract | Apply the targeted environment-variable update and inspect the resulting template | Azure Cloud Shell mapped `NVIDIA_API_KEY` to `secretRef: nvidia-api-key`; no duplicate secret was created | Cloud Shell completion record supplied by operator |
| E-11 | Prove successful revision provisioning after injection | Inspect revision properties and replica count | `ca-ai-jobscout-dev--0000007` is Active, Healthy, Provisioned, with one replica | Portal runtime observation supplied by operator |
| E-12 | Prove Phase 1 runtime configuration was preserved | Compare new revision configuration with the recorded baseline | Image, resources, probes, scaling, ingress, command, args, registry configuration, and container settings were unchanged | Portal/Cloud Shell comparison supplied by operator |
| E-13 | Prove public runtime health remained unchanged | HTTPS request to `/health` | HTTP 200 with unchanged `status=ok`, `service=ai-job-scout-api` response | Operator HTTPS observation; independent implementation-session HTTPS check also returned HTTP 200 |
| E-14 | Prove traffic cutover completed | Inspect revision traffic configuration | Latest revision weight is 100%; revision `0000007` receives 100%; older revision `0000006` receives 0% | Portal traffic observation supplied by operator |
| E-15 | Preserve local development validation | Run test suite and Compose validation | 25 tests passed with one existing deprecation warning; `docker compose config --quiet` passed | Local command output, 2026-07-18 |
| E-16 | Confirm documentation contains no secret value | Search tracked/untracked documentation for secret-like assignments and inspect diffs | Only names, placeholders, references, and classifications are recorded | Final documentation validation |

## 3. Runtime State

| Property | Verified state |
| --- | --- |
| Container App | `ca-ai-jobscout-dev` |
| Active revision | `ca-ai-jobscout-dev--0000007` |
| Revision state | Active, Healthy, Provisioned |
| Replica count | 1 |
| Traffic | Revision `0000007`: 100%; older revision: 0% |
| Health | HTTPS `/health`: HTTP 200, unchanged response |
| Runtime identity | Container App system-assigned managed identity |
| Key Vault role | `Key Vault Secrets User` at Key Vault scope |
| Key Vault secret | `nvidia-api-key` (value not recorded) |
| Container Apps secret | Key Vault-backed `nvidia-api-key` using system identity |
| Environment mapping | `NVIDIA_API_KEY` → `secretRef: nvidia-api-key` |
| ACR pull identity | Existing Container Apps Environment `system-environment` |
| Deployment identity | Existing GitHub OIDC service principal |
| Application code changes | None |
| Workflow changes | None |

The full platform secret path is implemented and structurally verified:

```text
Key Vault current secret version
  -> Key Vault reference authorized by Container App system identity
  -> Container Apps application secret nvidia-api-key
  -> revision environment secretRef
  -> NVIDIA_API_KEY in the existing application configuration contract
```

The health endpoint proves startup, public reachability, and the unchanged
health contract. It does not itself call NVIDIA; a provider-backed functional
request was not added to the health contract because that would change runtime
behavior and product operations.

## 4. Security Validation

| Control | Verification | Result |
| --- | --- | --- |
| No secret in source | Git ignore, Docker ignore, repository diff review | PASS |
| No secret in documentation | Value-free evidence and final secret-pattern review | PASS |
| Managed identity used | Key Vault reference identifies system identity; revision provisions successfully | PASS |
| Key Vault actually used | Container Apps secret type is Key Vault reference and maps to runtime variable | PASS |
| Read-only runtime role | `Key Vault Secrets User` at dedicated vault scope | PASS |
| Deployment identity separated | GitHub identity has deployment/registry roles and no Key Vault data role | PASS |
| Image-pull identity separated | Environment identity remains ACR pull identity | PASS |
| No long-lived Azure deployment credential | Entra app credential counts are zero; OIDC trust retained | PASS |
| Local `.env` unnecessary in Azure | Docker build excludes `.env`; revision uses Azure secret reference | PASS |
| Secret absent from Container Apps display | Portal shows reference metadata, not value | PASS |
| Unauthorized identity boundary | Role review confirms no Key Vault role for deployment or environment identity; no intrusive negative secret-read test was performed | PASS by assignment review |

## 5. Incident Log

### INC-001 — Local Azure CLI write blocked by Conditional Access

| Field | Record |
| --- | --- |
| Issue | Local Azure CLI resource writes were rejected even though read operations initially succeeded. |
| Root cause | The local ARM access token contained password authentication only and lacked the tenant-required MFA claims context. |
| Impact | Key Vault, identity, RBAC, and runtime configuration could not be written through the local CLI. No partial resource change remained after the failed attempts. |
| Resolution | Used Azure Portal for supported resource configuration and Portal-authenticated Azure Cloud Shell for the targeted environment-variable update. No client secret or policy bypass was introduced. |
| Validation | Portal operations completed; revision `0000007` provisioned Active and Healthy; HTTPS health and traffic validation passed. |
| Lesson | Authentication success is not equivalent to authorization for Azure writes under Conditional Access. Capture token/control-plane behavior before diagnosing a platform resource failure. |

### INC-002 — Azure Portal environment-variable editor unavailable

| Field | Record |
| --- | --- |
| Issue | The current Portal showed a read-only Environment Variables page and the new-revision wizard exposed no Add control. |
| Root cause | The observed Portal UX did not match Microsoft's documented revision editor for this tenant/session; the exact rollout or regression cause was not established. |
| Impact | Direct Portal environment-variable mapping could not be completed safely without guessing navigation. |
| Resolution | Verified the current supported CLI operation from Microsoft documentation and installed CLI help, then used Portal Azure Cloud Shell with targeted `--set-env-vars` semantics. |
| Validation | New revision `0000007` contains `NVIDIA_API_KEY` with `secretRef: nvidia-api-key`; unrelated template properties remained unchanged. |
| Lesson | Treat Portal UI instructions as version-sensitive. When the control is absent, stop guessing and use a documented narrow control-plane operation. |

### INC-003 — Initial runtime health did not prove NVIDIA authentication

| Field | Record |
| --- | --- |
| Issue | Phase 1 `/health` succeeded while the container template initially had no `NVIDIA_API_KEY` environment mapping. |
| Root cause | `/health` is intentionally independent of the external LLM provider; application startup does not eagerly create the LLM client. |
| Impact | Healthy status alone could have been misinterpreted as evidence of external-provider authentication. |
| Resolution | Inspected application code and runtime configuration, then implemented the missing Key Vault-secret-to-environment mapping. |
| Validation | Revision template now contains the secret reference, and the new revision is provisioned, Active, Healthy, and serving traffic. |
| Lesson | Separate platform health, secret-injection evidence, and external dependency functional evidence. Do not infer one from another. |

### INC-004 — Redundant same-value rotation rejected

| Field | Record |
| --- | --- |
| Issue | A proposed rotation test would have created a new Key Vault version containing the identical credential. |
| Root cause | The checklist required rotation evidence, but no distinct valid replacement NVIDIA credential was available. |
| Impact | Same-value rollover could trigger a restart without producing evidence that a changed value was adopted. |
| Resolution | Rejected the redundant operation and deferred live rotation until a distinct replacement credential exists. |
| Validation | Architecture owner approved the decision; no extra secret version or restart was created. |
| Lesson | Operational tests must produce discriminating evidence. Do not mutate a healthy runtime solely to satisfy a checklist. |

## 6. Lessons Learned

- Application-scoped Container Apps secrets are not automatically available to
  a container; a revision-scoped environment `secretRef` is required.
- A successful health response proves the defined health contract, not external
  provider authentication.
- Managed identity, ACR pull, and GitHub deployment identities must remain
  separate even when one service hosts all three relationships.
- Azure Portal behavior can diverge from current documentation. Stop when the
  expected control is absent and verify a supported API/CLI path.
- `--set-env-vars` is the safe targeted CLI behavior because it preserves
  unrelated environment variables; `--replace-env-vars` is inappropriate here.
- A versionless Key Vault reference enables platform-managed adoption, but a
  meaningful live rotation test requires a distinct valid credential.
- Secret values are unnecessary for evidence. Names, references, identities,
  role assignments, revision state, and health results are sufficient.

## 7. Remaining Risks

| Risk | Current exposure | Treatment |
| --- | --- | --- |
| Live rotation untested | Propagation, restart timing, provider acceptance, and rollback were not exercised with a different credential | CONDITIONAL PASS; execute runbook when a distinct valid replacement is available |
| Provider-backed operation not part of health | `/health` can remain green while NVIDIA is unavailable or rejects the credential | Keep health contract unchanged; use a controlled functional validation during real rotation |
| Runtime bearer credential | A compromised container process may read the injected environment variable | Restrict exec/debug access, logs, role assignments, and provider quota; rotate on suspicion |
| Vault-scope read role | Runtime identity can read any secret added to the dedicated vault | Keep vault dedicated; review contents and RBAC before adding secrets |
| Single replica | Revision-level restart or failure can temporarily interrupt service | Accepted development-environment risk inherited from Phase 1 |
| Local CLI write limitation | Emergency changes from the local CLI remain subject to Conditional Access behavior | Use MFA-compliant Portal/Cloud Shell; never bypass policy or create a client secret |
| Portal UX drift | Future manual instructions can become stale | Prefer resource-state verification and documented CLI/API semantics |
| No post-security GitHub redeployment executed | Workflow/OIDC were preserved and reviewed, but the security step did not require a new image deployment | Validate naturally on the next approved `main` deployment; do not trigger a redundant deployment solely for evidence |
| Public unauthenticated API | Existing API remains publicly reachable | Out of Phase 2 scope; changing it would alter product/runtime behavior |
| SQLite persistence | Container-local database remains ephemeral | Existing Phase 1 risk; managed data redesign is out of scope |

## 8. Requirements Traceability Matrix

| Requirement | Implementation/evidence | Status |
| --- | --- | --- |
| Azure Key Vault in existing resource group | Dedicated `kv-ai-jobscout-dev`, Azure RBAC, approved tags/SKU posture | PASS |
| System-assigned managed identity | Enabled on `ca-ai-jobscout-dev`; principal populated | PASS |
| Minimum runtime RBAC | `Key Vault Secrets User` at dedicated vault scope | PASS |
| Approved secret only | `nvidia-api-key`; unused OpenAI credential not provisioned | PASS |
| No secret values committed or documented | Value-free migration and evidence | PASS |
| Preserve `NVIDIA_API_KEY` | Existing name mapped to `secretRef: nvidia-api-key` | PASS |
| Prefer Container Apps Key Vault reference | Implemented with system identity and versionless reference | PASS |
| No application SDK integration | No code/dependency change | PASS |
| GitHub OIDC has no client secret | Zero password/key credentials; federated trust retained | PASS |
| Repository and branch restriction | Exact GitHub repository and `main` ref subject retained | PASS |
| Deployment/runtime identity separation | GitHub, environment ACR pull, and app runtime identities remain distinct | PASS |
| Revision Active/Healthy | Revision `0000007` Active, Healthy, Provisioned | PASS |
| One replica running | Observed replica count 1 | PASS |
| HTTPS endpoint and `/health` unchanged | HTTP 200 and unchanged response | PASS |
| Secret available through runtime configuration | Key Vault reference and environment `secretRef` present | PASS |
| Local `.env` not required in Azure | Excluded from image; Azure mapping supplies runtime secret | PASS |
| Secrets not exposed in logs/docs/config display | No value observed or recorded | PASS |
| Authorized managed identity succeeds | Key Vault-backed revision provisions and runs with assigned identity | PASS |
| Unauthorized identities excluded | No Key Vault data role for GitHub or environment identities | PASS by RBAC review |
| GitHub Actions/OIDC preserved | Workflow and trust unchanged; Phase 1 deployment path retained | PASS |
| pytest passes | 25 passed; one existing warning | PASS |
| Docker Compose validates | `docker compose config --quiet` passed | PASS |
| Traffic verification | Revision `0000007` receives 100%; older revision 0% | PASS |
| Meaningful live secret rotation | No distinct valid replacement credential available; same-value mutation rejected | DEFERRED |
| Rotation and rollback documentation | Complete versionless-reference runbook added | PASS |
| Product/runtime behavior preserved | No code, API, UI, image, command, ingress, scaling, probes, or registry change | PASS |
| Phase 3 excluded | No Phase 3 work started | PASS |

## 9. Evidence Conclusion

Phase 2 has a **CONDITIONAL PASS**. Identity, RBAC, Key Vault integration,
runtime injection, revision health, traffic, local validation, deployment
separation, and documentation requirements are complete. Meaningful live
secret rotation remains deferred because no distinct valid replacement NVIDIA
credential was available.

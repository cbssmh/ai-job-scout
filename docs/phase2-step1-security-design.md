# Phase 2 — Step 1 Security Design

**Project:** AI Job Scout: Cloud Operations Edition

**Status:** Design complete; implementation not started

**Scope:** Security design only

**Baseline:** Phase 0 and Phase 1 remain PASS

> This file is the approved Step 1 design-time record. Phase 2 Step 2 has since
> been implemented and received a **CONDITIONAL PASS**. See the
> [implemented security architecture](phase2-security-architecture.md),
> [runtime evidence](phase2-runtime-evidence.md), and
> [completion summary and master review](phase2-completion-summary.md). Step 2
> used the documented dedicated-vault fallback: `Key Vault Secrets User` at
> vault scope, with the vault reserved for this application and environment.

## 1. Executive Summary

This design adds an Azure-native secret-management boundary without changing
the product, application contract, image startup behavior, database design, or
Phase 1 deployment flow.

The only application runtime secrets found in the repository configuration are
the external LLM provider credentials `NVIDIA_API_KEY` and
`OPENAI_API_KEY`. The selected provider's credential belongs in Azure Key
Vault. Provider selection, model names, endpoint URLs, Azure resource
identifiers, and public endpoint URLs are not secrets and must remain outside
Key Vault.

The Azure Container App will use its own system-assigned managed identity to
resolve a versionless Key Vault secret reference. Azure Container Apps will
continue to expose the resolved value to the existing environment-variable
name, so the application consumes the same configuration contract and needs no
code change. The existing Container Apps Environment identity remains the ACR
pull identity. The existing GitHub OIDC service principal remains the
deployment identity and receives no Key Vault data-plane access.

This produces three explicit trust boundaries:

1. GitHub OIDC identity: publish and deploy a traceable image.
2. Container Apps Environment identity: pull the image from ACR.
3. Container App system identity: read only the selected LLM secret from Key
   Vault.

All actions described for Azure, RBAC, secret migration, or Container Apps are
future work. **Implementation deferred to Step 2.**

### Evidence basis

The design is based on the checked-in configuration in `app/config.py`,
`.env.example`, `docker-compose.yml`, `.github/workflows/deploy.yml`,
`.github/workflows/test.yml`, `web/src/lib/api.ts`,
`frontend/dashboard.py`, `app/db/database.py`, the Phase 1 deployment records,
and a presence-only check of local ignored files. The local `.env` and
`jobs.db` exist, but their contents were not inspected. No secret value was
read or recorded.

Microsoft documents that Container Apps can resolve Key Vault references by
using a managed identity with the `Key Vault Secrets User` role. A versionless
reference is refreshed within 30 minutes after a new secret version is
available, and active revisions using it as an environment variable are
restarted automatically. See [Manage secrets in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/manage-secrets).

## 2. Secret Inventory

### 2.1 Inventory rules

- **Runtime Secret:** a confidential value required by executing application
  code.
- **Non-secret Configuration:** an application setting safe to expose but
  still subject to integrity control.
- **Deployment Metadata:** a non-secret identifier or endpoint used to select
  the Azure deployment target or establish workload identity.
- **Local-only Development Value:** configuration used by local, Compose,
  frontend-development, test, or utility-script workflows and not intended as
  Azure application configuration.
- “Required in Azure runtime” means required as an explicit or defaulted value
  for the current containerized API. “Conditional” means required only when
  the named provider or component is enabled.
- Placeholder values in `.env.example` are documentation, not credentials.
- The inventory includes environment variables, deployment selectors, and
  fixed operational/integration settings. Scoring weights, UI labels/default
  form inputs, test fixtures, and domain-policy constants are product behavior,
  not security configuration; the product freeze leaves them untouched.

### 2.2 Application runtime inventory

| Variable name | Purpose | Classification | Current location | Required in Azure runtime | Proposed target | Migration decision | Risk if exposed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `NVIDIA_API_KEY` | Authenticates calls to NVIDIA NIM | Runtime Secret | Local ignored `.env`; placeholder in `.env.example`; read by `app/config.py` | Yes for the current default `nvidia` provider | Key Vault secret `nvidia-api-key`, exposed to the container only through an ACA secret reference | Migrate the real Azure runtime value; do not migrate the placeholder. **Implementation deferred to Step 2.** | High: unauthorized API use, quota/cost consumption, revocation, and possible account abuse |
| `OPENAI_API_KEY` | Authenticates calls to OpenAI | Runtime Secret | Local ignored `.env`; placeholder in `.env.example`; read by `app/config.py`; a non-secret dummy is set in one test | Conditional: only when `LLM_PROVIDER=openai` | Key Vault secret `openai-api-key` only if OpenAI is enabled in that environment | Do not provision or grant access while unused; migrate before enabling OpenAI in Azure. **Implementation deferred to Step 2.** | High: unauthorized API use, quota/cost consumption, revocation, and possible account abuse |
| `LLM_PROVIDER` | Selects `nvidia` or `openai` | Non-secret Configuration | `.env.example`; default in `app/config.py`; local `.env` may override it | Yes, either explicitly or through the image default | Plain Container App environment variable | Keep outside Key Vault; preserve the current value during Step 2 | Low confidentiality risk; medium integrity/availability risk because a wrong value disables or redirects LLM selection |
| `NVIDIA_BASE_URL` | Selects the OpenAI-compatible NVIDIA endpoint | Non-secret Configuration | `.env.example`; default in `app/config.py`; utility-script default | Yes when NVIDIA is selected, either explicitly or by default | Plain Container App environment variable or immutable image default | Keep outside Key Vault; preserve current endpoint | Low confidentiality risk; medium integrity risk because tampering can redirect credential-bearing traffic |
| `NVIDIA_MODEL` | Selects the NVIDIA model | Non-secret Configuration | `.env.example`; default in `app/config.py`; utility-script default | Yes when NVIDIA is selected | Plain Container App environment variable or immutable image default | Keep outside Key Vault; preserve current model | Low confidentiality risk; medium availability/cost/quality risk if altered |
| `OPENAI_MODEL` | Selects the OpenAI model | Non-secret Configuration | `.env.example`; default in `app/config.py` | Conditional: when OpenAI is selected | Plain Container App environment variable or immutable image default | Keep outside Key Vault; preserve current model if OpenAI is enabled | Low confidentiality risk; medium availability/cost/quality risk if altered |
| Uvicorn host/port and image startup command | Starts the API on the current container interface and port | Non-secret Configuration | Exec-form Dockerfile `CMD`; Dockerfile port metadata | Yes | Continue as immutable image metadata with Azure command/args overrides absent | Preserve exactly; no migration | None as a secret; high availability risk if altered |
| CORS allowed origin | Permits the current local Next.js origin | Non-secret Configuration | Fixed middleware setting in `app/main.py` | Yes as current application behavior | Remain in application code for this phase | Preserve exactly; redesign is outside scope | None as a secret; high browser security risk if broadened |
| Logging level and format | Configures current application stdout logging | Non-secret Configuration | Fixed in `app/logging_config.py` | Yes | Remain in application code/image | Preserve exactly; never add secret-bearing fields | None as a secret; medium detection risk if weakened and high disclosure risk if secrets are later logged |

Only the credential for the enabled provider should be attached to a running
revision. Storing a possible future provider key is permissible, but exposing
both credentials to the same container would violate least privilege.

### 2.3 Deployment metadata inventory

| Variable name | Purpose | Classification | Current location | Required in Azure runtime | Proposed target | Migration decision | Risk if exposed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `AZURE_CLIENT_ID` | Identifies the Entra application used by GitHub OIDC | Deployment Metadata | GitHub Actions variable or secret; workflow environment | No | GitHub Actions repository variable | Keep outside Key Vault and prefer a variable over a secret because it is an identifier | Low confidentiality risk; medium phishing/misconfiguration value when combined with tenant and trust details |
| `AZURE_TENANT_ID` | Selects the Entra tenant for OIDC login | Deployment Metadata | GitHub Actions variable or secret; workflow and bootstrap metadata | No | GitHub Actions repository variable | Keep outside Key Vault | Low confidentiality risk; medium deployment-integrity risk if changed |
| `AZURE_SUBSCRIPTION_ID` | Selects the Azure subscription | Deployment Metadata | GitHub Actions variable or secret; workflow and bootstrap metadata | No | GitHub Actions repository variable | Keep outside Key Vault | Low confidentiality risk; high deployment-integrity risk if changed |
| `AZURE_RESOURCE_GROUP` / `RESOURCE_GROUP` | Selects the Phase 0 resource group | Deployment Metadata | Deploy workflow and OIDC bootstrap script | No | Version-controlled deployment metadata | Keep unchanged and outside Key Vault | Low confidentiality risk; high integrity risk because a change can retarget deployment |
| `ACR_NAME` | Identifies the Azure Container Registry | Deployment Metadata | Deploy workflow and OIDC bootstrap script | No | Version-controlled deployment metadata | Keep unchanged and outside Key Vault | Low confidentiality risk; medium deployment-integrity risk |
| `ACR_LOGIN_SERVER` | Registry host used to tag/push images | Deployment Metadata | Deploy workflow | No | Version-controlled deployment metadata | Keep unchanged and outside Key Vault | Low confidentiality risk; high supply-chain risk if tampered with |
| `IMAGE_REPOSITORY` | Selects the ACR repository | Deployment Metadata | Deploy workflow | No | Version-controlled deployment metadata | Keep unchanged and outside Key Vault | Low confidentiality risk; high provenance risk if tampered with |
| `CONTAINER_APP_NAME` | Identifies the deployment target | Deployment Metadata | Deploy workflow | No | Version-controlled deployment metadata | Keep unchanged and outside Key Vault | Low confidentiality risk; high deployment-integrity risk |
| `CONTAINER_NAME` | Identifies the container updated inside the app | Deployment Metadata | Deploy workflow | No | Version-controlled deployment metadata | Keep unchanged and outside Key Vault | Low confidentiality risk; high availability risk if wrong |
| `HEALTH_URL` | Public post-deployment health endpoint | Deployment Metadata | Deploy workflow | No | Version-controlled deployment metadata | Keep unchanged and outside Key Vault | None as a secret; medium validation-integrity risk if redirected |
| `GITHUB_SHA` | Supplies the immutable source revision/image tag | Deployment Metadata | GitHub-provided workflow context | No | Continue using GitHub-provided ephemeral metadata | No migration | None as a secret; high provenance risk if replaced by mutable metadata |
| `APP_DISPLAY_NAME` | Names the deployment Entra application | Deployment Metadata | OIDC bootstrap script | No | Version-controlled bootstrap metadata | Keep unchanged and outside Key Vault | Low confidentiality risk; medium identity-administration risk if changed |
| `FEDERATED_CREDENTIAL_NAME` | Names the Entra federated credential | Deployment Metadata | OIDC bootstrap script | No | Version-controlled bootstrap metadata | Keep unchanged and outside Key Vault | Low confidentiality risk; medium identity-administration risk if changed |
| `GITHUB_SUBJECT` | Restricts OIDC trust to the repository and `main` ref | Deployment Metadata | OIDC bootstrap script and Phase 1 documentation | No | Version-controlled trust metadata | Keep unchanged and outside Key Vault | Not secret; high security risk if broadened or altered incorrectly |

These identifiers do not become credentials when grouped together. The OIDC
trust policy, exact subject, GitHub token, and Azure RBAC assignment together
provide authentication and authorization. No client secret exists or is
required.

### 2.4 Local-only development and test inventory

| Variable/value name | Purpose | Classification | Current location | Required in Azure runtime | Proposed target | Migration decision | Risk if exposed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `.env` | Supplies developer-specific environment variables to Python and Compose | Local-only Development Value | Ignored local file; mounted into both Compose services | No as a file | Developer workstation secret store or ignored `.env` with restricted file permissions | Never copy the file to Azure, the image, source control, or CI artifacts | High if it contains real provider credentials |
| `.env.example` placeholders | Documents supported settings and permits secret-free Compose validation | Local-only Development Value | Tracked repository file | No | Remain as non-working placeholders | Keep; never replace placeholders with real credentials | High only if a real credential is accidentally committed |
| `NEXT_PUBLIC_API_BASE_URL` | Selects the API endpoint used by the optional Next.js client | Local-only Development Value | `web/src/lib/api.ts`, `web/README.md`, main README | No for the Phase 1 API-only Azure deployment | Frontend deployment/build configuration if that client is deployed later | No Phase 2 migration | Public by design; medium integrity risk because `NEXT_PUBLIC_*` values are browser-visible and can redirect requests |
| Streamlit `API_BASE_URL` | Sets the local dashboard API endpoint and user-editable default | Local-only Development Value | Hard-coded in `frontend/dashboard.py` | No for the Phase 1 API-only Azure deployment | Keep local | No migration | None as a secret; medium request-redirection risk in a shared dashboard |
| Compose service/container names and ports | Defines local API/dashboard networking and health checks | Local-only Development Value | `docker-compose.yml`, Dockerfile exposed ports | No | Keep in Compose/Docker metadata | No migration | None as a secret; low local integrity/availability risk |
| `DATABASE_PATH` / `DATABASE_URL` | Points SQLAlchemy to the repository-root SQLite file | Local-only Development Value | Derived constants in `app/db/database.py`; ignored `jobs.db` exists locally | Not supplied as Azure configuration; the current image derives the same path internally | Preserve current image behavior; managed database redesign is out of scope | No migration in this step or Phase 2 security implementation | Database contents may be sensitive; path/URL itself is not. Current ephemeral persistence remains a known Phase 1 risk |
| Test `OPENAI_API_KEY=test` | Prevents configuration-dependent test setup | Local-only Development Value | `tests/test_health_routes.py` process environment | No | Keep as a clearly non-production dummy | No migration | None, provided it remains a dummy and is never mistaken for a live key |
| Utility `BOARD_TOKENS` | Selects public Greenhouse boards for the local fetch script | Local-only Development Value | Constant in `scripts/fetch_greenhouse_jobs.py` | No | Keep in the utility script | No migration | None as a secret; low ingestion-integrity risk if changed |
| Greenhouse `BASE_URL`, title keywords, and request timeout | Selects the public board API and bounds/filters local ingestion | Local-only Development Value | Constants in `app/crawler/greenhouse.py` | No for the deployed API startup and health contract | Keep in the local ingestion utility path | No migration or redesign | None as a secret; medium ingestion integrity/availability risk if altered |

The SQLite database may contain job data and derived analysis, but its path is
not a secret. Data protection, persistence, backup, and managed-database design
are separate risks and are not silently expanded into this secret-management
step.

## 3. Security Architecture

### 3.1 Values in Key Vault

The Key Vault contains only live external-service credentials needed by the
Azure workload:

- `nvidia-api-key` when `LLM_PROVIDER=nvidia`.
- `openai-api-key` when `LLM_PROVIDER=openai`.

Secret names are stable; secret values are versioned. A disabled provider's
credential is not attached to the Container App. Secret content must never be
placed in source control, image layers, GitHub Actions variables, deployment
summaries, command output, or plain Container Apps configuration.

### 3.2 Values outside Key Vault

The following remain outside Key Vault:

- Provider selector, model names, and provider endpoint URL.
- Azure client, tenant, subscription, resource group, registry, app, container,
  and endpoint identifiers.
- OIDC subject and federated-credential metadata.
- Git commit SHA and image tags.
- Local endpoints, ports, database path, and example placeholders.

Key Vault is not a general configuration database. Hiding non-secret values
would add access dependencies, reduce transparency, and blur the difference
between confidentiality and integrity controls.

### 3.3 Runtime secret flow

1. The Container App has a system-assigned managed identity tied to its own
   lifecycle.
2. That identity has `Key Vault Secrets User` at only the active provider
   secret's scope.
3. Container Apps configuration contains a versionless Key Vault URI and the
   system identity reference; it does not contain the secret value.
4. The platform authenticates to Key Vault using managed identity and resolves
   the Container Apps secret.
5. The platform exposes the resolved value to the existing
   `NVIDIA_API_KEY` or `OPENAI_API_KEY` environment variable.
6. Existing application configuration reads the same variable. No Key Vault
   SDK, managed-identity library, code change, or API behavior change is needed.

The Key Vault URI is an identifier and is safe to store in Container Apps
configuration. The resolved value remains sensitive and is available to the
container process, so access to Container Apps exec/debug surfaces and process
diagnostics must remain tightly restricted.

### 3.4 Local development configuration strategy

- Continue using an ignored `.env` for developer-specific values because the
  current application already loads it and Compose already consumes it.
- Keep `.env.example` populated only with obvious non-working placeholders and
  non-secret defaults.
- Prefer a developer's OS credential manager or password manager as the source
  from which a short-lived local `.env` is populated.
- Never make local development depend on the Azure workload identity or the
  shared Azure Key Vault. This preserves local/cloud separation and avoids
  granting humans runtime identity privileges.
- Keep CI secret-free; current tests use fakes, monkeypatching, or dummy values
  and must not call live LLM services.

### 3.5 Azure runtime configuration strategy

- Plain environment variables carry only non-secret provider configuration.
- A Container Apps secret backed by a Key Vault reference carries exactly one
  active provider credential into the existing environment-variable name.
- Use a versionless Key Vault secret URI to permit controlled rotation without
  editing application configuration.
- Preserve the Dockerfile command, absence of Azure command/args overrides,
  ingress, health routes, image reference, and all application behavior.
- Preserve the existing environment-level ACR pull identity and registry
  configuration.

Azure documents that a versionless Key Vault reference is refreshed within 30
minutes and active revisions consuming it through environment variables are
restarted. Rotation must therefore be treated as a controlled operational
event and validated like a restart, even though it does not change application
behavior.

### 3.6 Deployment identity boundary

The GitHub OIDC service principal remains responsible for:

- authenticating through the existing exact-subject federated trust;
- pushing images to the existing ACR; and
- updating and reading the existing Container App/revisions for deployment
  verification.

It must not receive `Key Vault Secrets User`, `Key Vault Secrets Officer`, Key
Vault access-policy permissions, or permission to create role assignments. It
deploys a reference, not a secret value. Its workflow remains free of provider
credentials and cannot read them.

### 3.7 Runtime identity boundary

The Container App system identity is responsible only for reading the selected
provider secret. It does not push or pull images, deploy revisions, write
secrets, manage Key Vault, or access the Azure subscription generally.

The Container Apps Environment identity remains responsible only for ACR pull.
It receives no Key Vault access. Keeping these identities separate prevents a
compromised application process from inheriting the environment's registry
role through the new secret-management design.

### 3.8 Secret rotation approach

- Rotate by creating a new enabled version under the same Key Vault secret
  name; never edit a value in source control or GitHub.
- Keep the previous version enabled during a bounded validation window so a
  rollback remains possible.
- Expect Container Apps to retrieve the new version within 30 minutes and
  restart active revisions that consume it as an environment variable.
- Validate revision health, public `/health`, and one authorized LLM-backed
  operation without logging request credentials or response headers.
- Revoke the old provider credential only after the new version is verified;
  then disable the old Key Vault version according to the agreed rollback
  window.
- Perform immediate rotation after suspected disclosure and review access and
  platform logs.
- Record owner, issuance time, expiry if supplied by the provider, rotation
  reason, validation result, and retirement time as metadata, never as secret
  content.

Automated provider-side credential rotation is not designed because neither
provider lifecycle nor an authorized automation identity is present in the
current project. Manual controlled rotation is the minimum reproducible
starting point. Automation may be designed later if rotation frequency or
operational load justifies another identity and failure mode.

## 4. Managed Identity Decision

### ADR-style decision summary

**Context.** The Phase 1 Container App has no assigned identity. The Container
Apps Environment system identity already performs ACR pull. Phase 2 needs one
workload identity to resolve one active LLM credential for one Container App.
There is no multi-app secret consumer, pre-authorized blue/green resource, or
identity lifecycle requirement independent of the app.

**Alternatives.** A system-assigned managed identity tied to the Container App,
or a separately created user-assigned managed identity attached to the app.

**Decision.** Select a **system-assigned managed identity on the Container
App**.

**Technical reason.** It is the smallest identity surface for a single
resource: Azure creates and deletes it with the Container App, the Key Vault
reference can identify it as `system`, and no reusable identity resource or
client ID must be managed. Microsoft describes system-assigned identities as
suited to workloads contained within one resource and user-assigned identities
as suited to reuse or pre-authorization; see [Managed identities in Azure
Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity).

**Consequences.** The identity cannot be shared, and recreating the Container
App creates a new principal that must receive a new role assignment before its
Key Vault reference can resolve. Because a system identity does not exist
before the app resource exists, Step 2 must sequence identity enablement, RBAC
assignment, and secret-reference configuration. This is acceptable for an
existing app and is safer than introducing a reusable principal without a
reuse requirement. The existing environment identity and ACR pull path remain
unchanged.

## 5. RBAC Design

### 5.1 Access control matrix

| Principal | Resource | Required role | Scope | Responsibility |
| --- | --- | --- | --- | --- |
| Container App system-assigned identity | Active provider secret in the Phase 2 Key Vault | `Key Vault Secrets User` | Individual secret resource (`nvidia-api-key` or `openai-api-key`) | Resolve the active LLM credential at runtime; read only |
| Container Apps Environment managed identity (`system-environment`) | Existing ACR | `AcrPull` | Existing registry resource | Pull deployment images; existing Phase 1 assignment retained |
| GitHub OIDC deployment service principal | Existing ACR | `AcrPush` | Existing registry resource | Authenticate Docker and push SHA/main image tags; existing Phase 1 assignment retained |
| GitHub OIDC deployment service principal | Existing Container App | `Container Apps Contributor` | Prefer the individual Container App resource after Step 2 verification; current Phase 1 assignment is resource-group scoped | Update the existing app image and inspect revisions; no Key Vault data access |
| Designated security operator group | Phase 2 Key Vault secret data | `Key Vault Secrets Officer` | Dedicated Key Vault | Create new versions, disable old versions, and recover secret versions; cannot manage RBAC |
| Designated platform operator group | Phase 2 Key Vault control plane | `Key Vault Contributor` | Dedicated Key Vault | Configure vault settings without reading secret values or assigning roles |
| Designated access administrator | Key Vault role assignments | `Role Based Access Control Administrator` | Dedicated Key Vault; eligible/time-bound where governance supports it | Assign or remove the runtime and operator roles; does not require secret-value access |
| CI test identity | None | None | None | Run tests with fakes/dummies; no Azure or LLM credential access |
| Local developer identity | Developer-owned local credential only | None in Azure for normal development | Local workstation | Run local/Compose development without impersonating the Azure runtime |

`Key Vault Secrets User` is a read-only data-plane role with secret-value and
metadata read actions; it has no secret write or RBAC actions. See [Azure
built-in roles for Security](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/security#key-vault-secrets-user).

### 5.2 Least-privilege notes

- Secret-level scope is selected for the runtime identity because only one
  credential is active. Enabling another provider requires an explicit second
  assignment and configuration change.
- A dedicated app/environment vault limits blast radius. If Azure operational
  constraints make secret-level assignment impractical, vault scope is an
  acceptable documented fallback only while the vault contains credentials
  for this application and environment alone.
- The deployment identity must not be able to read or write provider secrets.
- Secret officers must not manage role assignments; access administrators need
  not read secret values.
- Broad roles such as `Owner`, subscription `Contributor`, or Key Vault
  `Administrator` are not required for steady-state deployment or runtime.
- Phase 1 currently grants `Container Apps Contributor` at resource-group
  scope. Narrowing it requires validation against every existing deployment
  operation before removal of the old assignment. **Implementation deferred to
  Step 2.**

## 6. Architecture Decision Records

### ADR-001 — Managed Identity

**Context.** The app needs credential-free authentication to Key Vault. One
existing Container App consumes the secret; the existing environment identity
already has the separate ACR-pull responsibility.

**Decision.** Add a system-assigned managed identity to the Container App and
use it only for Key Vault secret resolution.

**Alternatives.** Use a user-assigned managed identity; reuse the environment
identity; use a service principal/client secret; or place the provider key
directly in Container Apps.

**Reason.** A system identity matches the one-app lifecycle, minimizes resource
and credential administration, prevents identity sharing, and follows the
stated default. Reusing the environment identity would merge registry and
application trust boundaries. A client secret or direct secret value would
violate Secret Zero.

**Consequences.** App recreation changes the principal and requires RBAC
reassignment. Identity and RBAC must be established before the Key Vault
reference. No application code or SDK changes are required. The Phase 1 ACR
pull identity remains unchanged.

**Validation Method.** Confirm the app exposes exactly one system principal;
confirm the environment identity still owns ACR pull; confirm the app identity
has only the intended Key Vault data-plane assignment; confirm the container
starts and `/health` succeeds without a stored identity credential.

### ADR-002 — Azure Key Vault

**Context.** Live LLM API keys are currently represented by local environment
variables and placeholders. Azure requires a centrally controlled,
identity-authorized, versioned location that does not put values in source,
images, GitHub, or plain deployment configuration.

**Decision.** Use one dedicated Azure Key Vault for this application and Azure
environment, using Azure RBAC authorization. Store only active or approved LLM
provider credentials as versioned secrets. Keep non-secret configuration and
deployment metadata outside the vault.

**Alternatives.** Plain Container Apps secrets, GitHub Actions secrets copied
at deployment, local `.env` uploaded to Azure, or a third-party secret manager.

**Reason.** Key Vault supplies Azure-native RBAC, versioning, auditability,
recovery controls, and managed-identity integration. Direct Container Apps or
GitHub values would put the deployment identity in the secret path and make
rotation less isolated. Uploading `.env` would mix local and cloud concerns.

**Consequences.** Key Vault availability and authorization become runtime
configuration dependencies. Operators need separated control-plane,
data-plane, and RBAC responsibilities. Network restrictions, purge protection,
retention, and audit settings must be selected in Step 2 without changing the
app contract. Non-secret settings remain visible and reviewable.

**Validation Method.** Confirm the vault uses Azure RBAC; verify only approved
credential names exist; verify no values appear in repository, image history,
GitHub variables, workflow summaries, or plain Container Apps secrets; inspect
role assignments and secret access logs; test recovery and rotation in a
non-destructive manner.

### ADR-003 — Secret Injection Strategy

**Context.** The existing code reads provider credentials from environment
variables. Direct application access to Key Vault would require code and
dependency changes, while plain environment values would retain secret-copying
risk.

**Decision.** Configure a Container Apps secret backed by a versionless Key
Vault reference using the Container App system identity, then map that secret
to the existing provider environment-variable name.

**Alternatives.** Add Key Vault SDK retrieval to application code; inject a
literal Container Apps secret; copy the value from GitHub during deployment;
mount a generated `.env`; or pin the Key Vault reference to a secret version.

**Reason.** The platform reference removes secret values from deployment and
source while preserving the application's current configuration contract. A
versionless reference supports rotation through a new secret version. It is
the least intrusive design compatible with the product freeze.

**Consequences.** The secret exists in the container process environment after
platform resolution and must not be logged or exposed through debug/exec
access. Rotation can take up to the documented refresh interval and restarts
active revisions. A bad new version can therefore affect availability and
requires staged validation plus a rollback window.

**Validation Method.** Confirm Container Apps configuration contains a Key
Vault URI/identity reference rather than a value; confirm only the selected
credential environment variable is present; verify health and one controlled
LLM call; rotate to a new version and confirm automatic adoption within the
documented interval; verify no code, command, args, API, or deployment workflow
behavior changed.

## 7. Remaining Risks

| Risk | Exposure after this design | Treatment or acceptance |
| --- | --- | --- |
| Provider API key remains a bearer credential | A process compromise can read the injected environment variable and use the external API | Limit the app identity and exec/debug access, apply provider-side quota/restrictions where available, redact logs, and rotate after suspected disclosure |
| Environment-variable visibility | Platform resolution removes deployment copies but the running process still receives the value | Accept for minimal intrusion; application-side SDK retrieval would change code and is not justified in this step |
| Rotation restart | A new version is adopted within the platform refresh window and active revisions restart | Treat rotation as a controlled event; retain the prior version and validate health/business dependency before revocation |
| Bad secret version | An invalid key can preserve `/health` while breaking LLM-backed requests because the current health endpoint does not call the provider | Add a controlled post-rotation functional check without changing the health contract |
| RBAC propagation delay | A newly enabled system identity may not immediately resolve the vault reference | Sequence Step 2 changes and verify authorization before attaching the reference |
| System identity recreation | Deleting/recreating the Container App invalidates the principal and its role assignment | Treat recreation as a security bootstrap event; do not assume the old assignment survives |
| Key Vault network exposure | Public endpoint configuration may allow network reachability beyond the workload even though Entra/RBAC still controls access | Decide firewall/private-endpoint posture in Step 2 based on current Container Apps networking and subscription capability; do not break the validated runtime |
| Human secret administration | A secret officer can read or replace provider credentials | Use a group, MFA/Conditional Access, time-bound eligibility where available, audit logs, and separation from RBAC administration |
| Existing deployment role scope | `Container Apps Contributor` is currently at resource-group scope | Validate individual-resource scope and narrow only if all Phase 1 deployment operations still pass |
| Secret discovery in history or external systems | This design did not inspect Git history, GitHub settings, provider dashboards, or Azure runtime values | Perform value-safe scanning and administrative review in Step 2; rotate any credential with uncertain provenance |
| SQLite persistence and data protection | Azure container-local SQLite remains ephemeral and may contain data | Remains an explicit Phase 1 risk; managed data storage is outside this security-secret step |
| Public unauthenticated API | Existing ingress exposes API behavior without authentication | Existing product/Phase 1 risk; authentication would change product/runtime behavior and is outside this step |
| Minimum logging only | Phase 1 does not provide complete alerting or security monitoring | Define Key Vault/identity audit retention and alerts in a later observability step if not included in Step 2 acceptance criteria |

## 8. Step 2 Implementation Plan

Everything in this section is a future implementation activity.
**Implementation deferred to Step 2.** No command is supplied by this design.

1. Reconfirm the live Azure baseline and capture value-free evidence of current
   identities, registry authentication, app configuration names, and role
   scopes.
2. Perform a value-safe secret exposure review of tracked history, GitHub
   configuration names, Container Apps secret metadata, and operator records.
   Rotate rather than reveal any credential with uncertain provenance.
3. Establish the dedicated app/environment Key Vault with Azure RBAC,
   recovery/retention controls, and a network posture compatible with the
   validated Container Apps environment.
4. Establish separated operator and access-administrator assignments.
5. Add the selected provider credential as a new Key Vault secret version
   through an approved secure input path; do not print or persist it in work
   artifacts.
6. Enable the Container App system identity and record only its principal
   identifier.
7. Grant that principal `Key Vault Secrets User` at the active provider secret
   scope and wait for/verify RBAC propagation.
8. Configure the Container Apps Key Vault reference and map it to the existing
   environment-variable name while preserving all non-secret settings, image,
   command/args, ingress, scale, and health configuration.
9. Verify active/Healthy revision state, public health, and one controlled
   provider-backed operation; verify no secret value appears in configuration,
   logs, summaries, or command history.
10. Remove the superseded literal Azure runtime secret only after successful
    validation. Do not alter the developer `.env` model.
11. Exercise a new-version rotation and rollback window, then document the
    measured adoption time and evidence.
12. Validate whether the GitHub deployment role can be narrowed from the
    resource group to the individual Container App without changing the Phase
    1 workflow. Remove the broader assignment only after a successful
    equivalent deployment validation.
13. Record the final access matrix, secret metadata, rotation owner, evidence,
    and rollback procedure without recording values.

Step 2 must use a change window and an explicit rollback point because identity
assignment, RBAC propagation, and secret resolution are control-plane changes
to the existing working deployment. The GitHub workflow remains image-only;
Step 2 security bootstrap is an administrative operation, not a redesign of
the deployment flow.

## 9. Scope Compliance Review

| Validation requirement | Review result |
| --- | --- |
| No implementation proposed as completed | PASS — all Azure/RBAC/migration actions are explicitly deferred to Step 2 |
| No Azure resources created or modified | PASS — repository inspection and documentation only |
| No application code modified | PASS — only this design document is added |
| No GitHub Actions modified | PASS — workflow is treated as an existing boundary |
| No Container Apps modified | PASS — current identity, image, command/args, ingress, health, and registry facts are documented only |
| No secrets migrated | PASS — local `.env` contents were not opened and no value was copied |
| No Azure CLI implementation commands generated | PASS — the Step 2 plan is tool-neutral and command-free |
| No application behavior changes | PASS — the design preserves the existing environment-variable contract and provider behavior |
| No deployment flow changes | PASS — existing OIDC, test gate, image build/push, SHA deployment, revision wait, and health verification remain the Phase 1 flow |
| No runtime behavior changes in Step 1 | PASS — this step changes documentation only; future secret resolution preserves the app-facing variable contract |
| Phase 1 assumptions remain valid | PASS — existing ACR, environment ACR-pull identity, Container App, GitHub OIDC identity, image strategy, startup configuration, ingress, health validation, and East Asia deployment are retained |
| Product Freeze and Minimal Intrusion | PASS — no product, API, UI, AI logic, database, or scoring change is included |
| Least Privilege and Separation of Concerns | PASS — deployment, ACR pull, Key Vault read, secret administration, and RBAC administration are separate responsibilities |
| Secret Zero and Local/Cloud Separation | PASS — no deploy-time/runtime identity credential is stored; local `.env` is not uploaded or shared with Azure |

The future use of a new secret version can restart active revisions as part of
Azure Container Apps' documented refresh behavior. This is an operational
effect of Step 2, not an application behavior change, and Step 2 must validate
it explicitly.

## 10. Step 1 Completion Summary

Phase 2 Step 1 is complete at the design level.

- Secret inventory completed without reading or exposing values.
- Runtime secrets separated from non-secret configuration, deployment
  metadata, and local-only values.
- Azure Key Vault placement and exclusion decisions recorded.
- System-assigned Container App identity selected with technical rationale.
- Deployment, environment, runtime, operator, access-administrator, CI, and
  local-development boundaries documented.
- Minimum RBAC matrix defined.
- ADR-001, ADR-002, and ADR-003 completed with context, decision,
  alternatives, reason, consequences, and validation methods.
- Rotation, remaining risks, rollback concerns, and Step 2 sequencing recorded.
- Scope compliance verified: documentation is the only change.

**Final Step 1 decision:** proceed to a separately authorized Step 2 using a
dedicated Key Vault, a Container App system-assigned managed identity, a
versionless platform Key Vault reference, and secret-level read RBAC for only
the enabled provider. **Implementation deferred to Step 2.**

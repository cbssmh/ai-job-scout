# Phase 1 Runtime Evidence

## 1. Deployment Overview

Phase 1 of **AI Job Scout: Cloud Operations Edition** is complete. Phase 0 and
Tasks 1 through 5 are recorded as PASS. The operational work deployed the
existing application from the `main` branch of `cbssmh/ai-job-scout` to Azure
Container Apps without changing the product's business functionality.

The validated deployment is commit
`131a119f798cc281f47f64e8990b93fe27d4555c`. GitHub Actions authenticates to
Azure through OIDC, builds and pushes a commit-SHA-tagged image to
`aijobscoutms2026.azurecr.io`, and deploys it to `ca-ai-jobscout-dev` in the
`cae-ai-jobscout-dev` environment in East Asia. The latest revision,
`ca-ai-jobscout-dev--0000005`, is active and Healthy, receives 100% of traffic,
and has one replica. The public HTTPS health endpoint returns the expected
service status.

The GitHub OIDC deployment identity performs Azure login, ACR push, and
Container App deployment. A separate Container Apps Environment managed
identity (`system-environment`) performs ACR pull; the Container App itself has
no assigned identity. Log Analytics provides only the minimum platform logging
required by the Container Apps environment. It is not a completed observability,
monitoring, alerting, or telemetry platform. Azure resources were provisioned
manually in Phase 1; Terraform/Bicep infrastructure reproducibility is outside
the Phase 1 scope.

---

## 2. Runtime Evidence

| Evidence | Purpose | Verification Method | Observed Result | Evidence Reference |
| --- | --- | --- | --- | --- |
| GitHub Actions success | Confirm that the automatic deployment pipeline completed its required gates. | Review the deployment workflow run for commit `131a119f798cc281f47f64e8990b93fe27d4555c`. | PASS. OIDC authentication, test and Compose gates, image publication, Container Apps deployment, revision verification, and HTTPS health verification completed successfully. | To be attached |
| Docker image build | Confirm that the application was packaged as a deployable container image. | Review the Buildx step in the successful GitHub Actions run. | PASS. The workflow built the deployment image successfully. | To be attached |
| Docker image push | Confirm that the built image was published to the configured registry. | Review the image push output in the successful GitHub Actions run. | PASS. The image used by the running revision was pushed to `aijobscoutms2026.azurecr.io`. | To be attached |
| ACR repository | Confirm that the deployment artifact is stored in the intended repository. | Inspect the ACR repository list and the deployed image reference. | PASS. Repository `ai-job-scout` exists under `aijobscoutms2026.azurecr.io`. | To be attached |
| SHA image tag | Establish source-to-runtime traceability. | Compare the deployed image tag with the Git commit recorded by the workflow. | PASS. The deployment uses `aijobscoutms2026.azurecr.io/ai-job-scout:131a119f798cc281f47f64e8990b93fe27d4555c`. | To be attached |
| Azure Container Apps deployment | Confirm that Azure accepted and provisioned the deployment. | Inspect the Container App and its latest revision in Azure. | PASS. `ca-ai-jobscout-dev` is deployed in `cae-ai-jobscout-dev`, East Asia. | To be attached |
| Latest Revision | Identify the revision created by the validated deployment. | Query `properties.latestRevisionName` for the Container App. | PASS. The latest revision is `ca-ai-jobscout-dev--0000005`. | To be attached |
| Active Revision | Confirm that the revision is eligible to serve requests. | Query `properties.active` for revision `ca-ai-jobscout-dev--0000005`. | PASS. The revision is active. | To be attached |
| Traffic allocation | Confirm that application traffic is routed to the validated revision. | Inspect the Container App ingress traffic configuration. | PASS. Revision `ca-ai-jobscout-dev--0000005` receives 100% of application traffic. | To be attached |
| Replica count | Confirm that the validated revision has a provisioned replica. | Inspect the replica count for revision `ca-ai-jobscout-dev--0000005`. | PASS. The revision has one replica. | To be attached |
| Healthy Revision | Confirm that the Azure platform reports the revision as healthy. | Query `properties.healthState` for revision `ca-ai-jobscout-dev--0000005`. | PASS. `healthState` is `Healthy`. | To be attached |
| HTTPS endpoint | Confirm that the public application endpoint is reachable over TLS. | Send an HTTPS request to `https://ca-ai-jobscout-dev.kindbay-14c42b35.eastasia.azurecontainerapps.io/health`. | PASS. The endpoint is reachable over HTTPS and returns a successful response. | To be attached |
| Health endpoint | Confirm that the deployed API reports its expected service health. | Inspect the response body from `GET /health`. | PASS. Response: `{"status":"ok","service":"ai-job-scout-api"}`. | To be attached |
| Functional validation | Confirm the deployed service can process the Phase 1 runtime validation request. | Invoke the public health route and validate both HTTP success and the expected JSON payload. | PASS. The live deployment returned the expected API health payload. This validation is limited to the Phase 1 health contract. | To be attached |
| pytest | Confirm that the existing automated Python test suite passed before deployment. | Review the `pytest -q` gate in the successful deployment workflow. | PASS. 25 passed, 1 existing warning. | To be attached |
| docker compose config | Confirm that the existing Compose definition remained valid. | Run `docker compose config --quiet`. | PASS. `docker compose config --quiet` completed successfully. | To be attached |

---

## 3. Incident Log

**Incident 1 — Azure region policy rejection**

| Field | Detail |
| --- | --- |
| Issue | Azure for Students policy rejected deployment attempts targeting Korea Central and Korea South. |
| Impact | Azure resources could not be provisioned in either initially selected Korea region. |
| Root Cause | The subscription policy did not permit deployment in Korea Central or Korea South. |
| Resolution | The deployment region was changed to East Asia. |
| Verification | The Container Apps environment and application were successfully deployed in East Asia. |
| Lessons Learned | Region eligibility must be checked against the active subscription policy before resource creation. Subscription policy, not geographic preference, determines the usable deployment regions. |

**Incident 2 — Interactive Azure bootstrap blocked by MFA**

| Field | Detail |
| --- | --- |
| Issue | A Conditional Access MFA challenge blocked an Azure role-assignment write during the initial GitHub OIDC bootstrap attempt. |
| Impact | The Entra application, service principal, and federated credential existed, but deployment role assignment could not complete in that attempt. |
| Root Cause | The interactive Azure CLI session did not satisfy the tenant's Conditional Access MFA requirement for the write operation. |
| Resolution | The operation was stopped without weakening authentication or creating a client secret. MFA-compliant authorization was required before completing the remaining role assignments. |
| Verification | The final GitHub Actions deployment authenticated through OIDC and successfully pushed to ACR and deployed to Container Apps, demonstrating that the required access was subsequently available. |
| Lessons Learned | Azure bootstrap procedures must be idempotent and safe to rerun after Conditional Access interrupts a partially completed setup. Interactive administrative access and workload OIDC authentication have different operational requirements. |

**Incident 3 — Azure Container Apps startup override passed malformed arguments**

| Field | Detail |
| --- | --- |
| Issue | The Azure Container Apps command and args override passed malformed Uvicorn arguments to the deployed container. |
| Impact | The created revision could not activate and did not serve the application. |
| Root Cause | Azure Container Apps startup overrides replace image startup metadata, and the configured override separated the Uvicorn command and arguments incorrectly. |
| Resolution | The Azure startup command and args overrides were removed so the image command remained authoritative. |
| Verification | A later revision started without the malformed platform startup override and served the public health endpoint successfully. |
| Lessons Learned | Platform startup overrides must not be used when they alter the intended command and argument boundaries. For this workload, the Azure command and args fields must remain unset. |

**Incident 4 — Container image lacked a default Dockerfile command**

| Field | Detail |
| --- | --- |
| Issue | The container image did not define a default command for direct image execution. |
| Impact | Removing the Azure startup override left the image without an authoritative default process to start the API. |
| Root Cause | The Dockerfile did not yet contain the required exec-form Uvicorn `CMD`. |
| Resolution | The default exec-form command `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]` was added to the Dockerfile. |
| Verification | A later revision started from the image-defined command and served the public health endpoint successfully. |
| Lessons Learned | The deployable image must define its own default process so it can run consistently without platform-specific startup overrides. |

**Incident 5 — First startup-override removal attempt remained configured**

| Field | Detail |
| --- | --- |
| Issue | The deployment workflow attempted to clear overrides with `--command ""` and `--args ""`. Azure stored `command: [""]` and `args: [""]` instead of empty arrays. |
| Impact | Container Apps still treated startup overrides as configured, and the resulting revision entered `ActivationFailed`. |
| Root Cause | The quoted empty strings were parsed as one-element lists containing an empty string, not as empty lists. |
| Resolution | The Azure CLI flags were supplied with zero values as `--command` and `--args`. Azure persisted `command: null` and `args: null`, meaning no startup override was configured. |
| Verification | The succeeding deployment used the Dockerfile command and activated without the invalid empty-string override. |
| Lessons Learned | For Azure CLI list arguments, an empty string value and an empty list are operationally different. The resulting Azure resource template must be inspected after configuration changes. |

**Incident 6 — Healthy deployment reported as workflow failure**

| Field | Detail |
| --- | --- |
| Issue | The deployment verification loop required both `healthState == Healthy` and `runningState == Running`. The revision returned `Healthy`, while `runningState` was empty. |
| Impact | The workflow exhausted all 30 attempts and failed even though the revision was active and already serving traffic. |
| Root Cause | `runningState` was treated as a mandatory readiness signal even though Azure Container Apps did not populate it reliably for the active healthy revision. |
| Resolution | The workflow success condition was changed to `active == true` and `healthState == Healthy`. The HTTPS health verification remained as the final runtime check. |
| Verification | The final deployment workflow passed with the revision active and Healthy, followed by a successful public `/health` response. |
| Lessons Learned | Container Apps deployment readiness must use stable revision signals. Active state plus platform health, followed by an external HTTPS request, avoids false failures caused by an absent optional running-state value. |

**Incident 7 — Temporary local HTTPS timeout after deployment**

| Field | Detail |
| --- | --- |
| Issue | A local HTTPS `curl` request temporarily timed out after deployment. |
| Impact | The timeout temporarily obscured whether the successfully provisioned revision was externally reachable. |
| Root Cause | No Azure configuration fault was found. The exact cause of the transient local timeout was not established; ingress, target port, traffic allocation, replica count, and revision health were all correct. |
| Resolution | The HTTPS check was repeated using bounded retries instead of treating the first timeout as a definitive deployment failure. |
| Verification | A subsequent bounded retry succeeded and returned `{"status":"ok","service":"ai-job-scout-api"}`. The revision was active and Healthy, received 100% of traffic, and had one replica. |
| Lessons Learned | A single local timeout should not immediately be treated as deployment failure. Active revision, traffic, replica, and health state must be cross-checked before declaring the deployment failed. |

---

## 4. Lessons Learned

- Azure subscription policy must be evaluated before choosing a deployment
  region. East Asia is the validated region for this subscription.
- GitHub Actions OIDC avoids long-lived deployment credentials, but initial
  Entra and RBAC bootstrap operations remain subject to interactive Conditional
  Access and MFA controls.
- Bootstrap automation must be idempotent because an MFA interruption can leave
  valid partial state that should be reused rather than duplicated.
- The container image must own its startup command. Azure command and args
  overrides must remain absent for this deployment.
- Azure CLI list arguments require verification at the resource-template level:
  `[""]` is a configured empty-string value, while zero-value CLI flags remove
  the override and Azure persists the properties as `null`.
- Container Apps revision readiness is established by an active, Healthy
  revision. `runningState` is not a reliable mandatory signal for this runtime.
- Platform state alone is insufficient runtime evidence. The deployment gate
  must also call the public HTTPS health endpoint and validate its response.
- A single local timeout should not immediately be treated as deployment
  failure. Cross-check the active revision, traffic allocation, replica count,
  and revision health before declaring deployment failure.
- Full Git SHA image tags provide an auditable mapping from the running revision
  to source. The SHA tag, rather than a mutable convenience tag, is the
  deployment reference.

---

## 5. Remaining Risks

| Risk | Why It Remains | Why It Is Acceptable for Phase 1 |
| --- | --- | --- |
| The development deployment currently has one replica. | A single replica provides limited redundancy during a replica-level interruption. | This is the validated development environment, and Phase 1 establishes operability rather than production high availability. The risk is explicit and can be revisited for a production service level. |
| Interactive Azure administration remains subject to Conditional Access MFA. | Future Entra or RBAC changes can pause until an authorized operator completes MFA. | This is an intentional security control. Routine deployments use short-lived GitHub OIDC credentials and do not depend on an interactive session. |
| The runtime validation exercises the public health contract, not every application workflow. | The `/health` response confirms reachability and API process health but does not prove every business path. | Phase 1 validation is operational in scope, and the existing pytest gate provides predeployment application regression coverage. Broader product validation is outside the Phase 1 operations objective. |
| Region selection is constrained by Azure for Students policy. | Korea Central and Korea South remain unavailable under the current subscription policy. | East Asia is permitted and has a verified Healthy deployment, 100% traffic allocation, and a successful HTTPS health response. |
| Azure resource provisioning is manual. | ACR, the Container Apps environment, and the Container App cannot be recreated from repository Terraform or Bicep. | Phase 1 required a working deployable platform; infrastructure-as-code reproducibility is explicitly deferred to a future phase. |
| Log Analytics is minimum platform logging only. | Phase 1 did not implement broader monitoring, alerting, or an operational telemetry platform. | Minimum Container Apps platform logging is present, and broader operational visibility belongs to future platform hardening. |

---

## 6. Runtime Verification Checklist

- **PASS — GitHub Actions:** Automatic deployment from `main` completed for
  commit `131a119f798cc281f47f64e8990b93fe27d4555c`.
- **PASS — Azure:** The deployment is hosted in the permitted East Asia region.
- **PASS — Container Registry:** ACR
  `aijobscoutms2026.azurecr.io` contains repository `ai-job-scout`.
- **PASS — Container Apps:** `ca-ai-jobscout-dev` is deployed in
  `cae-ai-jobscout-dev`.
- **PASS — Revision:** `ca-ai-jobscout-dev--0000005` is the latest active
  revision and receives 100% of traffic.
- **PASS — HTTPS:** The public endpoint is reachable over HTTPS.
- **PASS — Health:** `/health` returns
  `{"status":"ok","service":"ai-job-scout-api"}` and the revision health
  state is `Healthy`.
- **PASS — Application:** The deployed API satisfies the Phase 1 functional
  health validation.
- **PASS — Tests:** The deployment's `pytest -q` gate completed with 25 passed
  and 1 existing warning.
- **PASS — Docker:** The image build and push completed, the full Git SHA tag is
  deployed, and `docker compose config --quiet` passed.

---

## 7. Runtime Summary

Phase 1 is complete with all Phase 0 and Phase 1 Tasks 1 through 5 marked PASS.
Commit `131a119f798cc281f47f64e8990b93fe27d4555c` is deployed from GitHub Actions
through OIDC as a traceable SHA-tagged image in Azure Container Apps, East
Asia. Revision `ca-ai-jobscout-dev--0000005` is active and Healthy, receives
100% of traffic, and returns the expected response from the public HTTPS health
endpoint. The recorded incidents were resolved through subscription-compliant
region selection, image-owned startup configuration, correct removal of Azure
startup overrides, and stable revision-readiness checks.

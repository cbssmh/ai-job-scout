# AI Job Scout: Cloud Operations Edition — Runtime Report

**Environment:** Azure development environment  
**Validated region:** East Asia  
**Evidence window:** 2026-07-18 through 2026-07-19 (KST)  
**Final runtime check:** 2026-07-18T17:08:52Z

## 1. Executive Summary

AI Job Scout was validated as a running Azure Container Apps workload with a traceable deployment path, separated workload identities, Key Vault-backed runtime secret delivery, and queryable application telemetry.

The final revision, `ca-ai-jobscout-dev--0000011`, was Active, Healthy, Provisioned, latest-ready, and serving 100% of application traffic. The public HTTPS health endpoint returned HTTP 200 with the expected response. Application Insights stored real request, duration, exception, dependency, and W3C correlation records from the deployed service.

The validated outcome is a completed development-environment operations project. It does not establish production readiness, high availability, enterprise scale, or full external-dependency coverage.

## 2. Deployment Overview

The normal delivery path starts from the `main` branch of `cbssmh/ai-job-scout`. GitHub Actions runs automated tests and Docker Compose validation, authenticates to Azure through OpenID Connect (OIDC), builds a `linux/amd64` image, pushes it to Azure Container Registry (ACR), updates Azure Container Apps, waits for an Active and Healthy revision, and verifies the public HTTPS health contract.

The application image defines the Uvicorn startup process. Azure Container Apps command and argument overrides remain unset, so the deployed runtime uses the image's authoritative startup metadata.

The original automated deployment path was proven with a full commit-SHA image tag. The final instrumented image, `phase3-observability-20260719-01`, was published through the existing ACR-to-Container Apps path and runs in revision `ca-ai-jobscout-dev--0000011`.

## 3. Azure Resources

| Resource | Verified runtime role |
| --- | --- |
| Subscription `d05a26b7-4017-48f1-a956-d9f919361d10` | Active Azure for Students subscription used for validation |
| Resource group `rg-ai-jobscout-dev` | Existing governance and resource boundary |
| ACR `aijobscoutms2026.azurecr.io` | Stores repository `ai-job-scout` and deployment images |
| Container Apps environment `cae-ai-jobscout-dev` | Hosts the application and provides managed ingress, revision support, scaling, and platform logging |
| Container App `ca-ai-jobscout-dev` | Runs the FastAPI/Uvicorn application |
| Key Vault `kv-ai-jobscout-dev` | Stores the versioned NVIDIA runtime credential |
| Application Insights `appi-ai-jobscout-dev` | Receives Azure Monitor OpenTelemetry application traces |
| Log Analytics `workspacergaijobscoutdeva4e1` | Stores queryable Application Insights telemetry |
| Microsoft Entra deployment application | Federates GitHub Actions without a client secret |
| Managed identities | Separate ACR image-pull and application secret-access responsibilities |

All listed Azure resources were verified in East Asia. The region reflects the locations permitted by the current subscription policy.

## 4. Runtime Verification

### Active Container App Revision

Azure reported final revision `ca-ai-jobscout-dev--0000011` as:

- Active: `true`
- Health state: `Healthy`
- Provisioning state: `Provisioned`
- Latest ready revision: `0000011`
- Replica count at final verification: `1`

The revision used the clean instrumented image. No temporary exception-validation code, environment flag, or validation image tag remained.

### Traffic Assignment

The Container App's ingress configuration assigned 100% of application traffic to revision `ca-ai-jobscout-dev--0000011`. The latest revision and latest-ready revision matched.

### HTTPS Verification

A bounded public request to the Azure Container Apps endpoint completed over HTTPS and returned HTTP 200. This independently verified public TLS reachability; Application Insights records may show the internal proxy-to-container URL scheme and do not replace the external HTTPS check.

### Health Endpoint

`GET /health` returned the unchanged application contract:

```json
{
  "status": "ok",
  "service": "ai-job-scout-api"
}
```

The final clean-revision client request completed in `0.168240 s`; its Application Insights request record reported an `8 ms` server duration. The observed first cold/scale-up request took `24.285015 s`, while warm client samples were approximately `0.149–0.190 s`. These were bounded operational samples, not a load test or performance benchmark.

## 5. Security Verification

### GitHub OIDC

The GitHub Actions deployment identity uses Microsoft Entra workload federation with the expected GitHub issuer, audience, repository, and `main` branch restriction. The Entra application had zero password credentials and zero key credentials. The validated deployment demonstrated successful OIDC authentication, ACR push, and Container Apps deployment.

### Managed Identity

Identity responsibilities are separated:

- the Container Apps environment identity (`system-environment`) has registry-scoped `AcrPull` access;
- the Container App has a system-assigned identity for runtime Key Vault access;
- the GitHub deployment identity publishes images and deploys revisions but has no Key Vault data-plane role.

The final observability deployment preserved both managed-identity paths.

### Key Vault

Key Vault secret `nvidia-api-key` is enabled in `kv-ai-jobscout-dev`. Container Apps stores a versionless Key Vault reference using the application system identity; it does not store or display the provider credential in the deployment configuration.

The existing application contract is preserved through this mapping:

```text
Key Vault secret nvidia-api-key
  -> Container Apps Key Vault reference
  -> Container Apps secret nvidia-api-key
  -> NVIDIA_API_KEY secretRef
  -> application runtime
```

No secret value is recorded in the repository or evidence documents.

### RBAC

The application system identity has `Key Vault Secrets User` at the dedicated vault scope. The GitHub identity retains `AcrPush` and Container Apps deployment access, while the environment identity retains registry-scoped `AcrPull`. Role-assignment inspection confirmed that deployment and image-pull identities do not have Key Vault data access.

The Key Vault boundary was verified through identity, role, reference, revision provisioning, and runtime state. An intrusive unauthorized secret-read attempt was not performed.

## 6. Observability Verification

### Application Insights

Workspace-based Application Insights resource `appi-ai-jobscout-dev` reported `Succeeded` and was linked to the existing Log Analytics workspace. The final Container App template contained `APPLICATIONINSIGHTS_CONNECTION_STRING`; its value was omitted from command output and documentation.

Azure Monitor OpenTelemetry trace instrumentation was deployed and observed. OpenTelemetry log export, metric export, and Live Metrics were intentionally disabled to preserve the project's trace-only scope.

### Request Telemetry

`AppRequests` contained real records for successful health requests, harmless 404 requests, and the controlled 500 validation request. Verified fields included:

- timestamp;
- request name and URL;
- HTTP result code and success state;
- server duration;
- request, parent, and operation identifiers.

Final clean-revision telemetry included `/health` with HTTP 200, `Success=true`, and an `8 ms` server duration. The removed validation path returned HTTP 404 and was also recorded.

### Exception Telemetry

A temporary, environment-gated FastAPI route generated one controlled HTTP 500 during validation. `AppExceptions` recorded the expected `RuntimeError`, message, problem identifier, method, severity, and trace identifiers. Immediate post-failure `/health` verification returned HTTP 200.

The temporary route, environment flag, and validation images were removed. The final deployed validation path returns 404.

### Correlation

The controlled 500 request and exception used the same W3C operation ID. The exception `ParentId` matched the corresponding request `Id`, proving direct request-to-exception correlation in stored telemetry.

### Dependency Telemetry Status

`AppDependencies` contained automatically generated, correlated `InProc` ASGI send spans. No external HTTP, database, or LLM dependency was invoked solely for evidence collection, and business logic was not modified.

Dependency telemetry status is therefore **Observed but limited**. It proves automatic in-process dependency visibility, not full external-dependency coverage.

## 7. Operational Outcomes

- The Azure subscription, resource group, naming, tagging, and cost-governance foundation supported the deployed workload.
- The application runs from ACR in Azure Container Apps with a verified revision and traffic model.
- The standard GitHub Actions path uses short-lived OIDC authentication and commit-SHA image traceability.
- Deployment, image pull, and runtime secret access use separate identities and scoped RBAC.
- The NVIDIA credential is delivered through Key Vault without changing the application's existing environment-variable contract.
- Public HTTPS, application health, revision state, replica state, and traffic were independently verified.
- Real request, status, duration, exception, and correlation telemetry was queried from Application Insights.
- The controlled failure did not leave a test-only route, flag, or image in the final runtime.
- The final automated suite passed with 27 tests and 21 non-blocking dependency deprecation warnings.
- `docker compose config --quiet` and repository whitespace validation passed.

## 8. Remaining Limitations

- This is a single development workload, not a production-readiness or high-availability assessment.
- SQLite data is container-local and ephemeral; backup, restore, and managed persistence were not implemented.
- Public application endpoints do not include an authentication or authorization layer.
- `minReplicas: 0` permits scale-to-zero and produced a materially slower cold request in the observed sample.
- No SLOs, alerts, dashboards, action groups, or capacity/load tests were introduced.
- Default telemetry sampling can store fewer records than the number of incoming requests.
- The linked workspace retains telemetry for 30 days.
- External dependency telemetry was not proven; only automatically emitted in-process spans were observed.
- A meaningful live Key Vault secret rotation was not executed because no distinct valid replacement NVIDIA credential was available. The documented runbook remains the authoritative future procedure.
- The health endpoint proves service startup and reachability but does not call NVIDIA or validate every business workflow.
- The final instrumented image uses a descriptive validation tag rather than a commit SHA; the normal automated deployment workflow remains SHA-based.
- Azure infrastructure was provisioned manually and is not reproducible from repository infrastructure-as-code definitions.

## 9. Evidence References

This report summarizes the following existing evidence and does not replace their command output, incident records, queries, or traceability matrices:

- [Container deployment runtime evidence](phase1-runtime-evidence.md)
- [Container deployment completion review](phase1-completion-summary.md)
- [Security runtime evidence](phase2-runtime-evidence.md)
- [Implemented security architecture](phase2-security-architecture.md)
- [Secret rotation runbook](phase2-secret-rotation-runbook.md)
- [Security completion review](phase2-completion-summary.md)
- [Observability runtime evidence](phase3-runtime-evidence.md)
- [Observability architecture decision](phase3-observability-architecture.md)
- [Final observability review](phase3-completion-summary.md)

The Azure foundation is summarized in the deployment completion review because the original foundation established the subscription, resource group, naming, tagging, budget, and cost-governance baseline reused by the runtime.

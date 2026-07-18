# Release Notes

## Current Release — AI Job Scout: Cloud Operations Edition

**Runtime validation completed:** 2026-07-19 (KST)

Cloud Operations Edition is the completed operational transformation of the
existing AI Job Scout application. It preserves product behavior while adding
a governed Azure foundation, repeatable container deployment, workload
identity separation, managed runtime secret delivery, and verified application
telemetry.

> “We are not improving the product. We are improving how the product is operated.”

This release represents a validated development deployment. It does not claim
production readiness, high availability, or enterprise scale.

### Operational transformation summary

- Preserved the existing FastAPI API, scoring policy, provider boundary,
  SQLite design, Streamlit dashboard, and Next.js client.
- Made the container image directly executable through its image-defined
  Uvicorn command.
- Established automated validation and Azure deployment from `main`.
- Separated deployment, image-pull, and runtime secret-access identities.
- Added trace-focused Azure Monitor OpenTelemetry instrumentation.
- Collected and queried real Azure runtime evidence before project closure.

### Azure foundation

- Reused the Azure for Students subscription and resource group
  `rg-ai-jobscout-dev`.
- Applied the established naming, tagging, budget, and cost-governance
  conventions.
- Deployed the validated development environment in East Asia after the
  subscription policy rejected Korea Central and Korea South.

### Deployment and OIDC

- Stores `linux/amd64` images in ACR
  `aijobscoutms2026.azurecr.io`, repository `ai-job-scout`.
- Runs the API in Azure Container App `ca-ai-jobscout-dev` inside environment
  `cae-ai-jobscout-dev`.
- Uses GitHub Actions OIDC federation with no Entra client secret or
  certificate credential.
- Restricts the federated subject to the repository's `main` branch.
- Uses full commit-SHA image tags in the normal automated deployment path.
- Waits for an Active and Healthy revision before performing bounded public
  HTTPS health verification.

### Managed identity, Key Vault, and RBAC

- Stores the NVIDIA runtime credential as Key Vault secret `nvidia-api-key` in
  `kv-ai-jobscout-dev` without recording its value.
- Uses the Container App system-assigned identity and `Key Vault Secrets User`
  at the dedicated vault scope.
- Supplies the application through a versionless Key Vault reference mapped to
  the existing `NVIDIA_API_KEY` contract.
- Retains the Container Apps environment identity for registry-scoped
  `AcrPull`.
- Retains the GitHub OIDC identity for `AcrPush` and Container Apps deployment,
  without Key Vault data-plane access.

Meaningful live secret rotation was not performed because no distinct valid
replacement provider credential was available. The completed rotation and
rollback procedure is documented in
[the secret rotation runbook](docs/phase2-secret-rotation-runbook.md).

### Application Insights and OpenTelemetry

- Uses workspace-based Application Insights `appi-ai-jobscout-dev`, linked to
  the existing Log Analytics workspace.
- Initializes the Azure Monitor OpenTelemetry distribution before FastAPI is
  imported when runtime telemetry is configured.
- Exports trace-based request, exception, correlation, and automatically
  available dependency telemetry.
- Leaves OpenTelemetry log export, metric export, and Live Metrics disabled.
- Removes the temporary controlled-exception route, flag, and validation image
  tags after evidence collection.

### Runtime verification

- Final revision: `ca-ai-jobscout-dev--0000011`.
- Revision state: Active, Healthy, Provisioned, and latest-ready.
- Traffic: 100% assigned to the final revision.
- Replica count during final verification: one.
- Public `GET /health`: HTTPS 200 with
  `{"status":"ok","service":"ai-job-scout-api"}`.
- Request telemetry: real 200, 404, and controlled 500 results with timestamps,
  durations, success state, and W3C identifiers.
- Exception telemetry: controlled `RuntimeError` correlated directly to its
  originating 500 request.
- Dependency telemetry: automatically emitted in-process ASGI spans observed;
  external dependency coverage remains limited.
- Automated validation: 27 tests passed; Docker Compose configuration and
  repository whitespace validation passed.

See the [final runtime report](docs/runtime-report.md) for the consolidated
runtime record and links to the detailed evidence.

### Known limitations

- The deployment is a development workload and is not presented as
  production-ready or highly available.
- SQLite data remains container-local and ephemeral.
- Public application endpoints have no authentication or authorization layer.
- Scale-to-zero creates an observed cold-start trade-off.
- No SLOs, alerts, dashboards, action groups, or load tests are included.
- External HTTP, database, and LLM dependency telemetry was not exercised.
- Meaningful live provider-secret rotation remains deferred.
- The final observability validation image uses a descriptive tag; the normal
  automated workflow remains commit-SHA based.
- Azure infrastructure was provisioned manually rather than through
  repository infrastructure as code.

## Historical Release — v1.0.0 AI Job Scout MVP

The original MVP established the application behavior later operated by Cloud
Operations Edition. The notes below preserve that release's product scope and
historical limitations.

### MVP highlights

- AI-assisted structured job analysis for role, technology stack, experience
  level, language requirement, visa signal, and summary.
- Deterministic recommendation scoring with skill, language, visa, and
  location score components.
- Lightweight NVIDIA NIM provider support through an OpenAI-compatible API.
- FastAPI REST API with Swagger documentation.
- Docker Compose development environment.
- Greenhouse job ingestion and job lifecycle handling.
- Focused automated tests for scoring, parsing, lifecycle, health routes, and
  provider configuration.

### MVP installation notes

Python 3.11 or later is required.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python -m pytest
```

Optional manual NVIDIA smoke test:

```bash
python scripts/test_nvidia_api.py
```

### MVP limitations recorded at release

- NVIDIA free access was externally controlled and subject to change.
- No automatic paid provider fallback was implemented by design.
- SQLite was used for local development and portfolio demonstration.
- Recommendation scoring was explainable but intentionally simple.
- Dependencies were not pinned, so fresh-install reproducibility could vary.

### Capabilities not included in the MVP release

- Provider benchmarking
- Cost or token dashboards
- Model routing
- Deployment automation
- GitHub Package publishing
- Production traffic or uptime claims

Deployment automation and essential Azure telemetry were added later by Cloud
Operations Edition; the other exclusions remain outside the completed project
scope unless explicitly described above.

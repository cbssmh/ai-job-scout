# Phase 3 Observability Architecture

**Phase:** Observable Essentials  
**Decision status:** Accepted and verified  
**Date:** 2026-07-19 (KST)  
**Runtime:** Azure Container Apps, Python 3.11, FastAPI, Uvicorn

## Current-State Findings

- The image starts with `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Azure command and args overrides remain absent.
- `/health` is the existing side-effect-free health contract and returns
  `{"status":"ok","service":"ai-job-scout-api"}`.
- Python logging writes INFO-level records to standard output.
- The Container Apps environment already sends platform logs to Log Analytics,
  but that path did not provide application requests, result codes, latency,
  exceptions, or request/exception correlation.
- No Application Insights resource or application telemetry configuration
  existed before Phase 3.
- The existing Phase 2 system identity, Key Vault reference, RBAC, ACR pull
  identity, ingress, and GitHub OIDC deployment boundary were intact.

## ADR — Minimum Application Observability

### Context

The service was reachable and platform logs existed, but an operator could not
query application request timestamps, routes, result codes, durations,
exceptions, or correlated failures. Container health alone was insufficient for
runtime investigation.

Azure Container Apps does not provide no-code Python/FastAPI request
instrumentation. Its managed OpenTelemetry agent routes telemetry, but Microsoft
documents that the application must still install the OpenTelemetry SDK and emit
instrumented data. Microsoft also documents that Python FastAPI instrumentation
must be configured before `FastAPI` is imported or accessed.

### Decision

Use one workspace-based Application Insights resource,
`appi-ai-jobscout-dev`, linked to the existing East Asia Log Analytics
workspace `workspacergaijobscoutdeva4e1`.

Install the Microsoft `azure-monitor-opentelemetry` distribution and initialize
it once in `app/telemetry.py`. `app/main.py` calls the initializer before
importing FastAPI. Initialization is conditional on
`APPLICATIONINSIGHTS_CONNECTION_STRING`, so local and test behavior remains
unchanged when Azure telemetry is not configured.

Disable log export, metric export, and Live Metrics. Phase 3 collects only the
trace-based signals required for essential operation. Existing stdout logging
and Container Apps platform logging remain separate and unchanged.

The connection string is supplied through Container Apps configuration and is
never committed or printed. Microsoft classifies the embedded instrumentation
key as an identifier rather than a security token or key. Key Vault remains
reserved for the actual NVIDIA credential, preserving the Phase 2 security
boundary.

### Telemetry Scope

- Requests and timestamps
- HTTP result codes and success state
- Request duration
- Unhandled exceptions
- W3C trace/request/exception correlation
- Dependencies when automatically emitted
- Existing HTTPS health verification

No route-level, service-level, repository-level, scoring, AI, database, or UI
telemetry calls are added.

### Alternatives

| Alternative | Evaluation | Decision |
| --- | --- | --- |
| Container Apps platform logs only | Preserves zero code change but does not provide the required request, duration, exception, or correlation records. | Rejected as insufficient. |
| Application Insights platform automatic instrumentation | No supported no-code Python/FastAPI instrumentation path exists for this Container Apps deployment. | Rejected as technically invalid. |
| Container Apps managed OpenTelemetry agent | Routes OTLP data but still requires application SDK instrumentation; adds environment-level configuration and a managed single-replica agent without removing the code requirement. | Rejected as unnecessary for one application/destination. |
| Centralized Azure Monitor OpenTelemetry initialization | Adds one package and one isolated startup initializer; FastAPI, HTTP client, and supported framework instrumentation are automatic after initialization. | Selected. |
| Manual telemetry throughout business layers | Could capture custom details but increases coupling and risks product behavior changes. | Rejected. |
| Full dashboards, workbooks, metrics, alerts, and action groups | Exceeds the essential observability requirement and Phase 3 scope. | Rejected. |

### Reason

The selected design is the smallest supported implementation that produces the
mandatory runtime evidence. It changes startup only, uses the existing Azure
Monitor workspace, adds one Azure resource, and leaves all business and
user-facing behavior frozen.

### Consequences

#### Benefits

- Operators can query request time, operation name, URL, result code, duration,
  success, request ID, and operation ID.
- Unhandled exceptions can be joined directly to their originating request.
- Standard W3C `traceparent` values propagate into Application Insights.
- Supported dependencies appear without business-layer instrumentation.
- Local execution remains telemetry-free unless explicitly configured.

#### Limitations and trade-offs

- Telemetry ingestion and query availability are not instantaneous.
- Default SDK sampling can omit members of a burst; validation used spaced
  requests and explicit sampled W3C trace contexts.
- Automatically emitted dependency records in this validation window were
  limited to in-process ASGI send spans; no external business dependency was
  invoked solely for evidence.
- Application Insights records the internal reverse-proxy request URL as HTTP;
  independent runtime validation proves the public endpoint remains HTTPS.
- The linked Log Analytics workspace incurs normal ingestion/retention cost.
- The final image was deployed directly through the existing ACR-to-Container
  Apps mechanics because commit and push were explicitly prohibited. The GitHub
  Actions workflow remains unchanged and valid.

### Validation

The decision was verified through actual Azure runtime data:

- `ca-ai-jobscout-dev--0000011` is Active, Healthy, Provisioned, has one
  replica, and receives 100% traffic.
- HTTPS `/health` returns the unchanged HTTP 200 contract.
- `AppRequests` contains `/health` 200 and a harmless 404 with timestamps,
  durations, request IDs, parent IDs, and operation IDs.
- `AppExceptions` contains a controlled `RuntimeError`; its operation ID equals
  the request operation ID and its parent ID equals the request ID.
- `AppDependencies` contains automatically emitted in-process dependency spans.
- The temporary exception mechanism, flag, path, and ACR images were removed.
- The final validation path returns 404 and normal health remains 200.

Detailed commands and timestamps are in
[`phase3-runtime-evidence.md`](phase3-runtime-evidence.md).

## Authoritative Technical References

- [Collect and read OpenTelemetry data in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/opentelemetry-agents)
- [Enable OpenTelemetry in Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable)
- [Troubleshoot OpenTelemetry issues in Python](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-monitor/app-insights/telemetry/opentelemetry-troubleshooting-python)
- [Application Insights connection strings](https://learn.microsoft.com/en-us/azure/azure-monitor/app/connection-strings)

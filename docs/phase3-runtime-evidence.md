# Phase 3 Runtime Evidence

**Phase:** Observable Essentials  
**Evidence window:** 2026-07-18 16:56–17:08 UTC  
**Final runtime check:** 2026-07-18T17:08:52Z  
**Result:** PASS

## Evidence Handling

Commands are reproducible and value-filtered. The Application Insights
connection string, instrumentation key, NVIDIA credential, authorization
headers, and secret values are not recorded. Azure timestamps are UTC.

The public client durations below are a small manual sample for operational
verification, not a load test or performance benchmark.

## Configured, Deployed, Observed, and Verified

| State | Meaning | Phase 3 evidence |
| --- | --- | --- |
| Configured | Resource and application settings exist. | Application Insights is linked to the existing workspace; the final template contains the telemetry environment-variable name. |
| Deployed | Instrumented code is running in Azure. | Final image `phase3-observability-20260719-01` runs in revision `0000011`. |
| Observed | Azure accepted and stored real telemetry. | `AppRequests`, `AppExceptions`, and `AppDependencies` returned runtime records. |
| Verified | Stored records satisfy a specific operational gate. | Health, status, duration, exception detail, and request/exception correlation were queried by known operation IDs. |

## Evidence Register

| Evidence ID | Purpose | Verification Method | Command or Query | Timestamp | Observed Result | Evidence Reference | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-E01 | Confirm authenticated Azure context | Azure CLI account inspection | `az account show --output table` and `az account show --query id -o tsv` | 2026-07-18 16:49 UTC | Tenant `가천대학교`; subscription `Azure for Students`; ID `d05a26b7-4017-48f1-a956-d9f919361d10` | CLI session | PASS |
| P3-E02 | Establish pre-change observability baseline | Value-filtered resource, app, revision, environment, workspace, and resource-type queries | `az containerapp show`, `az containerapp revision list`, `az containerapp env show`, `az monitor log-analytics workspace list`, `az resource list --resource-type Microsoft.Insights/components` | 2026-07-18 16:45 UTC | Revision `0000007` Active/Healthy/Provisioned at 100%; Log Analytics configured; no Application Insights component | CLI session | PASS |
| P3-E03 | Verify Application Insights resource | Inspect component without connection-string output | `az monitor app-insights component show --app appi-ai-jobscout-dev -g rg-ai-jobscout-dev --query <redacted-fields>` | 2026-07-18T17:08:52Z | `Succeeded`, East Asia, workspace-based, linked to `workspacergaijobscoutdeva4e1` | Sanitized final resource snapshot | PASS |
| P3-E04 | Verify instrumentation configuration | Inspect final environment-variable names and source | `az containerapp show ... --query properties.template.containers[0].env[].{name:name,secretRef:secretRef}` | 2026-07-18T17:08:52Z | `APPLICATIONINSIGHTS_CONNECTION_STRING` present; value omitted; `NVIDIA_API_KEY` still uses `secretRef: nvidia-api-key` | Final template snapshot | PASS |
| P3-E05 | Verify instrumented image publication | Inspect latest ACR tags | `az acr repository show-tags -n aijobscoutms2026 --repository ai-job-scout --orderby time_desc` | 2026-07-18 17:08 UTC | Clean tag `phase3-observability-20260719-01` exists; temporary validation tags deleted | ACR tag list | PASS |
| P3-E06 | Verify final running revision | Inspect specific revision | `az containerapp revision show ... --revision ca-ai-jobscout-dev--0000011` | 2026-07-18T17:08:52Z | Active `true`, Healthy, Provisioned, one replica, clean Phase 3 image | Final revision snapshot | PASS |
| P3-E07 | Verify traffic assignment | Inspect Container App ingress traffic and ready revision | `az containerapp show ... --query '{latestRevision:...,latestReadyRevision:...,traffic:...}'` | 2026-07-18T17:08:52Z | Latest and latest-ready are `0000011`; latest revision receives 100% | Final app snapshot | PASS |
| P3-E08 | Verify public HTTPS health contract | Real HTTPS request with bounded timeouts | `curl --fail --connect-timeout 10 --max-time 30 https://.../health` | 2026-07-18 17:07 UTC | HTTP 200; `{"status":"ok","service":"ai-job-scout-api"}`; client duration 0.168240 s | Runtime request | PASS |
| P3-E09 | Verify request timestamp, operation, URL, status, duration, and IDs | Query `AppRequests` by known W3C trace IDs | See Request Telemetry Query | 2026-07-18 16:59 UTC | `/health` 200 at 2 ms and 1 ms; missing path 404 at 1 ms; timestamps, URLs, success, request IDs, parent IDs, and operation IDs visible | Operation IDs `1111…`, `3333…`, `5555…` | PASS |
| P3-E10 | Verify clean-final request telemetry | Query `AppRequests` by final trace IDs | See Final Revision Query | 2026-07-18 17:07 UTC | Final `/health` 200, 8 ms; removed validation path 404, 1 ms | Operation IDs `dddd…` and `eeee…` | PASS |
| P3-E11 | Verify exception telemetry | Controlled hidden route enabled only in temporary revision; query `AppExceptions` | See Exception Query | 2026-07-18T17:04:44Z | `RuntimeError`; message `Phase 3 controlled exception validation`; problem ID visible | Operation ID `bbbb…` | PASS |
| P3-E12 | Verify request/exception correlation | Compare `AppRequests` and `AppExceptions` identifiers | Request and exception queries filtered on `bbbb…` | 2026-07-18T17:04:44Z | Same operation ID; exception parent ID `b27e068fc7919a90` equals request ID | Joined query evidence | PASS |
| P3-E13 | Verify safe recovery after controlled failure | HTTPS checks before and after one controlled 500 | `curl` normal health, controlled route, normal health | 2026-07-18 17:04 UTC | Controlled request returned 500; immediate post-test `/health` returned 200 | Runtime request output | PASS |
| P3-E14 | Check automatically available dependencies | Query `AppDependencies` without invoking a business dependency | See Dependency Query | 2026-07-18 16:57–17:04 UTC | Automatically emitted `InProc` ASGI send spans are visible and correlated; no external dependency was invoked | `AppDependencies` output | Observed but limited |
| P3-E15 | Prove temporary mechanism removal | Source search, final env inspection, ACR deletion, and final 404 | `rg` temporary markers; final template query; exact ACR image deletes; HTTPS request to removed path | 2026-07-18 17:07–17:08 UTC | No temporary code/flag/image tags remain; path returns 404 | Source, ACR, and runtime checks | PASS |
| P3-E16 | Preserve Phase 2 security controls | Inspect identity, Key Vault reference, registry identity, and template | Value-filtered `az containerapp show` | 2026-07-18T17:08:52Z | System identity unchanged; Key Vault-backed `nvidia-api-key` unchanged; no secret value displayed; command/args remain null | Final app snapshot | PASS |
| P3-E17 | Preserve GitHub Actions deployment | Repository diff and existing workflow validation path | `git diff --quiet -- .github/workflows/deploy.yml`; review deploy workflow | 2026-07-18 17:07 UTC | No workflow change; OIDC, tests, Compose, SHA build/push, revision wait, and HTTPS health steps remain | Repository check | PASS |
| P3-E18 | Preserve local behavior and build validity | Full tests, Compose render, whitespace validation | `pytest -q`; `docker compose ... config --quiet`; `git diff --check` | 2026-07-18 17:07 UTC | 27 passed; 21 non-blocking deprecation warnings; Compose and diff checks passed | Local validation output | PASS |

## Reproducible Telemetry Queries

### Request Telemetry Query

```kusto
AppRequests
| where TimeGenerated >= ago(30m)
| where OperationId in (
    "11111111111111111111111111111111",
    "33333333333333333333333333333333",
    "55555555555555555555555555555555")
| project TimeGenerated, Name, Url, ResultCode, DurationMs, Success,
          OperationId, ParentId, Id
| order by TimeGenerated asc
```

Observed representative records:

| Name | Result | Server duration | Success | Operation ID |
| --- | --- | --- | --- | --- |
| `GET /health` | 200 | 2 ms | true | `11111111111111111111111111111111` |
| `GET /phase3-not-found` | 404 | 1 ms | false | `33333333333333333333333333333333` |
| `GET /health` | 200 | 1 ms | true | `55555555555555555555555555555555` |

### Exception Query

```kusto
AppExceptions
| where OperationId == "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
| project TimeGenerated, ExceptionType, OuterMessage, InnermostMessage,
          OperationId, ParentId, ProblemId, Method, SeverityLevel
```

The corresponding request query returned request ID `b27e068fc7919a90`, HTTP
500, and 13 ms. The exception record used the same operation ID and
`ParentId == b27e068fc7919a90`.

### Dependency Query

```kusto
AppDependencies
| where TimeGenerated >= ago(60m)
| project TimeGenerated, Name, DependencyType, Target, Data, ResultCode,
          DurationMs, Success, OperationId, ParentId
| order by TimeGenerated desc
```

Only automatically generated `InProc` ASGI send spans were observed. This is
classified as **Observed but limited**, not evidence of an external HTTP or
database dependency.

### Final Revision Query

```kusto
AppRequests
| where OperationId in (
    "dddddddddddddddddddddddddddddddd",
    "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
| project TimeGenerated, Name, ResultCode, DurationMs, Success,
          OperationId, ParentId, Id, Url
| order by TimeGenerated asc
```

Final clean-revision records:

- `/health`: HTTP 200, 8 ms, `Success=true`.
- Removed validation path: HTTP 404, 1 ms, `Success=false`.

## Latency Evidence

Public HTTPS client samples included:

- First cold/scale-up health request: 24.285015 s.
- Warm health and harmless route requests: approximately 0.149–0.190 s.
- Final clean-revision health request: 0.168240 s.

Application Insights server-side samples included 1 ms, 2 ms, 8 ms, and 13 ms.
These values prove that latency fields are available. They are not a capacity,
load, percentile, or performance benchmark.

## Evidence Conclusion

Application Insights is configured, deployed, observed, and verified. Requests,
result codes, durations, health traffic, exceptions, and correlation are
queryable. The final revision is healthy and the temporary validation mechanism
has been removed. Phase 3 runtime evidence is complete.

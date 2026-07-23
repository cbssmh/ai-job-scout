# Gate 3 Runtime Evidence

Project lifecycle is **CONDITIONAL CLOSEOUT** and v2.1.0 is **NOT RELEASED**. This file records the absence of validation-runtime evidence and the continued health of the protected v2.0.0 runtime.

## Validation Runtime

Validation runtime evidence is unavailable because Stage A failed before the Container Apps Environment and Container App could be created.

| Check | Result | Evidence |
| --- | --- | --- |
| Validation Container Apps Environment | NOT CREATED | Regional and later subscription-global admission failures |
| Image copy | NOT RUN | Execution stopped before external copy |
| Digest equality | NOT RUN | No destination manifest exists |
| Secretless Container App | NOT RUN | Stage B not reached |
| Dummy secret metadata | NOT RUN | No secret was injected |
| Final secret reference | NOT RUN | Stage C not reached |
| Validation `/health` | NOT RUN | No validation runtime exists |
| Validation telemetry | NOT RUN | No validation request exists |
| Post-apply no-change plan | NOT RUN | Final desired state was not provisioned |

## Protected Dev Runtime

| Evidence ID | Phase | HTTP | Body | Elapsed |
| --- | --- | ---: | --- | ---: |
| TF-EVIDENCE-002 | Before apply | 200 | `{"status":"ok","service":"ai-job-scout-api"}` | 23.129 s |
| TF-EVIDENCE-008 | After partial failure | 200 | `{"status":"ok","service":"ai-job-scout-api"}` | 22.152 s |

No external AI request was performed.

## Japan West Regional Retry

The Japan West retry did not reach a validation runtime. Stage A failed while creating the Container Apps Environment because Azure enforced a subscription-wide one-environment limit.

| Check | Result | Evidence |
| --- | --- | --- |
| Japan West preflight | PASS | Regional usage 0/1; names available; empty state |
| Stage A plan | PASS | 7 add, 0 change, 0 destroy |
| Stage A apply | FAIL | Global Container Apps Environment limit |
| Partial foundation | DESTROYED AT CLOSEOUT | Final Terraform plan destroyed the five managed resources |
| Image copy | NOT RUN | Containment stop |
| Stage B | NOT RUN | No Container Apps Environment |
| Dummy secret | NOT RUN | No secret created |
| Stage C | NOT RUN | No Container App |
| Validation health | NOT RUN | No validation runtime |
| Validation telemetry | NOT RUN | No validation request |
| Final no-change plan | NOT RUN | Final state not provisioned |

Protected dev after retry failure:

| Phase | HTTP | Body | Resource Count | Elapsed |
| --- | ---: | --- | ---: | ---: |
| Before retry | 200 | expected health response | 7 | 23.189 s |
| After retry failure | 200 | expected health response | 7 | 0.503 s |
| After Conditional Closeout cleanup | 200 | expected health response | 7 | 0.141 s |

No external AI request was performed.

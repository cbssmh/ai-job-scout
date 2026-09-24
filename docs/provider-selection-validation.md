# Provider-Selection Validation

- **Date:** 2026-09-24
- **Decision:** **NONE**
- **Scope:** Read-only provider validation using synthetic job postings
**Production changes:** None

## Executive decision

No provider/model combination is approved for AI Job Scout production.

The only locally accessible provider was the NVIDIA Public API Endpoint. Its
best candidate, `z-ai/glm-5.3-flash`, used native strict JSON Schema and met the
application contract in 13 of 15 trials. Two requests timed out at the existing
30-second boundary, producing a 13.3% degraded-fallback rate. That is not a
production-safe result. More importantly, NVIDIA documents its hosted catalog
endpoints as development/prototyping access; production use requires NVIDIA AI
Enterprise and a production deployment. The tested public endpoint therefore
is not an approved production endpoint even if its model reliability improves.

The repository already has a minimal OpenAI client path and defaults its OpenAI
candidate to `gpt-4.1-mini`, but no usable OpenAI API credential was locally
available. Documentation proves compatibility, not account access or runtime
reliability, so OpenAI is not approved from this phase.

## Guardrails observed

- No production request or production configuration mutation was made.
- `.env` was read only to identify whether credentials were present; it was not
  modified and no credential value was printed or retained.
- Azure Key Vault was not accessed or modified.
- Neither NVIDIA credential was revoked or altered.
- PR #5 was not merged. A read-only check found it open with `mergedAt: null`.
- Provider response bodies were held only in memory for validation and were not
  logged or written to the metrics artifact.
- All job postings were synthetic.

## Application contract used

A strict success required all of the following:

1. OpenAI-style chat-completion system and user messages were accepted.
2. Message content was exactly one JSON object, with no fence or prose wrapper.
3. All six required fields were present and non-null:
   `role`, `tech_stack`, `experience_level`, `language_requirement`,
   `visa_sponsorship`, and `summary`.
4. Every required value was a string.
5. The call completed inside 30 seconds with automatic SDK retries disabled.
6. `temperature=0` was accepted.

`degraded_fallback` was measured using the current application boundary: a
request degrades when the response cannot be parsed as an object after the
existing cleanup step or a required field is absent/null. Strict contract
success is narrower because a fenced or otherwise wrapped object is a format
violation even when the current cleanup code can recover it.

## Test design

The full suite used three trials for each of five synthetic scenarios:

- clear backend role;
- ambiguous platform/cloud role;
- security-oriented role;
- long/noisy posting; and
- sparse posting.

Each model was first probed, in order, with strict JSON Schema, JSON-object
mode, and prompt-only output. The first mode to satisfy the complete contract
was used for the full suite. When all three probes failed, the candidate was
classified as unavailable within the approved timeout and the 15-call suite was
not run; additional calls could not establish contract behavior while the
candidate was unreachable.

The harness is
[`scripts/validate_provider_candidates.py`](../scripts/validate_provider_candidates.py).
It records only timings, booleans, status codes, and exception classes. It uses
synthetic inputs, does not access the application database, Azure, or Key
Vault, and refuses to run unless the operator explicitly acknowledges that
live provider calls can consume quota or incur cost.

## Repository retention review

Both validation artifacts are retained because they provide decision evidence
and a reproducible contract test, not to increase documentation or test count.

- This report contains no credentials or provider response bodies. Its inputs
  are synthetic, its decision is **NONE**, and its p50/p95-like values are
  explicitly described as observations from a small sample rather than SLA or
  population claims.
- The harness contains no credential. It accepts credentials only from process
  environment or the ignored local `.env`, uses synthetic postings by default,
  stores metrics rather than response bodies, and has no application database,
  Azure, Key Vault, deployment, or credential-management code. Its required
  live-call acknowledgement reduces accidental quota/cost consumption.

## Access discovery

| Provider | Current access | Candidate | Basis |
| --- | --- | --- | --- |
| NVIDIA Public API | Yes, local development credential | Current hosted instruction/chat shortlist | Live `/models` returned 82 IDs; inference availability was verified separately because listing did not guarantee a usable completion endpoint. |
| OpenAI | No usable local API credential | `gpt-4.1-mini` | Repository supports it directly, but runtime testing was not possible. |
| Other OpenAI-compatible provider | No credential or configured provider path found | None | Adding provider configuration and obtaining credentials would exceed this validation phase. |

The configured NVIDIA model, `z-ai/glm-5.2`, was absent from the live model
listing and returned HTTP 410 in all three availability probes.

## NVIDIA results

Percentages for candidates marked **probe only** describe the three capability
probes, not the five-scenario suite. `p50/p95` are nearest-rank values from
completed calls in this small sample and are not population guarantees.
Format violations are assessable only when message content is returned; `N/A`
means that every request failed or timed out before a body was available.

| Model | Scope | Mode selected | Contract success | Timeout | Provider/HTTP error | JSON parse | Field complete | Degraded fallback | Format violation | Completed latency p50 / p95 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `z-ai/glm-5.2` | Probe only | None | 0/3 | 0/3 | 3/3 HTTP 410 | 0/3 | 0/3 | 3/3 | N/A | N/A |
| `ibm/granite-3.0-3b-a800m-instruct` | Probe only | None | 0/3 | 0/3 | 3/3 HTTP 404 | 0/3 | 0/3 | 3/3 | N/A | N/A |
| `google/gemma-3-4b-it` | Probe only | None | 0/3 | 0/3 | 3/3 HTTP 404 | 0/3 | 0/3 | 3/3 | N/A | N/A |
| `mistralai/mistral-7b-instruct-v0.3` | Probe only | None | 0/3 | 0/3 | 3/3 HTTP 404 | 0/3 | 0/3 | 3/3 | N/A | N/A |
| `nvidia/mistral-nemo-minitron-8b-8k-instruct` | Probe only | None | 0/3 | 0/3 | 3/3 HTTP 404 | 0/3 | 0/3 | 3/3 | N/A | N/A |
| `openai/gpt-oss-20b` on NVIDIA | Probe only | None | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 | 3/3 | N/A | N/A |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | Probe only | None | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 | 3/3 | N/A | N/A |
| `z-ai/glm-5.3-flash` | Full suite | Strict JSON Schema | 13/15 (86.7%) | 2/15 (13.3%) | 0/15 | 13/15 (86.7%) | 13/15 (86.7%) | 2/15 (13.3%) | 0/13 completed | 15.437s / 24.463s |
| `deepseek-ai/deepseek-v4.1-flash` | Probe only | None | 0/3 | 2/3 | 0/3 | 0/3 | 0/3 | 3/3 | 1/1 completed | 18.673s / 18.673s |

### Full-suite case breakdown for `z-ai/glm-5.3-flash`

| Synthetic case | Success | Timeout | Completed latencies |
| --- | ---: | ---: | --- |
| Clear backend | 3/3 | 0/3 | 11.147s, 13.618s, 19.363s |
| Ambiguous platform/cloud | 3/3 | 0/3 | 11.263s, 11.461s, 12.722s |
| Security-oriented | 2/3 | 1/3 | 15.437s, 15.509s |
| Long/noisy | 2/3 | 1/3 | 14.801s, 17.514s |
| Sparse | 3/3 | 0/3 | 20.420s, 21.236s, 24.463s |

The strict output control eliminated observed parse, completeness, and format
failures on completed GLM calls. It did not solve endpoint latency/reliability.

## Timeout decision

No timeout increase is approved.

The successful GLM sample had p50 15.437 seconds and p95-like 24.463 seconds,
but two calls still reached the 30-second boundary. Other candidates timed out
in every probe. A larger timeout might convert some timeouts into completions,
but this sample does not show what their eventual latency would be, and a
40–60 second synchronous wait would materially worsen blocking behavior.
Because the tested NVIDIA endpoint is also not production-entitled, increasing
the application timeout cannot make this candidate production-safe.

Any later candidate should first be tested at 30 seconds. A higher value should
be considered only after a full suite on a production-supported endpoint shows
a tight latency distribution, zero timeouts, and enough headroom between the
observed tail and the proposed boundary.

## Cost, entitlement, and production endpoint status

| Provider/candidate | Free/trial/paid status | Production endpoint/SLA | Uncertainty |
| --- | --- | --- | --- |
| NVIDIA Public API candidates | Current credential can access developer endpoints. NVIDIA says Developer Program API access is free for prototyping, research, development, and testing. | The tested hosted catalog endpoint is not a production entitlement. NVIDIA says production requires NVIDIA AI Enterprise; NIM can be self-hosted or deployed through cloud partners. Enterprise support includes defined SLAs. This would add infrastructure and licensing beyond the current architecture. | No evidence was obtained that either existing NVIDIA credential includes AI Enterprise production entitlement. Hosted public-endpoint pricing/SLA was not established. |
| OpenAI `gpt-4.1-mini` | Paid API; official model limits show no Free tier. Published PAYG text-token prices are $0.40/M input, $0.10/M cached input, and $1.60/M output. | Chat Completions and Structured Outputs are supported. OpenAI Scale Tier for Enterprise lists GPT-4.1 mini with a 99.9% uptime SLA and a latency SLA, but requires purchased capacity. | Current account access, billing tier, rate limits, and any Enterprise/Scale entitlement are unknown because no credential was available. Standard PAYG SLA was not established by the reviewed sources. |

Sources:

- [NVIDIA NIM General FAQ](https://docs.api.nvidia.com/nim/docs/product)
- [NVIDIA NIM deployment options](https://docs.api.nvidia.com/nim/docs/run-anywhere)
- [OpenAI GPT-4.1 mini model documentation](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI Scale Tier](https://openai.com/api-scale-tier/)

## Recommendation

**NONE.**

- Do not replace the production model with any tested NVIDIA public-endpoint
  candidate.
- Do not approve OpenAI from documentation alone.
- Do not change the 30-second timeout at this stage.
- Do not create a provider/model migration plan yet; the user requested a
  separate plan only after a candidate is approved.

The next provider-selection step requires explicit approval to supply or use a
non-production OpenAI API credential with billing enabled. Re-run the same five
synthetic cases against `gpt-4.1-mini` with strict JSON Schema, at least three
trials per case, and the same 30-second boundary. If that candidate does not
produce zero provider errors, zero timeouts, zero format/completeness failures,
and acceptable tail latency in the sample, retain the **NONE** decision.

## Separate evidence tracks

### 1. Provider/model migration

Status: **Not approved; no migration plan and no execution.**

This report is validation evidence only. The existing OpenAI-compatible client
shape makes a future OpenAI migration small in code terms, but access,
reliability, latency, and entitlement remain unproven.

### 2. NVIDIA credential containment

Status: **Unchanged and not exercised.**

No credential was printed, persisted in evidence, rotated, disabled, or
revoked. Key Vault was not accessed. This track remains governed by the
existing containment/rotation runbook and must not be inferred from provider
selection results.

### 3. PR #5 deployment-path hardening

Status: **Unchanged and unmerged.**

The read-only check on 2026-09-24 found
[PR #5](https://github.com/cbssmh/ai-job-scout/pull/5) open against `main`, with
no merge timestamp. Provider selection neither approves nor validates that
deployment path.

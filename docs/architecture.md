# Architecture

AI Job Scout is a local-first FastAPI backend for collecting software engineering job postings, extracting structured signals from raw descriptions, and returning explainable job recommendations. The current design favors simple module boundaries over infrastructure breadth.

## System Context

```mermaid
flowchart LR
    A["Greenhouse board API"] --> B["scripts/fetch_greenhouse_jobs.py"]
    B --> C["app.crawler.greenhouse.fetch_greenhouse_jobs"]
    C --> D["app.services.job_service.upsert_job"]
    D --> E[("SQLite jobs table")]
    E --> F["POST /analysis/run"]
    F --> G["app.services.recommend_service.analyze_all_jobs"]
    G --> H["app.agents.job_analyst.analyze_job_text"]
    H --> I[("SQLite job_analysis table")]
    I --> J["POST /recommendations/run"]
    J --> K["RecommendationScorer"]
    K --> L["RecommendationBuilder"]
    L --> M["Streamlit or Next.js client"]
```

The API can also receive jobs directly through `POST /jobs/`, which calls `create_job()` instead of the crawler script.

## Main Data Flow

1. `fetch_greenhouse_jobs()` requests Greenhouse jobs with `content=true` and keeps titles matching engineering-related keywords.
2. `scripts/fetch_greenhouse_jobs.py` converts each item into a `JobCreate` payload.
3. `upsert_job()` stores a new row or updates an existing row by URL and content hash.
4. `POST /analysis/run` selects active or updated jobs that have no current analysis.
5. `analyze_job_text()` asks the selected OpenAI-compatible provider for structured JSON. The Azure runtime currently selects NVIDIA through the application default.
6. If a configured model call or JSON parsing fails, `analyze_job_text_rule_based()` returns a simpler deterministic analysis. Missing provider configuration fails before that fallback block.
7. `AnalysisRepository.save_analysis()` writes `JobAnalysis`, sets `last_analyzed_at`, and restores updated jobs to `ACTIVE`.
8. `POST /recommendations/run` loads analyzed jobs, builds `RecommendationContext`, scores each job, and returns sorted recommendation dictionaries.

## API, Service, Repository, Domain Flow

```text
app/api/routes_recommendations.py
  -> app/services/recommend_service.py
  -> app/repository/recommendation_repository.py
  -> app/domain/recommendation_models.py
  -> app/scoring/recommendation_scorer.py
  -> app/recommendation/recommendation_builder.py
```

Routes stay thin and mainly handle request models and dependency injection. Services own workflow decisions. Repositories isolate SQLAlchemy queries and persistence. Domain dataclasses carry scoring inputs and outputs. The scorer owns ranking policy. The builder converts internal scoring results into API response dictionaries.

## Raw Job vs Job Analysis

`Job` stores source data and lifecycle metadata:

- source, title, company, location, URL
- raw description text
- content hash
- status, first/last seen timestamps, last analyzed timestamp

`JobAnalysis` stores derived fields:

- role
- tech stack
- experience level
- language requirement
- visa sponsorship
- summary

The separation makes re-analysis possible without losing the original posting. When `upsert_job()` detects changed content for the same URL, it marks the job as `UPDATED`, clears `last_analyzed_at`, and deletes the existing analysis row so the next analysis batch creates a fresh derived result.

## LLM vs Deterministic Scoring

The LLM is responsible for extraction only. `app/agents/job_analyst.py` asks for structured fields from unstructured job text.

Scoring is deterministic. `RecommendationScorer.score()` calculates:

```text
skill_score + language_bonus + visa_bonus + location_bonus
```

and caps the result at `100`. This keeps recommendation ranking independent from model wording variance after extraction.

## Job Registration, Change Detection, and Re-analysis

`create_job()` inserts a job directly and commits immediately. `upsert_job()` supports crawler-style repeated ingestion:

- New URL: insert as `ACTIVE`.
- Same URL and same content hash: update `last_seen_at`; reactivate if it was `CLOSED`.
- Same URL and changed content hash: update fields, mark `UPDATED`, set `last_analyzed_at` to `None`, delete stale `JobAnalysis`.

`AnalysisRepository.get_jobs_without_analysis()` selects `ACTIVE` or `UPDATED` jobs when analysis is missing, the job is updated, or `last_analyzed_at` is empty.

## Transaction and Commit Responsibility

The current code commits inside repository/service functions:

- `create_job()` commits job inserts.
- `upsert_job()` commits created, unchanged, and updated paths.
- `AnalysisRepository.save_analysis()` commits analysis writes and job status changes.

`analyze_all_jobs()` rolls back and re-raises if a job analysis write fails. There is no external unit-of-work abstraction yet.

## External API Failure Behavior

Greenhouse requests use `requests.get(..., timeout=15)` and `raise_for_status()`. Callers should expect network and HTTP exceptions.

Model-call, response-parsing, and JSON-decoding failures are contained inside
`analyze_job_text()` and trigger `analyze_job_text_rule_based()`. Provider
configuration is built before that exception handler, so a missing credential
raises a configuration error rather than entering the fallback. The fallback
summary includes the exception type for failures that occur inside the handled
model-call block.

## Azure Runtime Security

The Phase 2 Azure deployment uses a dedicated Key Vault, a Container App
system-assigned managed identity, Azure RBAC, and a Container Apps Key Vault
secret reference. The runtime path is:

```text
Key Vault nvidia-api-key
  -> Container App system identity with Key Vault Secrets User
  -> Container Apps Key Vault-backed secret nvidia-api-key
  -> NVIDIA_API_KEY environment secretRef
  -> existing app/config.py environment-variable contract
```

The GitHub OIDC deployment identity, Container Apps Environment ACR-pull
identity, and Container App runtime identity remain separate. The implemented
design and evidence are documented in
[`phase2-security-architecture.md`](phase2-security-architecture.md) and
[`phase2-runtime-evidence.md`](phase2-runtime-evidence.md).

## Azure Runtime Observability

Phase 3 adds one workspace-based Application Insights resource linked to the
existing Log Analytics workspace. `app/telemetry.py` initializes the Azure
Monitor OpenTelemetry distribution before FastAPI is imported when
`APPLICATIONINSIGHTS_CONNECTION_STRING` is present. Requests, result codes,
durations, exceptions, correlation, and automatically available dependencies
are collected without route- or business-layer telemetry calls.

The final verified runtime is revision `ca-ai-jobscout-dev--0000011`, using
image `phase3-observability-20260719-01`. The architecture decision and runtime
proof are documented in
[`phase3-observability-architecture.md`](phase3-observability-architecture.md)
and [`phase3-runtime-evidence.md`](phase3-runtime-evidence.md).

## Clients

The Docker Compose dashboard is Streamlit at `frontend/dashboard.py`. It calls the local FastAPI API and provides tabs for recommendations, stored jobs, and analysis results.

The Next.js app under `web/` is an additional client. It fetches jobs and runs recommendations through `web/src/lib/api.ts`. It is not started by Docker Compose.

## Current Limitations

- SQLite is configured as a local repository-root `jobs.db` file.
- `Base.metadata.create_all()` is used instead of migrations.
- There is no authentication or authorization.
- There is no background worker; analysis runs synchronously through the API request.
- Streamlit and Next.js behavior is not covered by automated tests.
- Greenhouse API failures and successful OpenAI response shape variations are not fully covered by current tests.
- Older similarity-oriented helper modules exist, but the active `/recommendations/run` route uses `RecommendationScorer`.

## Future Production Work

Before using this beyond local/demo scope, the project would still need
migrations, managed database configuration, authentication, broader CI checks,
backup/restore procedures, and a clear runbook for external API failures.
Deployment automation, Azure runtime secret management, and essential request
observability are implemented; meaningful live secret rotation remains
deferred until a distinct replacement credential exists.

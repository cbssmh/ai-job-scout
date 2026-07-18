# Operations

This document describes local and Docker Compose operations plus the current
Azure runtime security boundary. Detailed Azure deployment evidence remains in
the Phase 1 and Phase 2 records.

## Local Backend

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

FastAPI docs:

```text
http://localhost:8000/docs
```

## Docker Compose

Validate the compose file:

```bash
docker compose config
```

Start the API and Streamlit dashboard:

```bash
docker compose up --build -d
```

Services:

- API: `http://localhost:8000`
- Streamlit dashboard: `http://localhost:8501`

Stop services:

```bash
docker compose down
```

## Environment Variables

The current `.env.example` documents both supported providers and uses only
non-working placeholders. Local development loads an ignored `.env` through
`python-dotenv` and Docker Compose:

```env
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=z-ai/glm-5.2
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Never commit the local `.env` or copy it into Azure. The Azure runtime obtains
the NVIDIA credential through Key Vault and managed identity instead.

The Next.js client can optionally use:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Health Endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/db
```

Expected healthy responses:

```json
{"status":"ok","service":"ai-job-scout-api"}
```

```json
{"status":"ok","database":"connected"}
```

The root `/` endpoint only returns a service message.

## Database

The backend uses SQLite:

```text
jobs.db
```

`app/db/database.py` builds the URL as:

```text
sqlite:///jobs.db
```

relative to the repository root. Tables are created at app startup through `Base.metadata.create_all(bind=engine)`. There are no Alembic migrations in the current project.

## Tests

```bash
pytest -q
```

If the shell cannot find `pytest`:

```bash
.venv/bin/pytest -q
```

Current tests cover health endpoints, scoring, recommendation building, location parsing, job update/re-analysis lifecycle, LLM fallback behavior with fake clients, and a service-level backend workflow from job storage through response schema validation.

## Continuous Integration

GitHub Actions is configured in `.github/workflows/test.yml`.

Triggers:

- pull requests
- pushes to `main`

Commands:

```bash
python -m pip install -r requirements.txt
pytest -q
docker compose config
```

The workflow does not require API secrets because tests use fake or monkeypatched LLM clients and do not call OpenAI.

## LLM Provider Setting

The application supports `nvidia` and `openai` through the OpenAI-compatible
client. Current defaults are defined in `app/config.py`; provider credentials
remain environment variables at the application boundary.

For Azure, `NVIDIA_API_KEY` is mapped to the Container Apps secret
`nvidia-api-key`, which is backed by a versionless Key Vault reference and the
Container App system identity. No local `.env` file is used by Azure.

For local development, set the selected provider and corresponding credential
in the ignored `.env`. For example, NVIDIA uses:

```text
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=<local credential>
```

## LLM Fallback Behavior

`analyze_job_text()` catches exceptions from the configured model call and JSON
parsing. On failure inside that block it calls `analyze_job_text_rule_based()`,
which extracts a limited set of role, technology, experience, language, and
visa signals with string matching. Missing provider configuration is validated
before the fallback block and therefore surfaces as a configuration error.

The fallback summary includes the exception type:

```text
LLM fallback reason: <ExceptionType>
```

## Common Checks

API does not start:

```bash
.venv/bin/python -m pip show fastapi uvicorn
.venv/bin/python -c "from app.main import app; print(app.title)"
```

Database health fails:

```bash
ls -l jobs.db
curl http://localhost:8000/health/db
```

Docker dashboard waits for API:

```bash
docker compose ps
docker compose logs -f api
docker compose logs -f dashboard
```

Recommendation results are empty:

```bash
curl http://localhost:8000/jobs/
curl http://localhost:8000/analysis/
```

Jobs must have analysis rows before `/recommendations/run` can return ranked results.

## Logs

Local API logs are written to standard output by Uvicorn and Python logging. The logging format is configured in `app/logging_config.py`:

```text
timestamp level [logger] message
```

Docker logs:

```bash
docker compose logs -f api
docker compose logs -f dashboard
```

Never log environment-variable values, authorization headers, Key Vault secret
values, partial credentials, encoded values, or credential hashes.

## Azure Runtime Security

Current verified Azure runtime:

- Container App revision `ca-ai-jobscout-dev--0000011`
- Active, Healthy, Provisioned; one replica
- 100% traffic on revision `0000011`
- HTTPS `/health` returns HTTP 200 with the unchanged response
- Container App system identity reads `kv-ai-jobscout-dev` through `Key Vault
  Secrets User`
- `NVIDIA_API_KEY` references the Key Vault-backed Container Apps secret
  `nvidia-api-key`
- GitHub OIDC deployment, environment ACR pull, and runtime secret read use
  separate identities

Use the [Phase 2 Secret Rotation
Runbook](phase2-secret-rotation-runbook.md) for a real credential change. Live
rotation has not yet been tested and requires a distinct valid replacement
credential.

## Azure Runtime Observability

Application telemetry is stored through `appi-ai-jobscout-dev` in the existing
Log Analytics workspace `workspacergaijobscoutdeva4e1`. The final Container App
template contains the `APPLICATIONINSIGHTS_CONNECTION_STRING` setting, but its
value must never be printed, copied into documentation, or committed.

Use workspace queries for operational investigation:

```kusto
AppRequests
| where TimeGenerated >= ago(30m)
| project TimeGenerated, Name, ResultCode, DurationMs, Success, OperationId, Id
| order by TimeGenerated desc
```

```kusto
AppExceptions
| where TimeGenerated >= ago(30m)
| project TimeGenerated, ExceptionType, OuterMessage, OperationId, ParentId
| order by TimeGenerated desc
```

Join an exception to a request by matching `OperationId`; the exception
`ParentId` should identify the originating request `Id`. Public HTTPS protocol
and response-body verification remain separate because Application Insights
records the internal ingress-to-container URL scheme.

See [Phase 3 Runtime Evidence](phase3-runtime-evidence.md) for reproducible CLI
queries and validated examples. No alert or dashboard is part of the Phase 3
operating model.

## Data Reset

For local development only, stop the app and remove the SQLite file:

```bash
rm jobs.db
```

Then recreate data by inserting jobs through the API, running the seed script, or fetching jobs:

```bash
python scripts/seed_jobs.py
python scripts/fetch_greenhouse_jobs.py
```

Do not use this reset approach for a real shared database.

## Current Operating Scope

The repository supports local development, Docker Compose demonstration, CI,
automated Azure deployment, and Azure-native runtime secret management. It does
not include user authentication, a managed database, backup/restore automation,
or alerting. Essential Azure request observability is implemented through
Application Insights. Phase 2 live rotation remains deferred; Phase 3 is PASS.

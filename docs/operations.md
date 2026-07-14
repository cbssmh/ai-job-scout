# Operations

This document describes the current local and Docker Compose operating model. It does not describe a cloud production deployment.

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

The current `.env.example` contains:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

`app/config.py` loads `.env` with `python-dotenv` and exposes `settings.openai_api_key`.

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

`app/agents/job_analyst.py` uses:

```text
model="gpt-4.1-mini"
```

through the OpenAI Python client. Set `OPENAI_API_KEY` for LLM-backed analysis. The project does not currently expose model selection as an environment variable.

## LLM Fallback Behavior

`analyze_job_text()` catches exceptions from the OpenAI call and JSON parsing. On failure it calls `analyze_job_text_rule_based()`, which extracts a limited set of role, technology, experience, language, and visa signals with string matching.

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

The current repository supports local development, Docker Compose demonstration, and minimal CI validation. It does not include production deployment automation, authentication, managed database configuration, backup/restore automation, external monitoring, or alerting.

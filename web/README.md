# AI Job Scout Next.js Client

This directory contains an additional React/Next.js client for the FastAPI backend. It is separate from the Streamlit dashboard used by Docker Compose.

## Role

- Fetch stored jobs from `GET /jobs/`
- Run recommendations through `POST /recommendations/run`
- Display recommendation score components and stored job cards

The backend API is the source of truth for analysis and scoring behavior.

## Run Locally

Start the FastAPI backend from the repository root:

```bash
uvicorn app.main:app --reload
```

Then start the Next.js client:

```bash
cd web
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

Optional API base URL:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

# AI Job Scout Agent

AI-powered job intelligence system that collects real-world job postings, analyzes hiring signals using an automated AI pipeline, and ranks personalized job recommendations.

This project demonstrates a data pipeline combining web crawling, AI-based information extraction, and explainable recommendation scoring.

---

# Project Overview

The system automatically:

- Crawls job postings from public recruiting platforms
- Stores raw job descriptions in a database
- Extracts structured hiring signals
- Computes personalized job match scores
- Returns ranked recommendations through an API and dashboard

## Pipeline

```
Job Crawling
      ↓
Raw Job Storage
      ↓
AI Job Analysis
      ↓
Skill Matching
      ↓
Recommendation Ranking
      ↓
API Response
      ↓
Interactive Dashboard
```

---

# Key Features

- Real-world job posting crawler
- AI-powered job description analysis
- Tech stack and experience extraction
- Skill-based recommendation engine
- Explainable scoring system
- REST API built with FastAPI
- Interactive Streamlit dashboard
- Docker-based deployment

---

# Real Data Processing

The crawler collects live job postings from public recruiting platforms.

Example result:

```
526 job postings collected from Stripe's Greenhouse board
Batch analysis applied across all collected postings
AI-powered recommendation scores generated
```

This enables testing the pipeline on real-world hiring data.

---

# System Architecture

```
             Job Boards
                 │
                 ▼
          Web Crawler Layer
                 │
                 ▼
         Job Storage (SQLite)
                 │
                 ▼
          AI Analysis Pipeline
          ├─ Job Analyst
          ├─ Skill Matcher
          └─ Rule-based Fallback
                 │
                 ▼
        Recommendation Engine
                 │
                 ▼
            FastAPI API
                 │
                 ▼
        Streamlit Dashboard
```

---

# API Endpoints

## Get Stored Jobs

`GET /jobs/`

Returns stored job postings.

Example:

```json
{
  "title": "Backend Engineer",
  "company": "Stripe",
  "location": "Remote"
}
```

---

## Run Job Analysis

`POST /analysis/run`

Runs AI analysis on stored job postings.

Extracted signals include:

- role
- tech stack
- experience level
- language requirement
- visa sponsorship hints

Example:

```json
{
  "role": "Backend Engineer",
  "tech_stack": "python, fastapi, docker, aws",
  "experience_level": "3+ years"
}
```

---

## Get Analysis Results

`GET /analysis/`

Returns stored analysis results.

---

## Get Recommendations

`POST /recommendations/run`

Generates job recommendations based on user profile.

Example request:

```json
{
  "skills": ["Python", "FastAPI", "Docker", "AWS"],
  "preferred_countries": ["Germany"],
  "visa_needed": true
}
```

Example response:

```json
{
  "title": "Backend Engineer",
  "skill_score": 100,
  "language_bonus": 10,
  "visa_bonus": 10,
  "match_score": 100
}
```

---

# Recommendation Logic

Recommendation score is calculated using:

```
match_score =
    skill_score
  + language_bonus
  + visa_bonus
  + location_bonus
```

Where:

- `skill_score` = overlap between user skills and job tech stack
- `language_bonus` = English work environment detected
- `visa_bonus` = visa sponsorship hints detected
- `location_bonus` = preferred country match

Maximum score = **100**

---

# AI Analysis Strategy

The system uses a hybrid extraction approach.

## Primary

LLM-based structured extraction.

## Fallback

Rule-based parser when:

- API rate limits occur
- invalid responses occur
- LLM errors occur

This ensures the pipeline remains robust and fault tolerant.

Example fallback:

```
Rule-based fallback: role=Backend Engineer, tech=python, aws
```

---

# Dashboard

A lightweight Streamlit dashboard allows interactive exploration of:

- stored job postings
- analysis results
- personalized recommendations

Dashboard features:

- skill-based recommendation input
- job filtering and search
- direct links to original job postings
- analysis coverage metrics

Run with:

```
streamlit run frontend/dashboard.py
```

---

# Docker Deployment

The entire system can be launched using Docker Compose.

```
docker compose up --build
```

Services:

- FastAPI API → http://localhost:8000/docs
- Streamlit Dashboard → http://localhost:8501

---

# Installation (Local)

Clone repository:

```
git clone https://github.com/yourname/ai-job-scout.git
cd ai-job-scout
```

Create virtual environment:

```
python -m venv venv
```

Activate environment:

Windows:

```
venv\Scripts\activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

# Environment Variables

Create `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

---

# Running the Project

Insert sample jobs (optional):

```
python -m scripts.seed_jobs
```

Fetch real job postings:

```
python -m scripts.fetch_greenhouse_jobs
```

Start API:

```
uvicorn app.main:app --reload
```

Start dashboard:

```
streamlit run frontend/dashboard.py
```

---

# Project Structure

```
ai-job-scout

app
 ├─ agents
 ├─ crawler
 ├─ api
 ├─ db
 ├─ services
 └─ main.py

frontend
 └─ dashboard.py

scripts
 ├─ seed_jobs.py
 └─ fetch_greenhouse_jobs.py

Dockerfile
docker-compose.yml
requirements.txt
README.md
```

---

# Future Improvements

Possible extensions:

- multi-agent job analysis system
- salary prediction
- automated job application system
- email or Telegram notifications
- job market trend analysis
- improved ranking model

---

# Learning Outcomes

This project demonstrates:

- API design with FastAPI
- database modeling with SQLAlchemy
- web crawling pipelines
- LLM-assisted information extraction
- fault-tolerant AI system design
- explainable recommendation systems
- containerized deployment with Docker

---

# License

MIT License
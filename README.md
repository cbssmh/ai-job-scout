# AI Job Scout Agent

AI-powered job intelligence system that collects real-world job postings, analyzes hiring signals using an automated AI pipeline, and ranks personalized job recommendations.

This project demonstrates a production-style data pipeline combining web crawling, LLM-assisted information extraction, and explainable recommendation scoring.

---

# Demo

## API Documentation
http://localhost:8000/docs

## Dashboard
http://localhost:8501

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
- Fault-tolerant AI analysis pipeline

---

# Project Overview

The system automatically:

1. Crawls job postings from recruiting platforms  
2. Stores raw job descriptions in a database  
3. Extracts structured hiring signals using AI  
4. Computes personalized job match scores  
5. Returns ranked recommendations through an API and dashboard  

---

# Pipeline

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

# Real Data Processing

The crawler collects live job postings from public recruiting platforms.

Example run:

- 526 job postings collected from Stripe's Greenhouse board
- Batch analysis applied across all collected postings
- AI-powered recommendation scores generated

This allows the system to operate on real-world hiring data instead of synthetic datasets.

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

Example recommendation result:

```
Backend Engineer - Stripe

skill_score: 100
language_bonus: 10
visa_bonus: 10
match_score: 100
```

---

# AI Analysis Strategy

The system uses a **hybrid extraction approach**.

## Primary
LLM-based structured extraction.

## Fallback
Rule-based parser when:

- API rate limits occur
- invalid responses occur
- LLM errors occur

Example fallback output:

```
Rule-based fallback:
role = Backend Engineer
tech = python, aws
```

This ensures the pipeline remains robust and fault tolerant.

---

# API Endpoints

## Get Stored Jobs

```
GET /jobs/
```

Example response:

```json
{
  "title": "Backend Engineer",
  "company": "Stripe",
  "location": "Remote"
}
```

---

## Run Job Analysis

```
POST /analysis/run
```

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

```
GET /analysis/
```

Returns stored analysis results.

---

## Get Recommendations

```
POST /recommendations/run
```

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

# Dashboard

A lightweight **Streamlit dashboard** enables interactive exploration of:

- stored job postings
- analysis results
- personalized recommendations

Features:

- skill-based recommendation input
- job filtering and search
- direct links to original job postings
- analysis coverage metrics

Run with:

```
streamlit run frontend/dashboard.py
```

---

# Tech Stack

## Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite

## AI
- OpenAI API
- LLM structured extraction

## Frontend
- Streamlit

## Infrastructure
- Docker
- Docker Compose

---

# Installation

## Clone repository

```bash
git clone https://github.com/yourname/ai-job-scout.git
cd ai-job-scout
```

## Create virtual environment

```bash
python -m venv venv
```

## Activate environment

### Windows
```bash
venv\Scripts\activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create `.env`

```
OPENAI_API_KEY=your_api_key_here
```

---

# Running the Project

## Insert sample jobs (optional)

```bash
python -m scripts.seed_jobs
```

## Fetch real job postings

```bash
python -m scripts.fetch_greenhouse_jobs
```

## Start API

```bash
uvicorn app.main:app --reload
```

## Start dashboard

```bash
streamlit run frontend/dashboard.py
```

---

# Docker Deployment

```bash
docker compose up --build
```

Services

API  
http://localhost:8000/docs

Dashboard  
http://localhost:8501

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

---

# Author

GitHub  
https://github.com/cbssmh

---

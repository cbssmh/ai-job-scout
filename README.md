# AI Job Scout Agent

AI-powered job intelligence system that collects real-world job postings, analyzes hiring signals using an automated AI pipeline, and delivers **explainable, personalized job recommendations** through a modern dashboard.

This project demonstrates a **production-style AI pipeline + full-stack architecture**, combining web crawling, LLM-assisted extraction, and a React-based dashboard.

---

# 🚀 Demo

## API Documentation

http://localhost:8000/docs

## Next.js Dashboard

http://localhost:3000

---

# ✨ Key Features

* Real-world job posting crawler
* AI-powered job description analysis (LLM + fallback)
* Structured hiring signal extraction
* Skill-based recommendation engine
* Explainable scoring system
* FastAPI REST API
* **Next.js dashboard (Stitch-inspired UI)**
* Docker-based deployment
* Fault-tolerant AI pipeline

---

# 🧠 Project Overview

The system automatically:

1. Crawls real job postings
2. Stores raw job data
3. Extracts structured signals via AI
4. Computes personalized match scores
5. Displays ranked recommendations in a modern UI

---

# ⚙️ Architecture

```
Job Boards
   ↓
Crawler Layer
   ↓
SQLite Database
   ↓
AI Analysis Pipeline
   ↓
Recommendation Engine
   ↓
FastAPI API
   ↓
Next.js Dashboard
```

---

# 🧮 Recommendation Logic

```
match_score =
    skill_score
  + language_bonus
  + visa_bonus
  + location_bonus
```

* Skill match → core score
* Language → English environment bonus
* Visa → sponsorship signal
* Location → user preference match

Max score = **100**

---

# 🤖 AI Analysis Strategy

Hybrid approach:

## Primary

* LLM-based structured extraction

## Fallback

* Rule-based parser

Ensures robustness under:

* API rate limits
* invalid responses
* model failures

---

# 🔌 API Endpoints

## Get Jobs

```
GET /jobs/
```

## Run Analysis

```
POST /analysis/run
```

## Get Analysis Results

```
GET /analysis/
```

## Run Recommendations

```
POST /recommendations/run
```

---

# 🖥️ Dashboard (Next.js)

Modern dashboard built with:

* Next.js
* React
* Tailwind CSS
* Stitch-inspired UI design

Features:

* Real-time recommendation execution
* Match score visualization
* KPI metrics (avg score, top matches)
* Skill-based filtering
* Explainable scoring breakdown

---

# 🧱 Tech Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite

## AI

* OpenAI API
* LLM structured extraction

## Frontend

* Next.js
* React
* Tailwind CSS

## Infra

* Docker
* Docker Compose

---

# ⚙️ Installation

```bash
git clone https://github.com/cbssmh/ai-job-scout.git
cd ai-job-scout
```

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

```
OPENAI_API_KEY=your_api_key_here
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

# ▶️ Run

## Backend

```bash
uvicorn app.main:app --reload
```

## Frontend

```bash
cd web
npm install
npm run dev
```

---

# 🐳 Docker

```bash
docker compose up --build
```

---

# 📁 Structure

```
app/
web/
scripts/
Dockerfile
docker-compose.yml
```

---

# 🚀 Future Improvements

* search & filtering UI
* job detail page
* real-time alerts
* ranking model upgrade
* multi-agent analysis

---

# 🎯 What This Project Shows

* AI pipeline design
* LLM + rule-based hybrid system
* real-world data processing
* full-stack integration
* explainable recommendation system
* production-style architecture

---

# 📌 Author

https://github.com/cbssmh

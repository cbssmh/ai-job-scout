# 🤖 AI Job Scout Agent

AI-powered job intelligence system that transforms raw job postings into structured hiring signals and delivers **explainable, personalized, data-driven recommendations**.

This project is not only about implementing features, but also about designing a maintainable recommendation system through **refactoring, modular architecture, and explainable scoring**.

---

# 🚀 Demo

## API Documentation
http://localhost:8000/docs

## Next.js Dashboard
http://localhost:3000

---

# 🎯 Motivation

Most job platforms simply list openings.  
This project focuses on helping users discover better-fit opportunities through:

- structured job analysis
- personalized recommendation logic
- transparent score breakdown
- maintainable backend architecture

The goal was to build not just a crawler, but a **job intelligence system** that can turn messy job descriptions into explainable recommendation results.

---

# ✨ Key Features

- Real-world job posting crawler
- AI-powered job description analysis (LLM + fallback parser)
- Structured hiring signal extraction
- Skill-based recommendation engine
- Explainable scoring system
- FastAPI REST API
- Next.js dashboard (Stitch-inspired UI)
- Docker-based local deployment
- Fault-tolerant AI analysis pipeline

---

# 🧠 Project Overview

The system automatically:

1. Crawls real-world job postings
2. Stores raw job data
3. Extracts structured hiring signals
4. Computes personalized match scores
5. Ranks jobs based on recommendation logic
6. Displays explainable results through API and dashboard

---

# 🔄 Data Flow

This project was designed around a clear data flow from raw input to explainable output.

## Detailed Flow

1. **Crawl job postings** from external job boards
2. **Store raw posting data** in the database
3. **Run AI analysis** to extract structured fields
4. **Normalize extracted signals** for scoring
5. **Engineer recommendation features**
6. **Compute weighted match scores**
7. **Rank and format results**
8. **Expose explainable recommendations** via API and dashboard

## Data Pipeline

```text
Job Boards
   ↓
Crawler Layer
   ↓
Raw Job Storage
   ↓
AI Analysis Pipeline
   ↓
Structured Hiring Signals
   ↓
Feature Engineering
   ↓
Recommendation Scoring
   ↓
Ranking / Response Builder
   ↓
FastAPI API
   ↓
Next.js Dashboard
```

---

# ⚙️ System Architecture

## High-Level Architecture

```text
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

## Layered Responsibilities

- **Repository** → database access and query abstraction  
- **Processing** → parsing, normalization, structured transformation  
- **Scoring** → recommendation score calculation  
- **Recommendation** → response construction and ranking output  

---

# 🧱 Architecture Upgrade (Refactoring)

## Problem

Initially, recommendation logic was implemented inside a single service function.

That function handled:

- database queries
- skill matching
- bonus calculation
- response building
- sorting

### Issues

- large change impact when modifying scoring rules  
- low testability of internal logic  
- tight coupling between responsibilities  
- poor extensibility for future features  

---

## Before

```text
get_recommendations()
├─ DB query
├─ skill matching
├─ bonus calculation
├─ response creation
└─ sorting
```

All logic was tightly coupled inside one service-level flow.

---

## After

```text
service
├─ repository
├─ scorer
├─ builder
```

Each responsibility is isolated and replaceable.

---

## Refactoring Result

The recommendation flow was transformed from a function-driven implementation into a structure-driven architecture.

### Improvements

- separation of concerns  
- testability  
- change isolation  
- maintainability  
- future extensibility  

---

# ✅ Key Engineering Improvements

## 1. Separation of Concerns

Recommendation logic was split into dedicated modules:

- data access  
- preprocessing  
- scoring  
- result building  

---

## 2. Testability

Core modules can now be tested independently:

- LocationParser  
- RecommendationScorer  
- RecommendationBuilder  

---

## 3. Reduced Change Impact

### Before
modify scoring → edit entire service  

### After
modify scoring → edit only scorer module  

---

## 4. Maintainability

Service layer now acts as an orchestrator:

```text
service → repository → scorer → builder
```

---

## 5. Explainability

The system provides:

- total match score  
- component-level score breakdown  
- matched skills  
- reason-aware ranking  

---

# 🧮 Recommendation Logic

```text
match_score =
  skill_score
+ language_bonus
+ visa_bonus
+ location_bonus
```

## Scoring Components

- Skill Score → core relevance between user skills and job requirements  
- Language Bonus → language-friendly environment  
- Visa Bonus → sponsorship or authorization signal  
- Location Bonus → preferred location match  

**Max score = 100**

---

# 🧾 Example Recommendation Output

```json
{
  "job_id": 123,
  "company": "Example Tech",
  "position": "Backend Developer",
  "score": 87,
  "breakdown": {
    "skill_score": 60,
    "language_bonus": 10,
    "visa_bonus": 10,
    "location_bonus": 7
  },
  "matched_skills": ["Python", "FastAPI", "SQL"],
  "reason": "Strong backend skill match with favorable language and visa conditions."
}
```

---

# 🤖 AI Analysis Strategy

## Primary Strategy
- LLM-based structured extraction  

## Fallback Strategy
- Rule-based parser  

## Why This Design

- handles API rate limits  
- recovers from invalid responses  
- ensures robustness  

---

# ⚡ Backend-Focused Design Decisions

## Focus Areas

- modular service orchestration  
- isolated scoring policy  
- fault-tolerant AI pipeline  
- explainable output generation  
- maintainable data flow  

---

# 📊 Performance & Metrics

```text
Crawled jobs: N
Average AI analysis time per job: N sec
Recommendation latency: N ms
Fallback success rate: N%
Duplicate filtering accuracy: N%
```

---

# 🔌 API Endpoints

```http
GET    /jobs/
POST   /analysis/run
GET    /analysis/
POST   /recommendations/run
```

---

# 🖥️ Dashboard (Next.js)

## Built With

- Next.js  
- React  
- Tailwind CSS  

## Features

- real-time recommendation execution  
- score visualization  
- KPI metrics  
- skill-based filtering  
- explainable breakdown  

---

# 🧪 Testing

## Covered Modules

- LocationParser  
- RecommendationScorer  
- RecommendationBuilder  

## Run Tests

```bash
pytest -v
```

---

# 🧱 Tech Stack

## Backend
- Python  
- FastAPI  
- SQLAlchemy  
- SQLite  

## AI
- OpenAI API  
- LLM-based extraction  

## Frontend
- Next.js  
- React  
- Tailwind CSS  

## Infra
- Docker  
- Docker Compose  

---

# 📁 Project Structure

```text
app/
├─ api/
├─ core/
├─ models/
├─ repositories/
├─ services/
├─ scorers/
├─ builders/
├─ parsers/
└─ main.py

web/
tests/
scripts/
Dockerfile
docker-compose.yml
```

---

# ⚙️ Installation

```bash
git clone https://github.com/cbssmh/ai-job-scout.git
cd ai-job-scout

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

---

# 🔐 Environment Variables

```env
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

# 🧠 Engineering Decisions

## Why Refactor?

- reduce coupling  
- isolate change points  
- improve testability  
- enable explainable scoring  

## Key Design

- **Scoring** → evaluation logic  
- **Recommendation** → output logic  

---

# 🚀 Future Improvements

- advanced search UI  
- job detail page  
- real-time alerts  
- embedding-based search  
- ANN optimization  
- multi-agent pipeline  
- PostgreSQL migration  
- async queue processing  

---

# 📌 Author

GitHub: https://github.com/cbssmh

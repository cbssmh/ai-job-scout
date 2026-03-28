# 🤖 AI Job Scout Agent

AI-powered job intelligence system that collects real-world job postings, analyzes hiring signals using an automated AI pipeline, and delivers **explainable, personalized job recommendations**.

This project focuses not only on feature implementation, but also on **system design, refactoring, and maintainable architecture**.

---

# 🚀 Demo

## API Documentation
http://localhost:8000/docs

## Next.js Dashboard
http://localhost:3000

---

# ✨ Key Features

- Real-world job posting crawler
- AI-powered job description analysis (LLM + fallback)
- Structured hiring signal extraction
- Skill-based recommendation engine
- Explainable scoring system
- FastAPI REST API
- **Next.js dashboard (Stitch-inspired UI)**
- Docker-based deployment
- Fault-tolerant AI pipeline

---

# 🧠 Project Overview

The system automatically:

1. Crawls real job postings  
2. Stores raw job data  
3. Extracts structured signals via AI  
4. Computes personalized match scores  
5. Displays ranked recommendations  

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

# 🧱 Architecture Upgrade (Refactoring)

## Problem

Initially, the recommendation logic was implemented in a single service layer:

- data fetching
- skill matching
- bonus calculation
- response building

This caused:

- large change impact when modifying scoring logic  
- difficulty in testing individual components  
- tight coupling between business logic  
- limited scalability  

---

## Solution

Refactored the recommendation system into layered architecture:

```
Repository → Processing → Scoring → Recommendation
```

### Responsibilities

- **Repository** → database access  
- **Processing** → data normalization & parsing  
- **Scoring** → match score calculation  
- **Recommendation** → response construction  

---

## Before vs After

### ❌ Before

```
get_recommendations()
├─ DB query
├─ skill matching
├─ bonus calculation
├─ response creation
└─ sorting
```

👉 All logic tightly coupled in one function

---

### ✅ After

```
service
├─ repository
├─ scorer
├─ builder
```

👉 Each responsibility isolated and replaceable

---

## Key Improvements

### 1. Separation of Concerns

- scoring logic isolated from service layer  
- response building separated from business logic  

---

### 2. Testability

Core modules are independently testable:

- `LocationParser`
- `RecommendationScorer`
- `RecommendationBuilder`

---

### 3. Reduced Change Impact

Before:

```
modify scoring → edit entire service
```

After:

```
modify scoring → edit only scorer module
```

---

### 4. Maintainability

The service layer now acts as an orchestrator:

```
service → repository → scorer → builder
```

---

## Result

This refactoring transformed the system from:

> function-driven implementation

to:

> structure-driven architecture

---

# 🧮 Recommendation Logic

```
match_score =
  skill_score
+ language_bonus
+ visa_bonus
+ location_bonus
```

- Skill match → core score  
- Language → English environment bonus  
- Visa → sponsorship signal  
- Location → user preference  

Max score = **100**

---

# 🤖 AI Analysis Strategy

Hybrid approach:

## Primary
- LLM-based structured extraction

## Fallback
- Rule-based parser

Ensures robustness under:

- API rate limits  
- invalid responses  
- model failures  

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

Built with:

- Next.js
- React
- Tailwind CSS

Features:

- real-time recommendation execution  
- match score visualization  
- KPI metrics (avg score, top matches)  
- skill-based filtering  
- explainable scoring breakdown  

---

# 🧪 Testing

After refactoring, core components are independently testable.

## Covered Modules

- `LocationParser`
- `RecommendationScorer`
- `RecommendationBuilder`

## Run Tests

```bash
pytest -v
```

## Why It Matters

Before:

- recommendation logic was tightly coupled  
- testing required running entire pipeline  

After:

- each component can be tested independently  
- faster debugging and safer changes  

---

# 🧱 Tech Stack

## Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite

## AI
- OpenAI API
- LLM structured extraction

## Frontend
- Next.js
- React
- Tailwind CSS

## Infra
- Docker
- Docker Compose

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
tests/
scripts/
Dockerfile
docker-compose.yml
```

---

# 🧠 Engineering Decisions

## Why refactor the recommendation system?

The goal was not to add features, but to improve system structure.

Key focus:

- reduce coupling  
- isolate change points  
- improve testability  
- make the system explainable  

---

## Key Design Decision

Separated recommendation logic into:

- Scoring (evaluation)
- Recommendation (selection & presentation)

This allows:

- flexible policy changes  
- clear reasoning for recommendations  
- independent testing  

---

## Takeaway

This project demonstrates not only feature implementation, but:

> the ability to identify structural problems and refactor toward a scalable architecture

---

# 🚀 Future Improvements

- search & filtering UI  
- job detail page  
- real-time alerts  
- ranking model upgrade (ML-based)  
- embedding-based similarity search  
- multi-agent analysis pipeline  

---

# 📌 Author

https://github.com/cbssmh
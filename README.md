# 🩺 CareLoop

<p align="center">
AI-powered caregiver burnout detection and wellness companion
</p>

<p align="center">
Built for the <b>AMD Developer Challenge 2026</b>
</p>

---

# 📖 Overview

CareLoop is an AI-powered web application designed to help family caregivers recognize burnout before it becomes a serious mental or physical health issue.

Caregivers often neglect their own wellbeing while caring for loved ones. CareLoop allows users to write a daily journal entry, analyzes the emotional content using Artificial Intelligence, detects burnout indicators, tracks wellbeing over time, and recommends relevant support resources.

The application is lightweight, fully containerized with Docker, and can run either with cloud AI services or an intelligent fallback scoring system.

---

# 🎯 Problem Statement

Millions of caregivers experience stress, isolation, sleep deprivation, and emotional exhaustion without realizing how serious their condition has become.

Most available solutions focus on patients rather than caregivers.

CareLoop focuses on the caregiver.

---

# 💡 Solution

CareLoop helps caregivers by

- Recording daily journal entries
- Detecting burnout symptoms using AI
- Measuring emotional wellbeing
- Tracking burnout trends
- Recommending helpful resources
- Saving journal history securely

---

# ✨ Features

- AI-powered burnout analysis
- Daily caregiver journal
- Burnout trend visualization
- Personalized emotional summary
- Support resource recommendations
- Firebase cloud storage
- Local JSON backup
- Dockerized deployment
- FastAPI REST API
- Responsive web interface

---

# 🛠 Tech Stack

## Frontend

- HTML5
- CSS3
- JavaScript

## Backend

- Python
- FastAPI

## Artificial Intelligence

- Google Gemini API
- Fireworks AI
- Rule-Based Fallback Scoring

## Database

- Firebase Realtime Database
- Local JSON Storage

## DevOps

- Docker
- Docker Compose

---

# 🏗 System Architecture

```

User
│
▼
Frontend
│
▼
FastAPI Backend
│
├── Gemini AI
├── Fireworks AI
└── Rule-Based Scoring
│
▼
Firebase Database
│
▼
Burnout Scores
Trend History
Support Resources

```

---

# 📂 Project Structure

```

CareLoop

│

├── backend
│ ├── main.py
│ ├── scorer.py
│ ├── firebase_store.py
│ ├── requirements.txt
│ ├── Dockerfile
│ ├── .env.example
│ └── data

│

├── frontend
│ ├── index.html
│ └── Dockerfile

│

├── docker-compose.yml
├── README.md
└── .gitignore

```

---

# 🔄 Workflow

1. User writes a journal entry.
2. Frontend sends the entry to the FastAPI backend.
3. Backend analyzes the text using Gemini AI.
4. If Gemini is unavailable, Fireworks AI is used.
5. If both services are unavailable, CareLoop automatically switches to the built-in rule-based scorer.
6. Scores are stored in Firebase or locally.
7. Burnout trends and personalized resources are returned to the user.

---

# 📊 Burnout Categories

CareLoop evaluates five burnout indicators.

| Category | Description |
|-----------|-------------|
| Sleep Loss | Sleep quality and fatigue |
| Isolation | Feeling lonely or unsupported |
| Resentment | Frustration or anger |
| Physical Strain | Physical tiredness or pain |
| Emotional Exhaustion | Mental fatigue and burnout |

Each category is scored from **0 to 10**.

---

# 📋 Prerequisites

Before running the project, install

- Git
- Docker Desktop
- Docker Compose
- Google Gemini API Key
- Firebase Project
- Firebase Service Account Key

---

# 🚀 Installation

## Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/CareLoop.git
cd CareLoop
```

---

## Configure Environment Variables

Inside the **backend** folder create a file named

```
.env
```

Example

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

FIREWORKS_API_KEY=

FIREWORKS_MODEL=

FIREBASE_DATABASE_URL=YOUR_FIREBASE_DATABASE_URL

FIREBASE_CREDENTIALS_PATH=/app/firebase-key.json
```

---

## Add Firebase Credentials

Download your Firebase Service Account JSON file.

Place it inside

```
backend/firebase-key.json
```

---

# 🐳 Run Using Docker

Build and start the application

```bash
docker compose up --build
```

---

# 🌐 Access the Application

Frontend

```
http://localhost:8080
```

Backend

```
http://localhost:8000
```

Health Check

```
http://localhost:8000/api/health
```

---

# 🛑 Stop the Application

```bash
docker compose down
```

---

# 🔄 Rebuild After Code Changes

```bash
docker compose down

docker compose up --build
```

---

# 💾 Storage

CareLoop stores journal entries in

- Firebase Realtime Database

If Firebase is unavailable, it automatically stores data locally using

```
backend/data/entries.json
```

This ensures uninterrupted functionality.

---

# 🤖 AI Pipeline

Priority Order

1. Google Gemini
2. Fireworks AI
3. Rule-Based Scoring Engine

The application always returns a valid result even if AI services are unavailable.

---

# 📸 Screenshots

Add screenshots here

- Home Screen
- Journal Submission
- Burnout Analysis
- Trend Dashboard
- Resource Recommendations

---

# 🎥 Demo

Demo Video

```
Add your YouTube or Loom link here
```

---

# ☁ Deployment

The application is fully containerized using Docker and can be deployed on

- AMD Developer Cloud
- Azure
- AWS
- Google Cloud
- DigitalOcean
- Any Docker-compatible server

---

# 🔮 Future Improvements

- Voice journal support
- Mobile application
- AI chatbot for caregivers
- Multi-language support
- Wearable device integration
- Weekly wellness reports
- Emergency caregiver alerts

---

# 👥 Team

## Team Kinfolk Circle

| Member | Role |
|---------|------|
| Allah Nawaz | Team Lead, Backend Development, Integration, Docker, Presentation |
| Muhammad Abdullah | AI Integration, Prompt Engineering |
| Muhammad Yameen | Frontend Development, Firebase Integration |
| Hamna Shahid | Logic Design, Testing, Quality Assurance |

---

# 🏆 Hackathon

**Competition**

AMD Developer Challenge 2026

**Track**

AI-powered Healthcare Solution

---

# 📄 License

This project is created for educational and hackathon purposes.

---

# ❤️ Thank You

Thank you for reviewing **CareLoop**.

Our goal is to empower caregivers with AI-driven insights, helping them recognize burnout early and prioritize their own wellbeing while caring for others.

We hope CareLoop contributes to healthier caregivers and stronger communities.
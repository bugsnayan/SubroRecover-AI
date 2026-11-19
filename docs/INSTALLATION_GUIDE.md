# SubroRecover AI — Installation & Setup Guide

This guide provides step-by-step instructions for installing, configuring, running, and verifying **SubroRecover AI** across Windows, macOS, and Linux.

---

## 1. System Requirements

- **Operating System:** Windows 10/11, macOS (Apple Silicon or Intel), Ubuntu 22.04+
- **Python Version:** Python 3.11, 3.12, or 3.13 (Anaconda / Miniconda / standard python venv)
- **Memory (RAM):** 8 GB minimum (16 GB recommended)
- **Disk Space:** ~2 GB for dependencies, vector store, and SQLite database
- **Database Engine:**
  - *Default:* Embedded SQLite 3.35+ (zero configuration, automatic fallback)
  - *Production:* PostgreSQL 15+ (with psycopg3 driver)

---

## 2. Quickstart Installation (5 Minutes)

### Step 1: Clone or Open Workspace
```bash
cd SubroRecover-AI
```

### Step 2: Create & Activate Virtual Environment
```bash
# Option A: Using Python standard venv
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### Step 3: Install Core Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Environment Configuration

Copy the `.env.example` template to `.env`:
```bash
cp .env.example .env
```

Default `.env` configuration (ready for immediate local execution):
```ini
APP_NAME=SubroRecover AI
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=subrorecover-dev-key-2026

# Database configuration
# Leave as sqlite for instant zero-configuration local execution:
DATABASE_URL=sqlite:///./subro_recover.db
DB_FALLBACK_TO_SQLITE=true

# Optional Google Gemini API Key for live multimodal agent reasoning.
# If omitted, SubroRecover operates in transparent deterministic local rule mode.
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash

# Networking
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=8501

# ChromaDB vector store
CHROMA_PERSIST_DIR=./chroma_db
```

---

## 4. Database & Pipeline Initialization

Initialize the database schema, generate sample data, and execute the initial ETL pipeline:

```bash
# 1. Initialize relational schema
python database/connection.py

# 2. Generate synthetic insurance claim datasets
python sample_data/generate_synthetic_data.py

# 3. Run the Data Engineering ETL Pipeline
python data_engineering/pipeline.py

# 4. Train the Random Forest prioritization model
python ml/train.py
```

---

## 5. Running the Application Services

SubroRecover AI comprises two cooperating services: the **FastAPI REST Backend** and the **Streamlit Enterprise Dashboard**.

### Terminal 1: Launch FastAPI REST Backend
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
- API Health Check: `http://127.0.0.1:8000/health`
- Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### Terminal 2: Launch Streamlit Enterprise Dashboard
```bash
streamlit run frontend/app.py --server.port 8501
```
- Web Application URL: `http://localhost:8501`

---

## 6. Running Automated Tests

Run the comprehensive pytest test suite covering all modules:
```bash
pytest -v tests
```
Expected output: **18 passed, 0 failures**.

# Zomato AI Recommendation Advisor

A sophisticated culinary recommendation engine powered by real-time Zomato dataset insights and state-of-the-art LLMs (Groq). The project features a separated **FastAPI Backend Services API** and a modern, fully-responsive **React (Vite) Frontend Interface** aligned with Zomato’s premium brand visual language.

---

## 🚀 Features

- **Grounded Recommendations**: Recommendations are generated only from verified Zomato dataset restaurant candidates (no hallucinations/fabricated restaurants).
- **Deterministic Pre-Filtering**: Applies strict candidate filters (location, cuisine, budget, rating) before contacting the LLM to improve precision and minimize token consumption.
- **Request Correlation Trace**: Full request lifecycle observability with middleware correlation ID injection.
- **Quality & Input Hardening**: Enforces input length bounds (max 500 characters) and automatically cleans and sanitizes free-text inputs.
- **Responsive Web Dashboard**: A Zomato-themed Single-Page-Application featuring skeletal loaders, rating/result sliders, custom budget selection button pills, and responsive layout grids.

---

## 📁 Repository Directory Structure

```text
├── data/
│   ├── raw/             # Raw source datasets (CSV)
│   └── processed/       # Preprocessed database (Parquet format)
├── design/              # UI mockups and layout requirements
├── docs/                # Project architecture, edge-cases, and context details
├── frontend/            # React + Vite + Tailwind frontend application
├── scripts/             # CLI utilities for data ingestion and query tests
│   ├── ingest.py        # Pipeline to parse, clean, and store the Parquet database
│   └── recommend.py     # CLI test runner for recommendation queries
├── src/
│   └── app/             # Core FastAPI backend code
│       ├── api/         # Routes, endpoints, and request/response schemas
│       ├── data/        # Repository and database loaders
│       ├── ingestion/   # Data extraction and pre-processing pipeline
│       ├── models/      # Domain models and UserPreferences schemas
│       └── services/    # Orchestrator, filters, LLM clients, and prompt builders
├── tests/               # Pytest testing suites (unit, integration, and E2E)
└── pyrefly.toml         # Pyrefly LSP lint/type configuration
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the project root folder. You can use `.env.example` as a template:

```env
# LLM Provider Configuration
LLM_PROVIDER=groq
LLM_API_KEY=your_groq_api_key
LLM_MODEL=llama3-70b-8192

# Data Ingestion Configuration
DATA_PATH=./data/processed/restaurants.parquet
MAX_CANDIDATES=30

# Budget Thresholds
BUDGET_LOW_MAX=300
BUDGET_MEDIUM_MAX=700
```

---

## ⚙️ Setup and Installation

### 1. Backend Setup

Prerequisites: Python 3.9+ installed on your system.

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install required Python packages
pip install -r requirements.txt
```

### 2. Ingest Dataset
Before running the application, parse and compile the processed database using the ingestion CLI script:

```bash
python scripts/ingest.py
```

This reads the raw dataset and generates the preprocessed parquet database at `./data/processed/restaurants.parquet` along with a summary console report.

### 3. Frontend Setup

Prerequisites: Node.js (v18+) and npm installed on your system.

```bash
# Navigate to the frontend directory
cd frontend

# Install frontend dependencies
npm install
```

---

## 🏃 Running the Application

### 1. Launch Services
You can run both the FastAPI backend and Vite frontend dev servers using the startup bash helper script from the root directory:

```bash
chmod +x run.sh
./run.sh
```

Alternatively, run them separately:
- **Backend API Server (port 8000)**:
  ```bash
  python src/app/main.py
  ```
- **Frontend App (port 5173)**:
  ```bash
  cd frontend
  npm run dev
  ```

---

## 🧪 Testing

Execute the test suites containing unit tests, orchestrator integrations, and E2E pipelines using pytest:

```bash
.venv/bin/pytest
```

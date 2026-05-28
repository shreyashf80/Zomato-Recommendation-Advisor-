# Zomato AI Recommendation Advisor - Deployment Plan

This document outlines the step-by-step instructions to deploy the Zomato AI Recommendation Advisor backend service to **Railway.com** and the React frontend web application to **Vercel.com**. It also documents how to run the full stack locally using **Docker**.

---

## 🏗️ Architecture Flow in Production

```text
┌────────────────────────┐                    ┌────────────────────────┐
│   React Frontend       │   REST API Request │   FastAPI Backend      │
│   (Hosted on Vercel)   │───────────────────>│   (Hosted on Railway)  │
│   Vite + Tailwind      │<───────────────────│   Python + Parquet DB  │
└────────────────────────┘    CORS Approved   └────────────────────────┘
                                                           │
                                                           │ Consult LLM
                                                           ▼
                                                      ┌─────────┐
                                                      │  Groq   │
                                                      │  Cloud  │
                                                      └─────────┘
```

---

## 🐳 Option A: Docker (Local / Self-Hosted)

Docker lets you run both the backend and frontend together with a single command, with no local Python or Node.js installation required.

### Files Created

| File | Purpose |
| :--- | :--- |
| `Dockerfile` | Backend (FastAPI) container — multi-stage Python build |
| `frontend/Dockerfile` | Frontend (React) container — Vite build → Nginx serve |
| `frontend/nginx.conf` | Nginx config for SPA client-side routing |
| `docker-compose.yml` | Orchestrates both containers together |
| `.dockerignore` | Keeps build contexts lean (excludes `.venv`, `node_modules`, secrets) |

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Steps

1. **Copy and populate the environment file**:
   ```bash
   cp .env.example .env
   # Edit .env and fill in your GROQ_API_KEY
   ```

2. **Build and start all containers**:
   ```bash
   docker compose up --build
   ```
   > On first run the backend container will automatically download and ingest the Zomato dataset (~51 k rows). This takes 1–3 minutes. Subsequent starts use the cached `parquet_data` volume and skip the ingest.

3. **Access the application**:

   | Service | URL |
   | :--- | :--- |
   | Frontend | http://localhost:3000 |
   | Backend API | http://localhost:8000/api/v1 |
   | Interactive API Docs | http://localhost:8000/docs |

4. **Stop all containers**:
   ```bash
   docker compose down
   ```
   Add `-v` to also delete the Parquet data volume (forces re-ingest on next start):
   ```bash
   docker compose down -v
   ```

### How the `VITE_API_BASE_URL` build-arg works

Vite inlines environment variables at build time. The `docker-compose.yml` passes `VITE_API_BASE_URL=http://localhost:8000/api/v1` as a **Docker build argument** so the React bundle hits the local backend. When building for a different target (e.g., Railway), override it:

```bash
docker build \
  --build-arg VITE_API_BASE_URL=https://your-railway-domain.up.railway.app/api/v1 \
  -t zomato-frontend \
  frontend/
```

---

## ☁️ Option B: Railway (Backend) + Vercel (Frontend)

### 1. Backend Deployment (Railway.com)

Railway natively detects the `Dockerfile` at the repo root and builds the backend image automatically.

#### Steps:
1. **Create Project**:
   - Go to [Railway.com](https://railway.com) and sign in.
   - Click **New Project** -> **Deploy from GitHub repository**.
   - Select the `Zomato-Recommendation-Advisor-` repository.

2. **Configure Start Command** (if not using Dockerfile auto-detection):
   - Go to **Settings** -> **Deploy** -> **Start Command**.
   - Set:
     ```bash
     python scripts/ingest.py && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

3. **Set Environment Variables**:
   - Navigate to the **Variables** tab for the backend service.
   - Add the following variables:

     | Variable | Value |
     | :--- | :--- |
     | `LLM_PROVIDER` | `groq` |
     | `GROQ_API_KEY` | your actual Groq API key |
     | `LLM_MODEL` | `llama-3.3-70b-versatile` |
     | `DATA_PATH` | `./data/processed/restaurants.parquet` |
     | `MAX_CANDIDATES` | `30` |
     | `BUDGET_LOW_MAX` | `500` |
     | `BUDGET_MEDIUM_MAX` | `1500` |
     | `CORS_ORIGINS` | `http://localhost:5173` *(update after Vercel deploy)* |

4. **Generate Public Endpoint**:
   - Go to the **Settings** tab → **Networking** → click **Generate Domain**.
   - Copy the generated domain (e.g., `https://zomato-recommendation-advisor-production.up.railway.app`).

---

### 2. Frontend Deployment (Vercel.com)

Vercel builds and serves the static React SPA.

#### Steps:
1. **Create Project**:
   - Go to [Vercel.com](https://vercel.com) and sign in.
   - Click **Add New** -> **Project**.
   - Import the `Zomato-Recommendation-Advisor-` repository.

2. **Configure Directory & Build Settings**:
   - In the import wizard, set **Root Directory** to `frontend`.
   - **Framework Preset**: `Vite` (auto-detected)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

3. **Define Environment Variables**:
   - Key: `VITE_API_BASE_URL`
   - Value: `https://your-railway-domain.up.railway.app/api/v1`

4. **Deploy**:
   - Click **Deploy**. Copy the assigned production URL (e.g., `https://zomato-recommendation-advisor.vercel.app`).

---

### 3. Finalize CORS Handshake

To allow the Vercel frontend to call the Railway backend:

1. Go back to your **Railway** dashboard.
2. Open the backend service → **Variables** tab.
3. Update `CORS_ORIGINS`:
   ```
   http://localhost:5173,https://your-vercel-domain.vercel.app
   ```
4. Save. Railway will automatically redeploy the backend with the new CORS list.

---

## 🧪 Verification Checklist

- [ ] Open the frontend URL (Docker: `http://localhost:3000` | Vercel: deployed URL).
- [ ] Confirm the location and cuisine dropdowns populate (backend metadata request succeeds).
- [ ] Select **BTM** location + **Chinese** cuisine, add a special request, and click **Find My Perfect Meal**.
- [ ] Confirm recommendation cards and the AI Verdict banner display correctly.
- [ ] Check backend API docs at `/docs` to confirm all routes are live.

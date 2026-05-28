# Zomato AI Recommendation Advisor - Deployment Plan

This document outlines the step-by-step instructions to deploy the Zomato AI Recommendation Advisor — the **FastAPI backend** to **Railway.com** and the **React frontend** to **Vercel.com**.

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

## Step 1 — Backend Deployment (Railway.com)

Railway detects the `Dockerfile` at the repo root and builds the backend image automatically using it.

### 1.1 Create a New Project

1. Go to [Railway.com](https://railway.com) and sign in.
2. Click **New Project** → **Deploy from GitHub repository**.
3. Select the `Zomato-Recommendation-Advisor-` repository.
4. Railway will auto-detect the root `Dockerfile` and begin building.

> [!IMPORTANT]
> **Why the Dockerfile uses a 3-stage build with ingest at build time**
>
> The dataset is ~52 k rows. If ingestion runs inside the start command (`python scripts/ingest.py && uvicorn ...`), the container is not listening on `$PORT` during that time. Railway enforces a **~5-minute startup timeout** and will kill the container if the port is not bound in time, causing a deployment crash.
>
> The `Dockerfile` solves this by running `scripts/ingest.py` **during the image build** (Stage 2). The processed Parquet file is baked into the image so that at container start time the server binds the port in seconds.

### 1.2 Set the Start Command

1. In the Railway project panel, click on the service block.
2. Go to **Settings** → **Deploy** → **Start Command**.
3. Set it to:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
   > Ingest already ran during the Docker build — no ingestion at startup means the port binds in seconds and Railway's health check passes immediately.

### 1.3 Set Environment Variables

Navigate to the **Variables** tab and add:

| Variable | Value | Notes |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `groq` | |
| `GROQ_API_KEY` | `your_groq_api_key` | Get from [console.groq.com](https://console.groq.com) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | |
| `LLM_TEMPERATURE` | `0.3` | |
| `LLM_TIMEOUT_SECONDS` | `60` | |
| `LLM_MAX_RETRIES` | `1` | |
| `LLM_JSON_MODE` | `true` | |
| `DATA_PATH` | `./data/processed/restaurants.parquet` | |
| `MAX_CANDIDATES` | `30` | |
| `BUDGET_LOW_MAX` | `500` | |
| `BUDGET_MEDIUM_MAX` | `1500` | |
| `CORS_ORIGINS` | `http://localhost:5173` | ⚠️ Update after Vercel deploy (Step 3) |

### 1.4 Generate a Public Domain

1. Go to **Settings** → **Networking** → click **Generate Domain**.
2. Copy the domain — you will need it in the next step.
   Example: `https://zomato-recommendation-advisor-production.up.railway.app`

---

## Step 2 — Frontend Deployment (Vercel.com)

Vercel builds the Vite SPA and serves it as a static site.

### 2.1 Create a New Project

1. Go to [Vercel.com](https://vercel.com) and sign in.
2. Click **Add New** → **Project**.
3. Import the `Zomato-Recommendation-Advisor-` repository.

### 2.2 Configure Build Settings

In the import wizard:

| Setting | Value |
| :--- | :--- |
| **Root Directory** | `frontend` |
| **Framework Preset** | `Vite` *(auto-detected)* |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### 2.3 Set Environment Variables

Under the **Environment Variables** section, add:

| Key | Value |
| :--- | :--- |
| `VITE_API_BASE_URL` | `https://your-railway-domain.up.railway.app/api/v1` |

> Replace `your-railway-domain` with the actual domain generated in **Step 1.4**.
>
> `VITE_API_BASE_URL` is inlined at build time by Vite — the React bundle uses it to route all API requests to the Railway backend.

### 2.4 Deploy

Click **Deploy**. Vercel installs dependencies, builds the bundle, and assigns a production URL.
Copy the URL — you will need it in the next step.
Example: `https://zomato-recommendation-advisor.vercel.app`

---

## Step 3 — Finalize CORS Handshake

Allow the Vercel frontend to call the Railway backend by updating `CORS_ORIGINS`:

1. Go back to your **Railway** dashboard.
2. Open the service → **Variables** tab.
3. Update `CORS_ORIGINS` to include both local dev and the Vercel URL:
   ```
   http://localhost:5173,https://your-vercel-domain.vercel.app
   ```
4. **Save.** Railway automatically redeploys the backend with the updated allowed-origins list.

---

## 🔁 Redeployment

| Trigger | What happens |
| :--- | :--- |
| Push to `main` branch | Railway and Vercel both auto-redeploy |
| Change Railway env var | Railway redeploys the backend only |
| Change Vercel env var | Requires a manual **Redeploy** in the Vercel dashboard (build-time variable) |

---

## 🧪 Verification Checklist

- [ ] Open the Vercel frontend URL.
- [ ] Confirm the **Location** and **Cuisine** dropdowns populate *(backend metadata request succeeds)*.
- [ ] Select **BTM** location + **Chinese** cuisine, enter a special request, and click **Find My Perfect Meal**.
- [ ] Confirm recommendation cards and the **AI Verdict** banner render correctly.
- [ ] Visit `https://your-railway-domain.up.railway.app/docs` to confirm all API routes are live.

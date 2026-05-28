# Zomato AI Recommendation Advisor - Deployment Plan

This document outlines the step-by-step instructions to deploy the Zomato AI Recommendation Advisor backend service to **Railway.com** and the React frontend web application to **Vercel.com**.

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

## 1. Backend Deployment (Railway.com)

Railway natively detects the `requirements.txt` file and builds the Python environment using Nixpacks.

### Steps:
1. **Create Project**:
   - Go to [Railway.com](https://railway.com) and sign in.
   - Click **New Project** -> **Deploy from GitHub repository**.
   - Select the `Zomato-Recommendation-Advisor-` repository.

2. **Configure Custom Start & Ingestion Commands**:
   - In the Railway project panel, click on the backend service block.
   - Go to **Settings** -> **Deploy** -> **Start Command**.
   - Set the Start Command to:
     ```bash
     python scripts/ingest.py && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
     *(This runs the ingestion script at startup to download and compile the Parquet database into local scratch storage, then boots the FastAPI application via the root entrypoint on the correct dynamic port).*

3. **Set Environment Variables**:
   - Navigate to the **Variables** tab for the backend service.
   - Add the following variables:
     - `LLM_PROVIDER`: `groq`
     - `GROQ_API_KEY`: `your_actual_groq_api_key` *(or `LLM_API_KEY`)*
     - `LLM_MODEL`: `llama-3.3-70b-versatile`
     - `DATA_PATH`: `./data/processed/restaurants.parquet`
     - `MAX_CANDIDATES`: `30`
     - `BUDGET_LOW_MAX`: `500`
     - `BUDGET_MEDIUM_MAX`: `1500`
     - `CORS_ORIGINS`: `http://localhost:5173` *(We will append the Vercel URL here once the frontend is deployed)*

4. **Generate Public Endpoint**:
   - Go to the **Settings** tab.
   - Under **Networking**, click **Generate Domain**.
   - Copy the generated domain (e.g., `https://zomato-recommendation-advisor-production.up.railway.app`).

---

## 2. Frontend Deployment (Vercel.com)

Vercel will manage building and serving the static React Single Page Application (SPA).

### Steps:
1. **Create Project**:
   - Go to [Vercel.com](https://vercel.com) and sign in.
   - Click **Add New** -> **Project**.
   - Import the `Zomato-Recommendation-Advisor-` repository.

2. **Configure Directory & Build Settings**:
   - In the import wizard, look for **Root Directory** and click **Edit**.
   - Select the `frontend` folder.
   - Expand the **Build and Development Settings** section:
     - **Framework Preset**: `Vite` (automatically detected)
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`

3. **Define Environment Variables**:
   - Under the **Environment Variables** section, add:
     - Key: `VITE_API_BASE_URL`
     - Value: `https://your-railway-domain.up.railway.app/api/v1` *(Use the domain generated in Railway step 4)*

4. **Deploy**:
   - Click **Deploy**. Vercel will install dependencies, build the static assets, and assign a production URL.
   - Copy the deployed frontend URL (e.g., `https://zomato-recommendation-advisor.vercel.app`).

---

## 3. Finalize CORS Handshake

To allow the frontend hosted on Vercel to securely fetch data from the backend hosted on Railway:

1. Go back to your **Railway** dashboard.
2. Select your backend service and open the **Variables** tab.
3. Update the `CORS_ORIGINS` variable by adding your Vercel URL:
   - Key: `CORS_ORIGINS`
   - Value: `http://localhost:5173,https://your-vercel-domain.vercel.app`
4. Save the changes. Railway will automatically rebuild and redeploy the backend with the new CORS origin allowed list.

---

## 🧪 Verification Checklist

- Open your deployed Vercel URL.
- Verify that the form loads location and cuisine metadata dynamically (signaling a successful backend metadata request).
- Fill in BTM and Chinese cuisine, write a special request, and click **Find My Perfect Meal**.
- Check that the recommendations cards and AI Verdict display correctly.

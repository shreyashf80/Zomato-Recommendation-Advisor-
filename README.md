# Zomato AI Recommendation Advisor

A decoupled web application that leverages structured restaurant datasets and Large Language Models (LLMs) to serve as a personalized culinary digital concierge. The system applies deterministic criteria filters before utilizing the LLM to rank and provide custom explanations for selected restaurants.

## 🚀 Key Features
- **Deterministic Pre-Filtering**: Filters restaurant datasets by Location, Cuisine, and Budget range before sending candidates to the LLM to minimize latency, costs, and hallucination risks.
- **AI-Powered Personalization**: Integrates Groq (`llama-3.3-70b-versatile`) to reason, rank candidates, and generate natural language "AI Verdicts" based on user preferences.
- **Zomato "Sushi" Design System**: A responsive dashboard styling incorporating Zomato's signature color palette (Red, Green, Rating Gold), typography (Plus Jakarta Sans), and card styles.
- **Responsive Grid Layout**: Features a top compact search controller and a multi-column cards grid that stacks vertically on mobile devices.
- **Production-Grade Observability**: Context-aware logger formatted with request-scoped Correlation IDs (`X-Correlation-ID`) to trace latency, filter counts, and prompt token size metrics.

## 🛠️ Tech Stack
- **Frontend**: React JS, Vite, Tailwind CSS, Google Material Symbols.
- **Backend**: Python (3.11+), FastAPI, Uvicorn, Pydantic, Pandas, PyArrow.
- **AI Infrastructure**: Groq API (JSON response format).

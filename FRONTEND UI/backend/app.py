"""
FastAPI application entry point for the Personalized Networking Assistant.

Run with:
    uvicorn backend.app:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import starters, factcheck, history

app = FastAPI(
    title="Personalized Networking Assistant API",
    description=(
        "Generates tailored conversation starters for networking events, "
        "verifies facts via Wikipedia, and tracks conversation history/feedback."
    ),
    version="1.0.0",
)

# Allow the Streamlit frontend (and any local dev client) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(starters.router)
app.include_router(factcheck.router)
app.include_router(history.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}

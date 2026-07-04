"""
Pydantic schemas shared across the FastAPI routes.
Keeping these in one module makes the API contract easy to review
and keeps routes/services free of duplicated validation logic.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class EventInput(BaseModel):
    event_description: str = Field(..., example="AI for Sustainable Cities")
    interests: List[str] = Field(default_factory=list, example=["climate change", "urban planning"])
    user_id: Optional[str] = Field(default="anonymous")


class StarterResponse(BaseModel):
    themes: List[str]
    starters: List[str]
    history_id: str


class FactCheckRequest(BaseModel):
    query: str = Field(..., example="blockchain in healthcare")


class FactCheckResponse(BaseModel):
    query: str
    summary: str
    source_url: Optional[str] = None
    found: bool


class FeedbackInput(BaseModel):
    history_id: str
    useful: bool


class HistoryEntry(BaseModel):
    id: str
    user_id: str
    event_description: str
    interests: List[str]
    themes: List[str]
    starters: List[str]
    feedback: Optional[bool] = None
    timestamp: str

"""Route: generate personalized conversation starters (Scenario 1)."""
from fastapi import APIRouter

from backend.schemas import EventInput, StarterResponse
from backend.models.theme_extractor import theme_extractor
from backend.models.starter_generator import starter_generator
from backend.services import history_service

router = APIRouter(prefix="/starters", tags=["starters"])


@router.post("/generate", response_model=StarterResponse)
def generate_starters(payload: EventInput):
    themes = theme_extractor.extract_themes(payload.event_description, payload.interests)
    starters = starter_generator.generate_starters(themes, payload.interests)

    entry = history_service.add_entry(
        user_id=payload.user_id or "anonymous",
        event_description=payload.event_description,
        interests=payload.interests,
        themes=themes,
        starters=starters,
    )

    return StarterResponse(themes=themes, starters=starters, history_id=entry["id"])

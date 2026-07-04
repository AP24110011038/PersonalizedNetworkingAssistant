"""Route: review past strategies and submit feedback (Scenario 3)."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from backend.schemas import HistoryEntry, FeedbackInput
from backend.services import history_service

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/", response_model=List[HistoryEntry])
def get_history(user_id: Optional[str] = Query(default=None)):
    return history_service.get_history(user_id)


@router.post("/feedback", response_model=HistoryEntry)
def submit_feedback(payload: FeedbackInput):
    entry = history_service.set_feedback(payload.history_id, payload.useful)
    if entry is None:
        raise HTTPException(status_code=404, detail="History entry not found")
    return entry

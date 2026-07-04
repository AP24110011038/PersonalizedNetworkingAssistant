"""Route: quick fact verification via Wikipedia (Scenario 2)."""
from fastapi import APIRouter

from backend.schemas import FactCheckRequest, FactCheckResponse
from backend.models.fact_checker import fact_checker

router = APIRouter(prefix="/factcheck", tags=["factcheck"])


@router.post("/query", response_model=FactCheckResponse)
def check_fact(payload: FactCheckRequest):
    result = fact_checker.check_fact(payload.query)
    return FactCheckResponse(**result)

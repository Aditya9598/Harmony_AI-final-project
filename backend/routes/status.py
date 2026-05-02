from fastapi import APIRouter

from config import get_settings
from models.schemas import StatusResponse


router = APIRouter(tags=["status"])


@router.get("/status", response_model=StatusResponse)
async def status() -> StatusResponse:
    settings = get_settings()
    return StatusResponse(status="running", project=settings.app_name)

from fastapi import APIRouter, HTTPException
import httpx
from ..config import settings
from ..utils.utils import fetch_data

router = APIRouter(prefix="/teams", tags=["teams"])

@router.get("/{league_id}")
async def teams(league_id: int):
    url = settings.API_URL_TEAMS.format(league_id=league_id)
    return await fetch_data(url)



from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from httpx import HTTPStatusError
from typing import List
from ..config import settings
from ..utils.utils import fetch_data
from ..utils.logger import log_message
from ..schemas.league import League

router = APIRouter(prefix="/leagues", tags=["leagues"])

def parse_response(league: dict) -> League:
    return League(
        id=league.get("idLeague"),
        name=league.get("strLeague")
    )

async def customize_response(data: dict) -> List[League]:
    leagues = data.get("leagues", [])
    return [parse_response(league) for league in leagues]

@router.get("/", response_model=List[League])
async def get_leagues():
    url = settings.API_URL_LEAGUES
    try:
        data = await fetch_data(url)
        return await customize_response(data)
    except HTTPStatusError as e:
        if e.response.status_code == 307:
            return RedirectResponse(url=e.response.headers.get("Location"))
        log_message(f"HTTP error occurred: {e.response.text}", level="error")
        raise HTTPException(
            status_code=e.response.status_code,
            detail={
                "error": "Error fetching data from API",
                "message": f"Error fetching data from API: {e.response.text}",
            }
        ) from e
    except Exception as e:
        log_message(f"An unexpected error occurred: {str(e)}", level="error")
        raise HTTPException(status_code=500, detail={
            "error": "Internal Server Error",
            "message": f"An unexpected error occurred: {str(e)}",
        }) from e

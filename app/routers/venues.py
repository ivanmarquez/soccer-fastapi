from fastapi import APIRouter, HTTPException
from httpx import HTTPStatusError
from typing import List
import re
from ..config import settings
from ..utils.utils import fetch_data
from ..utils.logger import log_message
from ..schemas.venue import Venue

router = APIRouter(prefix="/venues", tags=["venues"])

def parse_coordinates(coord_str: str) -> dict:
    if not coord_str:
        return {"lat": 0.0, "lon": 0.0}

    def dms_to_dd(degrees, minutes, seconds, direction):
        dd = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
        if direction in ['S', 'W']:
            dd *= -1
        return dd

    pattern = re.compile(r"(\d+)°(\d+)′(\d+)″([NSEW])")
    matches = pattern.findall(coord_str)
    if len(matches) != 2:
        return {"lat": 0.0, "lon": 0.0}

    lat = dms_to_dd(*matches[0])
    lon = dms_to_dd(*matches[1])

    return {"lat": lat, "lon": lon}

def parse_response(venue: dict) -> Venue:
    coordinates = parse_coordinates(venue.get("strMap"))
    lat, lon = round(coordinates["lat"], 8), round(coordinates["lon"], 8)

    return Venue(
        id=venue.get("idVenue"),
        name=venue.get("strVenue"),
        country=venue.get("strCountry"),
        location=venue.get("strLocation"),
        lat=lat,
        lon=lon
    )

async def customize_response(data: dict) -> Venue:
    venues = data.get("venues", [])
    if not venues:
        raise HTTPException(status_code=404, detail="Venue not found")
    return parse_response(venues[0])

@router.get("/{venue_id}", response_model=Venue, response_model_exclude_unset=True)
async def get_venue(venue_id: int):
    url = settings.API_URL_VENUE.format(venue_id=venue_id)
    try:
        data = await fetch_data(url)
        return await customize_response(data)
    except HTTPStatusError as e:
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

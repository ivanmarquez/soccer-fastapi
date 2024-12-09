from fastapi import APIRouter, HTTPException
import asyncio
from typing import List
import json
from datetime import datetime
from ..config import settings
from ..utils.utils import fetch_data
from ..utils.logger import log_message
from ..schemas.match import Match
from ..schemas.team import Team
from ..routers.venues import get_venue
from ..routers.ai import match_analysis

router = APIRouter(prefix="/matches", tags=["matches"])


async def get_wheater(lat: float, lon: float, timestamp: str) -> dict:
    try:
        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").timestamp()
        url = settings.API_URL_WHEATER.format(lat=lat, lon=lon, dt=int(timestamp))
        return await fetch_data(url)
    except Exception as e:
        log_message(f"Error fetching weather data: {str(e)}", level="error")
        return {}

def generate_prompt(match: dict, weather: dict) -> str:
    match_string = json.dumps(match)
    weather_string = json.dumps(weather)

    prompt = (
        f""""
        Describe a 100-200 word analysis in English of the upcoming soccer match between soccer teams A and B.
        Focus on the team's strengths, recent performance, and any other contextual factors that might give one team an advantage over the other.
        If weather conditions are provided, include an analysis of how they might influence the gameplay (e.g., temperature, wind).
        Use a professional yet engaging tone suitable for a sports commentary. Provide a balanced and insightful perspective.

        DO NOT include any information:
        - Date and time of the match.
        - Location of the match.
        - Teams playing the match.

        Data that can help you write the analysis:
        {f"- The match will be played at {match.get("strVenue")} in {match.get("strCountry")}." if weather and match.get("strVenue") and weather.get('strCountry') else ""}
        {f"- The match will take place on {match.get("dateEvent")} at {match.get("strTime")}." if weather and match.get("dateEvent") and weather.get('strTime') else ""}
        {f"- The home team is {match.get("strHomeTeam")} and the away team is {match.get("strAwayTeam")}." if weather and match.get("strHomeTeam") and weather.get('strAwayTeam') else ""}
        {f"- The weather forecast for the match is as follows: {weather.get('weather')[0].get('description')}." if weather and weather.get('weather') else ""}
        {f"- The temperature will be {weather.get('main').get('temp')}°C with a humidity of {weather.get('main').get('humidity')}%." if weather and weather.get('main') else ""}
        {f"- The wind speed will be {weather.get('wind').get('speed')} m/s." if weather and weather.get('wind') else ""}

        Soccer Match data in JSON format: {match_string}
        Weather data in JSON format: {weather_string}"""
    )

    return prompt


async def parse_response(match: dict) -> Match:
    venue_id = match.get("idVenue")
    venue, weather = (None, None)

    if venue_id:
        venue_task = get_venue(venue_id)
        venue = await venue_task

        if venue and (venue.lat != 0.0 or venue.lon != 0.0):
            weather_task = get_wheater(venue.lat, venue.lon, match.get("strTimestamp"))
            weather = await weather_task

    prompt = generate_prompt(match, weather or {})
    #prompt_result = await match_analysis(prompt)
    prompt_result = { "prompt":  "Analysis placeholder text" }

    return Match(
        id=match.get("idEvent"),
        league_id=match.get("idLeague"),
        name=match.get("strEvent"),
        timestamp=match.get("strTimestamp"),
        date=match.get("dateEvent"),
        time=match.get("strTime"),
        venue=venue,
        country=match.get("strCountry"),
        image=match.get("strThumb"),
        home_team=Team(
            id=match.get("idHomeTeam"),
            name=match.get("strHomeTeam"),
            image=match.get("strHomeTeamBadge"),
            league_id=match.get("idLeague"),
        ),
        away_team=Team(
            id=match.get("idAwayTeam"),
            name=match.get("strAwayTeam"),
            image=match.get("strAwayTeamBadge"),
            league_id=match.get("idLeague"),
        ),
        prompt=prompt_result,
    )


async def customize_response(data: dict) -> List[Match]:
    events = data.get("events", [])
    if not events:
        return []

    semaphore = asyncio.Semaphore(10)

    async def process_event(event):
        async with semaphore:
            return await parse_response(event)

    #return await asyncio.gather(*(process_event(event) for event in events if event))
    return await asyncio.gather(*(process_event(event) for event in events[:12] if event))


@router.get("/{league_id}", response_model=List[Match], response_model_exclude_unset=True)
async def matches(league_id: int):
    url = settings.API_URL_MATCHES.format(league_id=league_id)

    try:
        data = await fetch_data(url)
        if not data:
            raise HTTPException(status_code=404, detail="No data found.")
        return await customize_response(data)
    except Exception as e:
        log_message(f"Error in matches endpoint: {str(e)}", level="error")
        raise HTTPException(status_code=500, detail="Failed to fetch matches.")

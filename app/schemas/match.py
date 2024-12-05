from pydantic import BaseModel
from datetime import date, time
from ..schemas.team import Team
from ..schemas.venue import Venue
from ..schemas.prompt import Prompt

class Match(BaseModel):
    id: int
    league_id: int
    name: str
    timestamp: str
    date: date
    time: time
    venue: Venue
    country: str
    image: str
    home_team: Team
    away_team: Team
    prompt: Prompt

    class Config:
        from_attributes: bool = True

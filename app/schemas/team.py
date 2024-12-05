from pydantic import BaseModel
from typing import Optional

class Team(BaseModel):
    id: int
    name: str
    name_short: Optional[str] = None
    location: Optional[str] = None
    image: str
    league_id: int

    class Config:
        from_attributes = True

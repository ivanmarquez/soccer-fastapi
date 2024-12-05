from pydantic import BaseModel

class Venue(BaseModel):
    id: int
    name: str
    country: str
    location: str
    lat: float
    lon: float

    class Config:
        from_attributes = True


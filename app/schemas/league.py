from pydantic import BaseModel

class League(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


from pydantic import BaseModel

class FavoriteBase(BaseModel):
    match_id: int

class FavoriteCreate(FavoriteBase):
    pass

class Favorite(FavoriteBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

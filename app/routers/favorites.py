from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..utils.logger import log_message
from ..database import get_db
from ..models import favorite as favorite_model, match as match_model, user as user_model
from ..schemas import favorite as favorite_schema
from ..auth.jwt_handler import get_current_user

router = APIRouter(prefix="/favorites", tags=["favorites"])

def get_match_or_404(db: Session, match_id: int):
    db_match = db.query(match_model.Match).filter(match_model.Match.id == match_id).first()
    if not db_match:
        log_message(f"Match with id {match_id} not found")
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match

def create_favorite(db: Session, user_id: int, match_id: int):
    db_favorite = favorite_model.Favorite(user_id=user_id, match_id=match_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

@router.post("/", response_model=favorite_schema.Favorite)
async def add_favorite(favorite: favorite_schema.FavoriteCreate, db: Session = Depends(get_db), current_user: user_model.User = Depends(get_current_user)):
    try:
        get_match_or_404(db, favorite.match_id)
        return create_favorite(db, current_user.id, favorite.match_id)
    except HTTPException as e:
        log_message(f"Error adding favorite: {e.detail}")
        raise e

@router.get("/", response_model=List[favorite_schema.Favorite])
async def get_favorites(db: Session = Depends(get_db), current_user: user_model.User = Depends(get_current_user)):
    try:
        return db.query(favorite_model.Favorite).filter(favorite_model.Favorite.user_id == current_user.id).all()
    except Exception as e:
        log_message(f"Error fetching favorites: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

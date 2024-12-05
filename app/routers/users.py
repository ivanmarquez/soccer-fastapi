from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserLogin, User as UserSchema
from ..auth.jwt_handler import create_access_token, verify_access_token
from ..utils.logger import log_message
import hashlib

router = APIRouter(prefix="/users", tags=["users"])

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_user(db: Session, email: str, password: str = None) -> User:
    query = db.query(User).filter(User.email == email)

    if password:
        hashed_password = hash_password(password)
        query = query.filter(User.hashed_password == hashed_password)

    return query.first()


def handle_user_not_found(email: str):
    log_message(f"User {email} not found.")
    raise HTTPException(status_code=404, detail="User not found")


def handle_invalid_credentials(email: str):
    log_message(f"Failed login attempt for email: {email}")

    raise HTTPException(
        status_code=401,
        detail={
            "error": "Invalid email or password",
            "message": "Invalid email or password. Please try again."
        }
    )


def handle_existing_user(email: str):
    log_message(f"Email already registered: {email}")
    raise HTTPException(
        status_code=409,
        detail={
            "error": "Email already registered",
            "message": f"The email {email} is already in use. Please use a different email address or login if you already have an account."
        }
    )


@router.post("/signup", response_model=UserSchema)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user(db, user.email)
    if (existing_user):
        handle_existing_user(user.email)

    hashed_password = hash_password(user.password)

    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        favorites=[]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return JSONResponse(status_code=201, content={"success": True, "user": UserSchema.from_orm(db_user).dict()})


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user(db, user.email, user.password)
    if not db_user or db_user.hashed_password != hash_password(user.password):
        handle_invalid_credentials(user.email)

    access_token = create_access_token(data={"sub": db_user.email})
    return JSONResponse(
        status_code=200,
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserSchema.from_orm(db_user).dict()
        }
    )


@router.post("/logout")
async def logout(token: str = Depends(verify_access_token), db: Session = Depends(get_db)):
    # TODO: Implement token invalidation
    # Assuming you have a token blacklist table to store invalidated tokens

    # Add the token to the blacklist
    db_token = TokenBlacklist(token=token)
    db.add(db_token)
    db.commit()

    return JSONResponse(status_code=204, content={"message": "Successfully logged out"})


@router.put("/update", response_model=UserSchema)
async def update_user(user: UserUpdate, db: Session = Depends(get_db), token: str = Depends(verify_access_token)):
    db_user = get_user(db, token)

    if not db_user:
        handle_user_not_found(token)
    if user.email:
        db_user.email = user.email
    if user.password:
        db_user.hashed_password = hash_password(user.password)
    if user.first_name:
        db_user.first_name = user.first_name
    if user.last_name:
        db_user.last_name = user.last_name

    db.commit()
    db.refresh(db_user)

    return db_user

from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import leagues, teams, matches, venues, users, ai, favorites

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(leagues.router)
app.include_router(teams.router)
app.include_router(matches.router)
app.include_router(venues.router)
app.include_router(ai.router)
app.include_router(favorites.router)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()

@app.get("/")
async def root():
    return {"message": "Welcome to the Soccer API"}

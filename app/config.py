from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/postgres")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_DELTA: int = os.getenv("JWT_EXPIRATION_DELTA", 30)

    API_KEY: str = os.getenv("API_KEY", "3")
    API_URL_LEAGUES: str = os.getenv("API_URL_LEAGUES", f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/all_leagues.php")
    API_URL_TEAMS: str = os.getenv("API_URL_TEAMS", f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/lookup_all_teams.php?id={{league_id}}")
    API_URL_MATCHES: str = os.getenv("API_URL_MATCHES", f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/eventsnextleague.php?id={{league_id}}")
    API_URL_VENUE: str = os.getenv("API_URL_VENUE", f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/lookupvenue.php?id={{venue_id}}")
    API_URL_WHEATER: str = os.getenv("API_URL_WHEATER", f"http://nestapi:3000/weather/?lat={{lat}}&lon={{lon}}&dt={{dt}}")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GPT_MODEL: str = os.getenv("GPT_MODEL", "gpt-4o")

settings = Settings()

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from .team import Team

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    league_id = Column(Integer, ForeignKey("leagues.id"))
    score = Column(String, nullable=True)

    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    league = relationship("League", back_populates="matches")
    favorites = relationship("Favorite", back_populates="match")

Team.home_matches = relationship("Match", foreign_keys=[Match.home_team_id], back_populates="home_team")
Team.away_matches = relationship("Match", foreign_keys=[Match.away_team_id], back_populates="away_team")

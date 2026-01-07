from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Anime(Base):
    __tablename__ = 'animes'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, unique=True)
    english_title = Column(String(255))
    original_title = Column(String(255))
    year = Column(Integer)
    season = Column(String(50))  # Spring, Summer, Fall, Winter
    status = Column(String(50))  # Ongoing, Completed, etc.
    episodes_total = Column(Integer)
    episodes_aired = Column(Integer)
    duration_per_episode = Column(Integer)  # in minutes
    description = Column(Text)
    genres = Column(String(500))  # comma-separated
    studios = Column(String(255))
    rating = Column(Float)  # 0-10
    vote_count = Column(Integer, default=0)
    cover_image_url = Column(String(500))
    anime_hay_url = Column(String(500), unique=True)
    anime_hay_id = Column(String(100))
    source = Column(String(50), default='animehay')
    is_ongoing = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    episodes = relationship('Episode', back_populates='anime', cascade='all, delete-orphan')
    reviews = relationship('AnimeReview', back_populates='anime', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Anime(id={self.id}, title={self.title}, year={self.year})>'


class Episode(Base):
    __tablename__ = 'episodes'
    
    id = Column(Integer, primary_key=True)
    anime_id = Column(Integer, ForeignKey('animes.id'), nullable=False)
    episode_number = Column(Integer)
    episode_title = Column(String(255))
    duration = Column(Integer)  # in seconds
    air_date = Column(DateTime)
    description = Column(Text)
    views_count = Column(Integer, default=0)
    episode_url = Column(String(500), unique=True)
    video_sources = Column(Text)  # JSON format with video links
    created_at = Column(DateTime, default=datetime.utcnow)
    
    anime = relationship('Anime', back_populates='episodes')
    
    def __repr__(self):
        return f'<Episode(anime_id={self.anime_id}, ep={self.episode_number})>'


class AnimeReview(Base):
    __tablename__ = 'anime_reviews'
    
    id = Column(Integer, primary_key=True)
    anime_id = Column(Integer, ForeignKey('animes.id'), nullable=False)
    reviewer_name = Column(String(255))
    rating = Column(Float)  # 0-10
    content = Column(Text)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    anime = relationship('Anime', back_populates='reviews')
    
    def __repr__(self):
        return f'<AnimeReview(anime_id={self.anime_id}, rating={self.rating})>'


class AnimeGenre(Base):
    __tablename__ = 'anime_genres'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    slug = Column(String(100), unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnimeGenre(name={self.name})>'

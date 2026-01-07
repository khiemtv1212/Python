from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, unique=True)
    year = Column(Integer)
    director = Column(String(255))
    duration = Column(Integer)  # in minutes
    description = Column(Text)
    genres = Column(String(255))  # comma-separated
    imdb_url = Column(String(500), unique=True)
    poster_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ratings = relationship('Rating', back_populates='movie', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='movie', cascade='all, delete-orphan')
    cast_members = relationship('CastMember', back_populates='movie', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Movie(id={self.id}, title={self.title}, year={self.year})>'


class Rating(Base):
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    source = Column(String(50))  # imdb, rottentomatoes, etc.
    score = Column(Float)  # 0-10 or 0-100
    vote_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    movie = relationship('Movie', back_populates='ratings')
    
    def __repr__(self):
        return f'<Rating(movie_id={self.movie_id}, source={self.source}, score={self.score})>'


class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    reviewer_name = Column(String(255))
    rating = Column(Float)
    content = Column(Text)
    source = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    movie = relationship('Movie', back_populates='reviews')
    
    def __repr__(self):
        return f'<Review(movie_id={self.movie_id}, reviewer={self.reviewer_name})>'


class CastMember(Base):
    __tablename__ = 'cast_members'
    
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    actor_name = Column(String(255))
    character_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    movie = relationship('Movie', back_populates='cast_members')
    
    def __repr__(self):
        return f'<CastMember(movie_id={self.movie_id}, actor={self.actor_name})>'

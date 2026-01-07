from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.movie import Base
from config.settings import DATABASE_URL
from utils.logger import get_logger

logger = get_logger(__name__)

class Database:
    """Database connection and session management"""
    
    def __init__(self):
        try:
            self.engine = create_engine(DATABASE_URL, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database engine created successfully")
        except Exception as e:
            logger.error(f"Error creating database engine: {str(e)}")
            self.engine = None
    
    def create_tables(self):
        """Create all tables in database"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
    
    def get_session(self):
        """Get a new database session"""
        if self.engine is None:
            logger.error("Database engine not initialized")
            return None
        return self.Session()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

# Global database instance
db = Database()

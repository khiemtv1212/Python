"""
Movie Web Crawler - Main Script
Crawls movie information from various websites
"""

import time
from crawlers.imdb_crawler import IMDBCrawler
from crawlers.general_crawler import GeneralMovieCrawler
from database import db
from models.movie import Movie, Rating, Review, CastMember
from utils.logger import get_logger

logger = get_logger(__name__)

def save_movie_to_db(session, movie_data):
    """Save movie data to database"""
    try:
        # Check if movie already exists
        existing = session.query(Movie).filter_by(title=movie_data['title']).first()
        if existing:
            logger.info(f"Movie '{movie_data['title']}' already exists")
            return existing
        
        # Create new movie
        movie = Movie(
            title=movie_data.get('title', ''),
            year=int(movie_data.get('year', 0)) if movie_data.get('year') else None,
            director=movie_data.get('director', ''),
            duration=movie_data.get('duration'),
            description=movie_data.get('description', ''),
            genres=movie_data.get('genres', ''),
            imdb_url=movie_data.get('url', ''),
            poster_url=movie_data.get('poster_url', '')
        )
        
        # Add ratings
        if movie_data.get('rating'):
            rating = Rating(
                source=movie_data.get('source', 'unknown'),
                score=float(movie_data['rating']) if isinstance(movie_data['rating'], (int, float, str)) else None,
                movie=movie
            )
            session.add(rating)
        
        # Add cast members
        for cast in movie_data.get('cast', []):
            cast_member = CastMember(
                actor_name=cast.get('actor_name'),
                character_name=cast.get('character_name'),
                movie=movie
            )
            session.add(cast_member)
        
        session.add(movie)
        session.commit()
        logger.info(f"Saved movie: {movie.title}")
        return movie
        
    except Exception as e:
        logger.error(f"Error saving movie to database: {str(e)}")
        session.rollback()
        return None

def crawl_imdb_top250():
    """Example: Crawl IMDB Top 250 movies"""
    logger.info("Starting IMDB Top 250 crawl...")
    
    crawler = IMDBCrawler()
    session = db.get_session()
    
    try:
        # Get movie list
        url = 'https://www.imdb.com/chart/top250/'
        movies = crawler.crawl_movie_list(url, limit=10)  # Start with 10 for testing
        
        logger.info(f"Found {len(movies)} movies, crawling details...")
        
        for movie in movies:
            if movie.get('url'):
                # Full URL needed
                full_url = movie['url'] if movie['url'].startswith('http') else f"https://www.imdb.com{movie['url']}"
                details = crawler.crawl_movie_details(full_url)
                
                if details:
                    save_movie_to_db(session, details)
                
                # Be respectful with delays
                time.sleep(2)
        
        logger.info("IMDB Top 250 crawl completed")
        
    except Exception as e:
        logger.error(f"Error in IMDB crawl: {str(e)}")
    finally:
        session.close()

def crawl_custom_website(url, config):
    """
    Example: Crawl a custom movie website
    
    Args:
        url: Website URL
        config: Configuration with CSS selectors
            Example: {
                'movie_selector': 'div.movie-item',
                'title_selector': 'h2.title',
                'year_selector': 'span.year',
                'rating_selector': 'div.rating',
                'description_selector': 'p.description'
            }
    """
    logger.info(f"Starting custom website crawl: {url}")
    
    crawler = GeneralMovieCrawler()
    session = db.get_session()
    
    try:
        # Crawl movie list
        movies = crawler.crawl_movie_list(
            url,
            movie_selector=config.get('movie_selector'),
            title_selector=config.get('title_selector'),
            limit=20
        )
        
        logger.info(f"Found {len(movies)} movies")
        
        # Save to database
        for movie in movies:
            save_movie_to_db(session, movie)
        
        logger.info("Custom website crawl completed")
        
    except Exception as e:
        logger.error(f"Error in custom crawl: {str(e)}")
    finally:
        session.close()

def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("Movie Web Crawler Started")
    logger.info("=" * 50)
    
    # Create database tables
    db.create_tables()
    
    # Example 1: Crawl IMDB (uncomment to use)
    # crawl_imdb_top250()
    
    # Example 2: Crawl custom website
    # custom_config = {
    #     'movie_selector': 'div.movie-card',
    #     'title_selector': 'h3.movie-title',
    #     'year_selector': 'span.year',
    #     'rating_selector': 'div.rating',
    #     'description_selector': 'p.synopsis'
    # }
    # crawl_custom_website('https://example-movie-site.com/', custom_config)
    
    logger.info("Movie Web Crawler Finished")
    db.close()

if __name__ == '__main__':
    main()

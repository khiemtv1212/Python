"""
Crawl anime data from AnimeHay.life
"""

import time
from crawlers.animehay_crawler import AnimeHayCrawler
from database import db
from models.anime import Anime, Episode, AnimeGenre
from utils.logger import get_logger

logger = get_logger(__name__)

def save_anime_to_db(session, anime_data):
    """Save anime data to database"""
    try:
        # Check if anime already exists
        existing = session.query(Anime).filter_by(
            anime_hay_url=anime_data.get('anime_hay_url')
        ).first()
        
        if existing:
            logger.info(f"Anime '{anime_data.get('title')}' already exists")
            return existing
        
        # Create new anime
        anime = Anime(
            title=anime_data.get('title', ''),
            original_title=anime_data.get('original_title', ''),
            year=anime_data.get('year'),
            status=anime_data.get('status', ''),
            episodes_aired=anime_data.get('episodes_aired'),
            episodes_total=anime_data.get('episodes_total'),
            description=anime_data.get('description', ''),
            genres=anime_data.get('genres', ''),
            studios=anime_data.get('studios', ''),
            rating=anime_data.get('rating'),
            cover_image_url=anime_data.get('cover_image_url', ''),
            anime_hay_url=anime_data.get('anime_hay_url', ''),
            anime_hay_id=anime_data.get('anime_hay_id', ''),
            is_ongoing=anime_data.get('is_ongoing', False),
            source='animehay'
        )
        
        session.add(anime)
        session.commit()
        logger.info(f"Saved anime: {anime.title}")
        return anime
        
    except Exception as e:
        logger.error(f"Error saving anime to database: {str(e)}")
        session.rollback()
        return None

def save_episodes_to_db(session, anime_id, episodes_data):
    """Save episodes to database"""
    try:
        count = 0
        for ep_data in episodes_data:
            # Check if episode already exists
            existing = session.query(Episode).filter_by(
                anime_id=anime_id,
                episode_number=ep_data.get('episode_number')
            ).first()
            
            if not existing:
                episode = Episode(
                    anime_id=anime_id,
                    episode_number=ep_data.get('episode_number'),
                    episode_title=ep_data.get('episode_title', ''),
                    duration=ep_data.get('duration'),
                    description=ep_data.get('description', ''),
                    episode_url=ep_data.get('episode_url', '')
                )
                session.add(episode)
                count += 1
        
        session.commit()
        logger.info(f"Saved {count} episodes for anime_id {anime_id}")
        
    except Exception as e:
        logger.error(f"Error saving episodes: {str(e)}")
        session.rollback()

def crawl_newest_animes(limit=20):
    """Crawl newest animes from homepage"""
    logger.info("Starting to crawl newest animes...")
    
    crawler = AnimeHayCrawler()
    session = db.get_session()
    
    try:
        # Get newest anime list
        animes = crawler.crawl_newest(limit=limit)
        
        logger.info(f"Found {len(animes)} newest animes")
        
        for anime_info in animes:
            if anime_info.get('anime_hay_url'):
                # Crawl detailed information
                details = crawler.crawl_anime_details(anime_info['anime_hay_url'])
                
                if details:
                    # Save anime
                    saved_anime = save_anime_to_db(session, details)
                    
                    # Crawl and save episodes
                    if saved_anime:
                        episodes = crawler.crawl_episodes(anime_info['anime_hay_url'], limit=50)
                        if episodes:
                            save_episodes_to_db(session, saved_anime.id, episodes)
                
                # Be respectful with delays
                time.sleep(1)
        
        logger.info("Finished crawling newest animes")
        
    except Exception as e:
        logger.error(f"Error in crawl: {str(e)}")
    finally:
        session.close()

def crawl_category(category_slug, limit=20):
    """
    Crawl animes from a specific category
    
    Args:
        category_slug: Category slug (e.g., 'anime-1', 'cn-animation-34')
        limit: Maximum number of animes to crawl
    """
    logger.info(f"Starting to crawl category: {category_slug}")
    
    crawler = AnimeHayCrawler()
    session = db.get_session()
    
    try:
        # Get anime list by category
        animes = crawler.crawl_category(category_slug, limit=limit)
        
        logger.info(f"Found {len(animes)} animes in category")
        
        for anime_info in animes:
            if anime_info.get('anime_hay_url'):
                # Crawl detailed information
                details = crawler.crawl_anime_details(anime_info['anime_hay_url'])
                
                if details:
                    save_anime_to_db(session, details)
                
                time.sleep(1)
        
        logger.info("Finished crawling category")
        
    except Exception as e:
        logger.error(f"Error in category crawl: {str(e)}")
    finally:
        session.close()

def search_anime(query):
    """Search for anime by name"""
    logger.info(f"Searching for: {query}")
    
    crawler = AnimeHayCrawler()
    session = db.get_session()
    
    try:
        # Search
        results = crawler.search_anime(query)
        
        logger.info(f"Found {len(results)} search results")
        
        for anime_info in results:
            if anime_info.get('anime_hay_url'):
                details = crawler.crawl_anime_details(anime_info['anime_hay_url'])
                if details:
                    save_anime_to_db(session, details)
                
                time.sleep(1)
        
        logger.info("Finished searching")
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
    finally:
        session.close()

def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("AnimeHay Crawler Started")
    logger.info("=" * 50)
    
    # Create database tables
    db.create_tables()
    
    # Crawl examples
    crawl_newest_animes(limit=5)  # Start with 5 for testing
    
    # Or crawl by category
    # crawl_category('anime-1', limit=5)
    
    # Or search
    # search_anime('one piece')
    
    logger.info("AnimeHay Crawler Finished")
    db.close()

if __name__ == '__main__':
    main()

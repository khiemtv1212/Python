from crawlers.base_crawler import BaseCrawler
from utils.helpers import safe_extract, clean_text
from utils.logger import get_logger

logger = get_logger(__name__)

class IMDBCrawler(BaseCrawler):
    """Crawler for IMDB"""
    
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.imdb.com'
    
    def crawl_movie_list(self, url, limit=50):
        """
        Crawl list of movies from IMDB
        Example: https://www.imdb.com/chart/top250/
        """
        soup = self.get_soup(url)
        if soup is None:
            return []
        
        movies = []
        # Adjust selectors based on actual IMDB HTML structure
        movie_items = soup.select('div.ipc-title--base')[:limit]
        
        for item in movie_items:
            try:
                title = safe_extract(item, 'a', default='')
                if title:
                    movies.append({
                        'title': title,
                        'url': safe_extract(item, 'a', 'href', default=''),
                        'source': 'imdb'
                    })
            except Exception as e:
                logger.error(f"Error parsing movie item: {str(e)}")
        
        logger.info(f"Found {len(movies)} movies on IMDB")
        return movies
    
    def crawl_movie_details(self, movie_url):
        """
        Crawl detailed information about a movie
        """
        soup = self.get_soup(movie_url)
        if soup is None:
            return {}
        
        try:
            movie_data = {
                'title': safe_extract(soup, 'h1.sc-d541859f-1', default=''),
                'year': safe_extract(soup, 'span.sc-d541859f-3', default=''),
                'duration': safe_extract(soup, '[aria-label*="minutes"]', default=''),
                'description': safe_extract(soup, 'div.Storyline__StorylineSection--plot-summary', default=''),
                'genres': ','.join([
                    clean_text(tag.get_text()) 
                    for tag in soup.select('div.ipc-chip--on-base')[:5]
                ]),
                'rating': safe_extract(soup, 'span.sc-d541859f-1 span', default=''),
                'url': movie_url,
                'source': 'imdb'
            }
            
            # Extract cast
            cast = []
            for item in soup.select('div.StyledComponents__CastItemWrapper')[:10]:
                actor_name = safe_extract(item, 'a span', default='')
                if actor_name:
                    cast.append({
                        'actor_name': actor_name,
                        'character_name': safe_extract(item, 'div.sc-4b14c47-2', default='')
                    })
            
            movie_data['cast'] = cast
            logger.info(f"Crawled movie: {movie_data['title']}")
            return movie_data
            
        except Exception as e:
            logger.error(f"Error crawling movie details from {movie_url}: {str(e)}")
            return {}

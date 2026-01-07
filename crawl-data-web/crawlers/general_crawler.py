from crawlers.base_crawler import BaseCrawler
from utils.helpers import safe_extract, clean_text
from utils.logger import get_logger

logger = get_logger(__name__)

class GeneralMovieCrawler(BaseCrawler):
    """General crawler for movie websites"""
    
    def crawl_movie_list(self, url, movie_selector, title_selector, limit=50):
        """
        Crawl list of movies with custom selectors
        
        Args:
            url: URL to crawl
            movie_selector: CSS selector for movie container
            title_selector: CSS selector for movie title within container
            limit: Maximum number of movies to crawl
        """
        soup = self.get_soup(url)
        if soup is None:
            return []
        
        movies = []
        movie_items = soup.select(movie_selector)[:limit]
        
        for item in movie_items:
            try:
                title = safe_extract(item, title_selector, default='')
                if title:
                    movies.append({
                        'title': clean_text(title),
                        'source': 'general'
                    })
            except Exception as e:
                logger.error(f"Error parsing movie item: {str(e)}")
        
        logger.info(f"Found {len(movies)} movies")
        return movies
    
    def crawl_movie_details(self, url, selectors_map):
        """
        Crawl movie details with custom selectors
        
        Args:
            url: URL to crawl
            selectors_map: Dictionary mapping field names to CSS selectors
                Example: {
                    'title': 'h1.title',
                    'year': 'span.year',
                    'rating': 'div.rating',
                    'description': 'div.synopsis'
                }
        """
        soup = self.get_soup(url)
        if soup is None:
            return {}
        
        try:
            movie_data = {'url': url}
            
            for field, selector in selectors_map.items():
                movie_data[field] = safe_extract(soup, selector, default='')
            
            logger.info(f"Crawled movie: {movie_data.get('title', 'Unknown')}")
            return movie_data
            
        except Exception as e:
            logger.error(f"Error crawling movie details from {url}: {str(e)}")
            return {}
    
    def crawl_reviews(self, url, review_selector, reviewer_selector, rating_selector, content_selector):
        """Crawl reviews from a page"""
        soup = self.get_soup(url)
        if soup is None:
            return []
        
        reviews = []
        review_items = soup.select(review_selector)
        
        for item in review_items:
            try:
                review = {
                    'reviewer_name': safe_extract(item, reviewer_selector, default=''),
                    'rating': safe_extract(item, rating_selector, default=''),
                    'content': safe_extract(item, content_selector, default='')
                }
                if review.get('content'):
                    reviews.append(review)
            except Exception as e:
                logger.error(f"Error parsing review: {str(e)}")
        
        logger.info(f"Found {len(reviews)} reviews")
        return reviews

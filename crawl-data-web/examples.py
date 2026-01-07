"""
Example usage and test cases for the movie crawler
"""

from crawlers.imdb_crawler import IMDBCrawler
from crawlers.general_crawler import GeneralMovieCrawler
from database import db
from utils.logger import get_logger

logger = get_logger(__name__)

def example_crawl_with_custom_selectors():
    """Example: How to crawl a website with custom selectors"""
    
    logger.info("Example: Crawling with custom selectors")
    
    crawler = GeneralMovieCrawler()
    
    # Define your selectors based on target website HTML structure
    selectors = {
        'title': 'h1.movie-title',           # Adjust based on actual HTML
        'year': 'span.release-year',
        'duration': 'span.runtime',
        'description': 'div.plot-summary',
        'rating': 'span.imdb-rating',
        'genres': 'span.genre'
    }
    
    # Example URL (replace with actual movie URL)
    url = 'https://example-movie-site.com/movie/1'
    
    # Crawl movie details
    movie_data = crawler.crawl_movie_details(url, selectors)
    print(f"Movie data: {movie_data}")
    
    return movie_data

def example_crawl_reviews():
    """Example: How to crawl reviews"""
    
    logger.info("Example: Crawling reviews")
    
    crawler = GeneralMovieCrawler()
    
    url = 'https://example-movie-site.com/movie/1/reviews'
    
    # Define selectors for reviews
    reviews = crawler.crawl_reviews(
        url=url,
        review_selector='div.review-item',           # Container for each review
        reviewer_selector='span.reviewer-name',      # Reviewer name
        rating_selector='span.review-rating',        # Rating
        content_selector='p.review-content'          # Review text
    )
    
    print(f"Found {len(reviews)} reviews")
    for review in reviews:
        print(f"  - {review['reviewer_name']}: {review['rating']}/10")
    
    return reviews

def inspect_website_structure(url):
    """
    Utility function to inspect website HTML structure
    Use this to find the correct CSS selectors for your target website
    """
    from bs4 import BeautifulSoup
    from crawlers.base_crawler import BaseCrawler
    
    crawler = BaseCrawler()
    soup = crawler.get_soup(url)
    
    if soup:
        print(f"Website title: {soup.title.string if soup.title else 'N/A'}")
        print("\nHTML structure (first 500 chars):")
        print(soup.prettify()[:500])
    else:
        print("Failed to fetch website")

# Add more examples as needed

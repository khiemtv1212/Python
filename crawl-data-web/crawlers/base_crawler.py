from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from utils.helpers import fetch_page, create_session
from utils.logger import get_logger

logger = get_logger(__name__)

class BaseCrawler(ABC):
    """Base class for all crawlers"""
    
    def __init__(self):
        self.session = create_session()
    
    def get_soup(self, url):
        """Fetch and parse HTML"""
        html = fetch_page(url, self.session)
        if html is None:
            return None
        return BeautifulSoup(html, 'html.parser')
    
    @abstractmethod
    def crawl_movie_list(self, url):
        """Crawl list of movies"""
        pass
    
    @abstractmethod
    def crawl_movie_details(self, url):
        """Crawl detailed information about a movie"""
        pass
    
    def __del__(self):
        """Close session on deletion"""
        if self.session:
            self.session.close()

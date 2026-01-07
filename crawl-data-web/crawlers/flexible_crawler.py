"""
Flexible web crawler that works with any website configuration
"""

import time
from urllib.parse import urljoin, urlencode
from bs4 import BeautifulSoup
from crawlers.base_crawler import BaseCrawler
from utils.helpers import safe_extract, clean_text
from utils.logger import get_logger

logger = get_logger(__name__)

class FlexibleWebCrawler(BaseCrawler):
    """
    Universal crawler that works with any website using custom configuration
    """
    
    def __init__(self, config):
        """
        Initialize with configuration
        
        Args:
            config: CrawlerConfig object with website selectors and settings
        """
        super().__init__()
        self.config = config
        self.base_url = config.base_url
        
        # Apply custom headers
        if config.headers:
            self.session.headers.update(config.headers)
        
        # Apply custom cookies
        if config.cookies:
            for key, value in config.cookies.items():
                self.session.cookies.set(key, value)
    
    def crawl_items(self, url=None, limit=50, page=1):
        """
        Crawl list of items from a page
        
        Args:
            url: URL to crawl (if None, uses config.list_url)
            limit: Maximum number of items to crawl
            page: Page number for pagination
        
        Returns:
            List of item dictionaries
        """
        if url is None:
            url = self._build_list_url(page)
        
        logger.info(f"Crawling items from: {url}")
        soup = self.get_soup(url)
        
        if soup is None:
            logger.error("Failed to fetch page")
            return []
        
        items = []
        
        # Find item containers
        if not self.config.item_container:
            logger.error("item_container selector not configured")
            return []
        
        item_elements = soup.select(self.config.item_container)
        logger.info(f"Found {len(item_elements)} items")
        
        for item in item_elements[:limit]:
            try:
                item_data = self._parse_item(item)
                if item_data and item_data.get('title'):
                    items.append(item_data)
                    
                    # Respect delay
                    time.sleep(self.config.delay_between_items)
                    
            except Exception as e:
                logger.error(f"Error parsing item: {str(e)}")
        
        logger.info(f"Crawled {len(items)} items")
        return items
    
    def _parse_item(self, item_element):
        """Parse a single item from the list"""
        
        item_data = {}
        
        # Extract title
        if self.config.item_title:
            title = safe_extract(item_element, self.config.item_title, default='')
            item_data['title'] = clean_text(title)
        
        # Extract URL
        if self.config.item_url:
            url_elem = item_element.select_one(self.config.item_url)
            if url_elem:
                item_url = url_elem.get('href', '')
                if item_url and not item_url.startswith('http'):
                    item_url = urljoin(self.base_url, item_url)
                item_data['url'] = item_url
        
        # Extract image
        if self.config.item_image:
            img_elem = item_element.select_one(self.config.item_image)
            if img_elem:
                img_url = img_elem.get('src', '') or img_elem.get('data-src', '')
                if img_url and not img_url.startswith('http'):
                    img_url = urljoin(self.base_url, img_url)
                item_data['image_url'] = img_url
        
        # Extract rating
        if self.config.item_rating:
            rating = safe_extract(item_element, self.config.item_rating, default='')
            item_data['rating'] = clean_text(rating)
        
        # Extract short description
        if self.config.item_description_short:
            desc = safe_extract(item_element, self.config.item_description_short, default='')
            item_data['description_short'] = clean_text(desc)
        
        item_data['source'] = self.config.name
        
        return item_data
    
    def crawl_detail(self, detail_url):
        """
        Crawl detailed information about an item
        
        Args:
            detail_url: URL of the detail page
        
        Returns:
            Dictionary with detailed information
        """
        logger.info(f"Crawling detail: {detail_url}")
        soup = self.get_soup(detail_url)
        
        if soup is None:
            logger.error("Failed to fetch detail page")
            return {}
        
        try:
            detail_data = {'url': detail_url, 'source': self.config.name}
            
            # Extract all configured fields
            if self.config.detail_title:
                detail_data['title'] = safe_extract(soup, self.config.detail_title, default='')
            
            if self.config.detail_description:
                detail_data['description'] = safe_extract(soup, self.config.detail_description, default='')
            
            if self.config.detail_rating:
                detail_data['rating'] = safe_extract(soup, self.config.detail_rating, default='')
            
            if self.config.detail_year:
                detail_data['year'] = safe_extract(soup, self.config.detail_year, default='')
            
            if self.config.detail_genres:
                detail_data['genres'] = safe_extract(soup, self.config.detail_genres, default='')
            
            if self.config.detail_duration:
                detail_data['duration'] = safe_extract(soup, self.config.detail_duration, default='')
            
            if self.config.detail_image:
                img_elem = soup.select_one(self.config.detail_image)
                if img_elem:
                    img_url = img_elem.get('src', '') or img_elem.get('data-src', '')
                    if img_url and not img_url.startswith('http'):
                        img_url = urljoin(self.base_url, img_url)
                    detail_data['image_url'] = img_url
            
            if self.config.detail_status:
                detail_data['status'] = safe_extract(soup, self.config.detail_status, default='')
            
            if self.config.detail_episodes:
                detail_data['episodes'] = safe_extract(soup, self.config.detail_episodes, default='')
            
            # Clean all text fields
            for key in detail_data:
                if isinstance(detail_data[key], str):
                    detail_data[key] = clean_text(detail_data[key])
            
            logger.info(f"Crawled detail: {detail_data.get('title', 'Unknown')}")
            return detail_data
            
        except Exception as e:
            logger.error(f"Error crawling detail: {str(e)}")
            return {}
    
    def crawl_paginated(self, start_page=1, num_pages=1, items_per_page=50):
        """
        Crawl multiple pages with pagination
        
        Args:
            start_page: Starting page number
            num_pages: Number of pages to crawl
            items_per_page: Maximum items per page
        
        Returns:
            List of all crawled items
        """
        all_items = []
        
        for page in range(start_page, start_page + num_pages):
            logger.info(f"Crawling page {page}...")
            
            items = self.crawl_items(limit=items_per_page, page=page)
            all_items.extend(items)
            
            # Respect delay between pages
            if page < start_page + num_pages - 1:
                time.sleep(self.config.delay_between_pages)
        
        return all_items
    
    def _build_list_url(self, page=1):
        """Build list URL with pagination"""
        url = self.config.list_url
        
        pagination_config = self.config.pagination
        
        if pagination_config.get('type') == 'url_param':
            param_name = pagination_config.get('param_name', 'page')
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}{param_name}={page}"
        
        return url
    
    def inspect_page(self, url):
        """
        Inspect a page to help find correct selectors
        Returns HTML structure
        """
        logger.info(f"Inspecting page: {url}")
        soup = self.get_soup(url)
        
        if soup is None:
            return None
        
        return {
            'title': soup.title.string if soup.title else 'N/A',
            'html_preview': soup.prettify()[:2000],
            'all_links': [a.get('href', '') for a in soup.find_all('a')[:10]],
            'all_images': [img.get('src', '') for img in soup.find_all('img')[:10]],
        }

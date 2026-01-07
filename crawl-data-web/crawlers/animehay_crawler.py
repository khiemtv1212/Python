import time
from urllib.parse import urljoin, parse_qs, urlparse
from crawlers.base_crawler import BaseCrawler
from utils.helpers import safe_extract, clean_text
from utils.logger import get_logger

logger = get_logger(__name__)

class AnimeHayCrawler(BaseCrawler):
    """Crawler for AnimeHay.life - Vietnamese anime streaming site"""
    
    def __init__(self):
        super().__init__()
        self.base_url = 'https://animehay.life'
        self.session.headers.update({
            'Referer': self.base_url,
            'Accept-Language': 'vi-VN,vi;q=0.9'
        })
    
    def crawl_anime_list(self, url=None, limit=50):
        """
        Crawl list of animes from AnimeHay
        
        Args:
            url: URL to crawl (default: homepage)
            limit: Maximum number of animes to crawl
        
        Returns:
            List of anime info dicts
        """
        if url is None:
            url = self.base_url
        
        logger.info(f"Crawling anime list from: {url}")
        soup = self.get_soup(url)
        
        if soup is None:
            logger.error("Failed to fetch anime list")
            return []
        
        animes = []
        
        # AnimeHay uses specific structure for anime items
        # Look for anime cards/containers
        anime_items = soup.select('.phim-item, .film-item, .anime-card, [data-film]')
        logger.info(f"Found {len(anime_items)} anime items")
        
        for item in anime_items[:limit]:
            try:
                anime_info = self._parse_anime_item(item)
                if anime_info and anime_info.get('title'):
                    animes.append(anime_info)
            except Exception as e:
                logger.error(f"Error parsing anime item: {str(e)}")
        
        logger.info(f"Crawled {len(animes)} animes")
        return animes
    
    def _parse_anime_item(self, item):
        """Parse a single anime item from the list"""
        
        # Try multiple selector patterns for title
        title = (safe_extract(item, 'h3 a', default='') or
                safe_extract(item, '.phim-title a', default='') or
                safe_extract(item, 'a.film-name', default='') or
                safe_extract(item, 'h2 a', default=''))
        
        # Get anime URL
        title_link = item.select_one('h3 a, .phim-title a, a.film-name, h2 a')
        anime_url = title_link.get('href', '') if title_link else ''
        
        if not anime_url.startswith('http'):
            anime_url = urljoin(self.base_url, anime_url)
        
        # Get current episode info
        episode_info = safe_extract(item, '.episodes', default='')
        
        # Get rating
        rating = safe_extract(item, '.rating, .imdb-score, [data-rating]', default='')
        
        # Get genres
        genres = safe_extract(item, '.genres, .the-loai', default='')
        
        # Get cover image
        cover_img = item.select_one('img')
        cover_url = cover_img.get('src', '') if cover_img else ''
        
        return {
            'title': clean_text(title),
            'anime_hay_url': anime_url,
            'episode_info': clean_text(episode_info),
            'rating': clean_text(rating),
            'genres': clean_text(genres),
            'cover_image_url': cover_url,
            'source': 'animehay'
        }
    
    def crawl_anime_details(self, anime_url):
        """
        Crawl detailed information about an anime
        
        Args:
            anime_url: URL of anime detail page
        
        Returns:
            Dictionary with detailed anime info
        """
        logger.info(f"Crawling anime details: {anime_url}")
        soup = self.get_soup(anime_url)
        
        if soup is None:
            logger.error("Failed to fetch anime details")
            return {}
        
        try:
            anime_data = {
                'anime_hay_url': anime_url,
                'source': 'animehay'
            }
            
            # Extract anime ID from URL
            # Format: /thong-tin-phim/anime-name-id.html
            path = urlparse(anime_url).path
            anime_id = path.split('-')[-1].replace('.html', '')
            anime_data['anime_hay_id'] = anime_id
            
            # Title
            title = (safe_extract(soup, 'h1.title-film', default='') or
                    safe_extract(soup, 'h1', default=''))
            anime_data['title'] = clean_text(title)
            
            # Description/Synopsis
            description = (safe_extract(soup, '.synopsis', default='') or
                          safe_extract(soup, '.description', default='') or
                          safe_extract(soup, '.content-detail', default=''))
            anime_data['description'] = clean_text(description)
            
            # Extract info from details table/section
            info_section = soup.select_one('.info-item, .thong-tin-phim, .film-info')
            if info_section:
                # Status
                status_text = safe_extract(info_section, '.status', default='')
                anime_data['status'] = clean_text(status_text)
                
                # Episodes
                episodes = safe_extract(info_section, '.episodes-count, .so-tap', default='')
                anime_data['episodes_aired'] = self._extract_number(clean_text(episodes))
                
                # Year
                year = safe_extract(info_section, '.year, .nam-phat-hanh', default='')
                anime_data['year'] = self._extract_number(clean_text(year))
                
                # Genres
                genres = safe_extract(info_section, '.genres, .the-loai', default='')
                anime_data['genres'] = clean_text(genres)
                
                # Rating
                rating = safe_extract(info_section, '.rating, .imdb-score', default='')
                anime_data['rating'] = self._extract_float(clean_text(rating))
            
            # Cover image
            cover_img = soup.select_one('img.cover, img.poster, img[alt*="poster"]')
            if cover_img:
                cover_url = cover_img.get('src', '') or cover_img.get('data-src', '')
                anime_data['cover_image_url'] = cover_url
            
            # Check if ongoing
            anime_data['is_ongoing'] = 'ongoing' in str(anime_data.get('status', '')).lower()
            
            logger.info(f"Crawled anime: {anime_data['title']}")
            return anime_data
            
        except Exception as e:
            logger.error(f"Error crawling anime details: {str(e)}")
            return {}
    
    def crawl_episodes(self, anime_url, limit=None):
        """
        Crawl all episodes of an anime
        
        Args:
            anime_url: URL of anime page
            limit: Maximum number of episodes to crawl
        
        Returns:
            List of episode info dicts
        """
        logger.info(f"Crawling episodes from: {anime_url}")
        soup = self.get_soup(anime_url)
        
        if soup is None:
            return []
        
        episodes = []
        
        # Find episode list
        episode_list = soup.select('.tap-list, .episode-list, .ep-list')
        
        for ep_container in episode_list:
            ep_items = ep_container.select('.tap-item, .episode-item, li a, [data-episode]')
            
            for idx, ep_item in enumerate(ep_items):
                if limit and len(episodes) >= limit:
                    break
                
                try:
                    ep_info = self._parse_episode_item(ep_item, idx + 1)
                    if ep_info:
                        episodes.append(ep_info)
                except Exception as e:
                    logger.error(f"Error parsing episode: {str(e)}")
            
            if limit and len(episodes) >= limit:
                break
        
        logger.info(f"Crawled {len(episodes)} episodes")
        return episodes
    
    def _parse_episode_item(self, ep_item, episode_num):
        """Parse a single episode item"""
        
        # Episode title/name
        ep_title = safe_extract(ep_item, 'a', default='')
        
        # Episode URL
        ep_link = ep_item.select_one('a')
        ep_url = ep_link.get('href', '') if ep_link else ''
        
        if ep_url and not ep_url.startswith('http'):
            ep_url = urljoin(self.base_url, ep_url)
        
        return {
            'episode_number': episode_num,
            'episode_title': clean_text(ep_title),
            'episode_url': ep_url
        }
    
    @staticmethod
    def _extract_number(text):
        """Extract first number from text"""
        import re
        match = re.search(r'\d+', text)
        return int(match.group()) if match else None
    
    @staticmethod
    def _extract_float(text):
        """Extract first float from text"""
        import re
        match = re.search(r'\d+\.?\d*', text)
        return float(match.group()) if match else None
    
    def crawl_category(self, category_slug, limit=50):
        """
        Crawl animes from a specific category
        
        Args:
            category_slug: Category slug (e.g., 'anime-1', 'cn-animation-34')
            limit: Maximum number of animes to crawl
        
        Returns:
            List of anime info dicts
        """
        url = f"{self.base_url}/the-loai/{category_slug}.html"
        logger.info(f"Crawling category: {url}")
        return self.crawl_anime_list(url, limit)
    
    def crawl_newest(self, limit=50):
        """Crawl newest animes"""
        return self.crawl_anime_list(f"{self.base_url}/", limit)
    
    def search_anime(self, query):
        """
        Search for anime by name
        
        Args:
            query: Search query
        
        Returns:
            List of search results
        """
        logger.info(f"Searching for: {query}")
        # AnimeHay search typically uses query parameter
        search_url = f"{self.base_url}/search?q={query}"
        return self.crawl_anime_list(search_url, limit=20)

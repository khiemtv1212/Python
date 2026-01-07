"""
Configuration management for website crawling
"""

import json
import os
from utils.logger import get_logger

logger = get_logger(__name__)

class CrawlerConfig:
    """Configuration for crawling a specific website"""
    
    def __init__(self, config_dict):
        self.name = config_dict.get('name', 'Unknown')
        self.base_url = config_dict.get('base_url', '')
        self.list_url = config_dict.get('list_url', '')  # URL pattern for list pages
        self.pagination = config_dict.get('pagination', {})
        
        # Selectors for item list
        self.item_container = config_dict.get('selectors', {}).get('item_container', '')
        self.item_title = config_dict.get('selectors', {}).get('item_title', '')
        self.item_url = config_dict.get('selectors', {}).get('item_url', '')
        self.item_image = config_dict.get('selectors', {}).get('item_image', '')
        self.item_rating = config_dict.get('selectors', {}).get('item_rating', '')
        self.item_description_short = config_dict.get('selectors', {}).get('item_description_short', '')
        
        # Selectors for detail page
        self.detail_title = config_dict.get('detail_selectors', {}).get('title', '')
        self.detail_description = config_dict.get('detail_selectors', {}).get('description', '')
        self.detail_rating = config_dict.get('detail_selectors', {}).get('rating', '')
        self.detail_year = config_dict.get('detail_selectors', {}).get('year', '')
        self.detail_genres = config_dict.get('detail_selectors', {}).get('genres', '')
        self.detail_duration = config_dict.get('detail_selectors', {}).get('duration', '')
        self.detail_image = config_dict.get('detail_selectors', {}).get('image', '')
        self.detail_status = config_dict.get('detail_selectors', {}).get('status', '')
        self.detail_episodes = config_dict.get('detail_selectors', {}).get('episodes', '')
        
        # Delay settings
        self.delay_between_items = config_dict.get('delay_between_items', 1)
        self.delay_between_pages = config_dict.get('delay_between_pages', 2)
        
        # Other settings
        self.enable_javascript = config_dict.get('enable_javascript', False)
        self.headers = config_dict.get('headers', {})
        self.cookies = config_dict.get('cookies', {})
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'name': self.name,
            'base_url': self.base_url,
            'list_url': self.list_url,
            'pagination': self.pagination,
            'selectors': {
                'item_container': self.item_container,
                'item_title': self.item_title,
                'item_url': self.item_url,
                'item_image': self.item_image,
                'item_rating': self.item_rating,
                'item_description_short': self.item_description_short,
            },
            'detail_selectors': {
                'title': self.detail_title,
                'description': self.detail_description,
                'rating': self.detail_rating,
                'year': self.detail_year,
                'genres': self.detail_genres,
                'duration': self.detail_duration,
                'image': self.detail_image,
                'status': self.detail_status,
                'episodes': self.detail_episodes,
            },
            'delay_between_items': self.delay_between_items,
            'delay_between_pages': self.delay_between_pages,
            'enable_javascript': self.enable_javascript,
            'headers': self.headers,
            'cookies': self.cookies,
        }


class ConfigManager:
    """Manage website crawler configurations"""
    
    def __init__(self, config_dir='config/website_configs'):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
    
    def save_config(self, config_name, config):
        """Save configuration to JSON file"""
        try:
            file_path = os.path.join(self.config_dir, f"{config_name}.json")
            
            config_data = config.to_dict() if isinstance(config, CrawlerConfig) else config
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Configuration saved: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def load_config(self, config_name):
        """Load configuration from JSON file"""
        try:
            file_path = os.path.join(self.config_dir, f"{config_name}.json")
            
            if not os.path.exists(file_path):
                logger.error(f"Configuration file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            logger.info(f"Configuration loaded: {file_path}")
            return CrawlerConfig(config_data)
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return None
    
    def list_configs(self):
        """List all available configurations"""
        try:
            configs = []
            for file in os.listdir(self.config_dir):
                if file.endswith('.json'):
                    configs.append(file[:-5])  # Remove .json extension
            return configs
        except Exception as e:
            logger.error(f"Error listing configurations: {str(e)}")
            return []
    
    def delete_config(self, config_name):
        """Delete a configuration"""
        try:
            file_path = os.path.join(self.config_dir, f"{config_name}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Configuration deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting configuration: {str(e)}")
            return False
    
    @staticmethod
    def create_template(name, base_url):
        """Create a configuration template"""
        return {
            'name': name,
            'base_url': base_url,
            'list_url': f'{base_url}',
            'pagination': {
                'type': 'url_param',  # 'url_param', 'next_button', 'load_more'
                'param_name': 'page',
                'start_page': 1,
            },
            'selectors': {
                'item_container': '',  # e.g., 'div.movie-item', 'li.product'
                'item_title': '',      # e.g., 'h2.title', 'a.name'
                'item_url': '',        # e.g., 'a', 'a.link'
                'item_image': '',      # e.g., 'img', 'img.thumbnail'
                'item_rating': '',     # e.g., 'span.rating', 'div.score'
                'item_description_short': '',
            },
            'detail_selectors': {
                'title': '',           # e.g., 'h1.title'
                'description': '',     # e.g., 'div.description', 'p.synopsis'
                'rating': '',          # e.g., 'span.rating-score'
                'year': '',            # e.g., 'span.year'
                'genres': '',          # e.g., 'span.genre', 'div.tags'
                'duration': '',        # e.g., 'span.duration'
                'image': '',           # e.g., 'img.cover', 'img.poster'
                'status': '',          # e.g., 'span.status'
                'episodes': '',        # e.g., 'span.episodes', 'div.ep-count'
            },
            'delay_between_items': 1,
            'delay_between_pages': 2,
            'enable_javascript': False,
            'headers': {},
            'cookies': {}
        }

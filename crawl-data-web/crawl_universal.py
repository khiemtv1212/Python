"""
Universal crawler script - crawl any website with custom configuration
"""

import json
from config.crawler_config import ConfigManager, CrawlerConfig
from crawlers.flexible_crawler import FlexibleWebCrawler
from utils.selector_finder import SelectorFinder, print_selector_guide
from utils.logger import get_logger
from database import db
from models.movie import Movie, Rating

logger = get_logger(__name__)

def create_website_config(name, base_url):
    """
    Create a new website configuration interactively
    
    Args:
        name: Website name (e.g., 'myanimelist', 'boxmovies')
        base_url: Website base URL
    """
    logger.info(f"Creating configuration for: {name}")
    
    config_manager = ConfigManager()
    template = ConfigManager.create_template(name, base_url)
    
    print(f"\n📝 Creating configuration for '{name}'")
    print("=" * 60)
    print("\nTo find correct selectors, use the selector finder:")
    print(">>> finder = SelectorFinder()")
    print(f">>> finder.inspect_elements('{base_url}')\n")
    
    # Alternatively, show the template
    template_path = f"config/website_configs/{name}_template.json"
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Template created at: {template_path}")
    print("   Edit this file with correct CSS selectors from your website")
    
    return template

def find_selectors_interactive(website_url):
    """
    Interactive selector finder
    
    Args:
        website_url: URL to inspect
    """
    print(f"\n🔍 Inspecting: {website_url}")
    print("=" * 60)
    
    finder = SelectorFinder()
    
    # Inspect the page
    result = finder.inspect_elements(website_url, limit=5)
    
    if result is None:
        print("❌ Failed to inspect page")
        return
    
    print(f"\n📄 Page title: {result['page_title']}")
    
    # Show element samples
    for elem_type in ['h2', 'a', 'div']:
        elements = result.get(elem_type, [])
        if elements:
            print(f"\n{elem_type.upper()} elements found: {len(elements)}")
            for i, elem in enumerate(elements[:3], 1):
                print(f"  {i}. Text: {elem['text'][:50]}")
                print(f"     CSS: {elem['css_selector']}")
                if elem['classes']:
                    print(f"     Classes: {elem['classes']}")

def crawl_with_config(config_name, list_url=None, detail_crawl=False, limit=20, pages=1):
    """
    Crawl a website using saved configuration
    
    Args:
        config_name: Name of saved configuration
        list_url: Override list URL
        detail_crawl: Whether to crawl detail pages
        limit: Max items per page
        pages: Number of pages to crawl
    """
    logger.info(f"Starting crawl with config: {config_name}")
    
    config_manager = ConfigManager()
    config = config_manager.load_config(config_name)
    
    if config is None:
        print(f"❌ Configuration not found: {config_name}")
        return
    
    print(f"\n🚀 Crawling with configuration: {config.name}")
    print(f"   Website: {config.base_url}")
    print(f"   Pages: {pages}, Items/page: {limit}")
    print("=" * 60)
    
    # Initialize crawler
    crawler = FlexibleWebCrawler(config)
    
    # Override list URL if provided
    if list_url:
        config.list_url = list_url
    
    all_items = []
    
    # Crawl pages
    for page in range(1, pages + 1):
        print(f"\n📄 Crawling page {page}...")
        items = crawler.crawl_items(limit=limit, page=page)
        
        print(f"   Found {len(items)} items")
        
        if detail_crawl and items:
            print(f"   Crawling details for {len(items)} items...")
            for i, item in enumerate(items, 1):
                if item.get('url'):
                    detail = crawler.crawl_detail(item['url'])
                    item.update(detail)
                    print(f"     {i}/{len(items)}", end='\r')
        
        all_items.extend(items)
    
    print(f"\n✅ Crawled total: {len(all_items)} items")
    
    # Save to JSON for review
    output_file = f"data/{config_name}_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Data saved to: {output_file}")
    
    return all_items

def save_to_database(config_name, items):
    """Save crawled items to database"""
    logger.info(f"Saving {len(items)} items to database")
    
    session = db.get_session()
    
    try:
        for item in items:
            # Try to save as movie (flexible)
            movie = Movie(
                title=item.get('title', '')[:255],
                description=item.get('description', ''),
                imdb_url=item.get('url', '')[:500],
                poster_url=item.get('image_url', '')[:500] if item.get('image_url') else '',
            )
            
            session.add(movie)
        
        session.commit()
        logger.info(f"Saved {len(items)} items to database")
        
    except Exception as e:
        logger.error(f"Error saving to database: {str(e)}")
        session.rollback()
    finally:
        session.close()

def list_saved_configs():
    """List all saved website configurations"""
    config_manager = ConfigManager()
    configs = config_manager.list_configs()
    
    print("\n📋 Saved Configurations:")
    print("=" * 60)
    
    if not configs:
        print("No configurations saved yet")
        return
    
    for config_name in configs:
        config = config_manager.load_config(config_name)
        if config:
            print(f"  • {config_name}")
            print(f"    Website: {config.base_url}")
    
    print()

def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Universal Web Crawler")
    logger.info("=" * 60)
    
    # Create database tables
    db.create_tables()
    
    # Example: Create config for a website
    # config_data = create_website_config('example_site', 'https://example.com/movies')
    
    # Example: Find selectors
    # find_selectors_interactive('https://example.com')
    
    # Example: Crawl with saved config
    # crawl_with_config('animehay', detail_crawl=True, limit=5, pages=1)
    
    # List saved configs
    # list_saved_configs()
    
    print_selector_guide()
    
    db.close()

if __name__ == '__main__':
    main()

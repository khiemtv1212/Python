"""
Web crawling with automatic image downloading
Examples of how to crawl data AND download images simultaneously
"""

import json
from pathlib import Path
from crawlers.flexible_crawler import FlexibleWebCrawler
from crawlers.animehay_crawler import AnimeHayCrawler
from config.crawler_config import ConfigManager
from utils.image_downloader import ImageDownloader, extract_and_download_images
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# PHƯƠNG PHÁP 1: Dùng FlexibleWebCrawler + ImageDownloader
# ============================================================================

def crawl_phimhay_with_images(pages=2, max_images=None, detail_crawl=True):
    """
    Crawl PhimHay.co.in AND download images
    
    Args:
        pages: Number of pages to crawl
        max_images: Limit images to download (None = all)
        detail_crawl: Also crawl detail pages
    """
    print("=" * 70)
    print("CRAWLING PHIMHAY.CO.IN WITH IMAGE DOWNLOADS")
    print("=" * 70)
    
    # Initialize crawler and downloader
    config_mgr = ConfigManager()
    config = config_mgr.load_config('phimhay')
    crawler = FlexibleWebCrawler(config)
    downloader = ImageDownloader('downloads/phimhay')
    
    all_items = []
    
    # Crawl multiple pages
    for page in range(1, pages + 1):
        print(f"\n[Page {page}] Crawling...")
        try:
            items = crawler.crawl_items(page=page, limit=20)
            print(f"Found {len(items)} items on page {page}")
            all_items.extend(items)
        except Exception as e:
            logger.error(f"Error crawling page {page}: {e}")
    
    print(f"\nTotal items crawled: {len(all_items)}")
    
    # Download images from list page
    print(f"\n[Images] Downloading {len(all_items)} images...")
    image_results = extract_and_download_images(
        all_items,
        image_field='image',
        subfolder='list_images',
        downloader=downloader,
        max_images=max_images
    )
    
    print(f"✓ Downloaded: {image_results['success_count']}")
    print(f"✗ Failed: {image_results['failed_count']}")
    
    # Crawl detail pages and download detail images
    if detail_crawl:
        print(f"\n[Detail Pages] Crawling details for {len(all_items)} items...")
        for i, item in enumerate(all_items[:max_images] if max_images else all_items, 1):
            try:
                detail_url = item.get('url')
                if not detail_url:
                    continue
                
                print(f"  [{i}] {item.get('title', 'Unknown')[:40]}...")
                details = crawler.crawl_detail(detail_url)
                
                # Merge details
                item.update(details)
                
                # Download detail images if available
                if 'image' in details and details['image']:
                    result = downloader.download_image(
                        details['image'],
                        subfolder='detail_images',
                        filename=f"{item.get('title', 'movie')[:30]}.jpg"
                    )
                    if result['success']:
                        item['detail_image_local'] = result['local_path']
                
            except Exception as e:
                logger.error(f"Error crawling detail: {e}")
    
    # Save results
    output_file = Path('data/phimhay_with_images.json')
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Results saved to: {output_file}")
    
    # Show stats
    stats = downloader.get_download_stats()
    print(f"\n📊 Download Statistics:")
    print(f"   Total images: {stats['total_files']}")
    print(f"   Total size: {stats['total_size_mb']} MB")
    print(f"   Location: {stats['base_dir']}")


# ============================================================================
# PHƯƠNG PHÁP 2: Crawl AnimeHay + Download anime images + episode thumbnails
# ============================================================================

def crawl_animehay_with_images(category='anime-1', pages=2, max_images=None):
    """
    Crawl AnimeHay AND download anime poster + episode thumbnails
    
    Args:
        category: Anime category (anime-1, cn-animation-34, etc.)
        pages: Number of pages to crawl
        max_images: Limit images to download
    """
    print("=" * 70)
    print("CRAWLING ANIMEHAY WITH IMAGE DOWNLOADS")
    print("=" * 70)
    
    crawler = AnimeHayCrawler()
    downloader = ImageDownloader('downloads/animehay')
    
    all_animes = []
    
    # Crawl animes
    print(f"\n[Animes] Crawling from {category}...")
    try:
        animes = crawler.crawl_category(category, pages=pages, limit=20)
        print(f"Found {len(animes)} animes")
        all_animes.extend(animes)
    except Exception as e:
        logger.error(f"Error crawling animes: {e}")
    
    # Download anime posters
    print(f"\n[Posters] Downloading {len(all_animes)} anime posters...")
    poster_results = extract_and_download_images(
        all_animes,
        image_field='image',
        subfolder='anime_posters',
        downloader=downloader,
        max_images=max_images
    )
    
    print(f"✓ Downloaded: {poster_results['success_count']}")
    print(f"✗ Failed: {poster_results['failed_count']}")
    
    # Crawl episodes and download thumbnails
    print(f"\n[Episodes] Crawling episodes...")
    for i, anime in enumerate(all_animes[:max_images] if max_images else all_animes, 1):
        try:
            anime_url = anime.get('url')
            if not anime_url:
                continue
            
            print(f"  [{i}] {anime.get('title', 'Unknown')[:40]}...")
            
            # Crawl episodes
            episodes = crawler.crawl_episodes(anime_url)
            anime['episodes'] = episodes
            
            # Download first few episode thumbnails
            for ep in episodes[:3]:  # Only first 3 episodes
                ep_image = ep.get('image')
                if ep_image:
                    result = downloader.download_image(
                        ep_image,
                        subfolder='episode_thumbnails'
                    )
                    if result['success']:
                        ep['image_local'] = result['local_path']
            
            print(f"      ✓ {len(episodes)} episodes found")
            
        except Exception as e:
            logger.error(f"Error crawling episodes: {e}")
    
    # Save results
    output_file = Path('data/animehay_with_images.json')
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_animes, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Results saved to: {output_file}")
    
    # Show stats
    stats = downloader.get_download_stats()
    print(f"\n📊 Download Statistics:")
    print(f"   Total images: {stats['total_files']}")
    print(f"   Total size: {stats['total_size_mb']} MB")
    print(f"   Location: {stats['base_dir']}")


# ============================================================================
# PHƯƠNG PHÁP 3: Custom website + images
# ============================================================================

def crawl_custom_website_with_images(config_name, pages=1, image_field='image'):
    """
    Generic method to crawl any configured website with images
    
    Args:
        config_name: Name of config file (without .json)
        pages: Number of pages to crawl
        image_field: Field name containing image URL
    """
    print("=" * 70)
    print(f"CRAWLING {config_name.upper()} WITH IMAGE DOWNLOADS")
    print("=" * 70)
    
    # Load config
    config_mgr = ConfigManager()
    config = config_mgr.load_config(config_name)
    
    crawler = FlexibleWebCrawler(config)
    downloader = ImageDownloader(f'downloads/{config_name}')
    
    all_items = []
    
    # Crawl pages
    print(f"\n[Pages] Crawling {pages} pages...")
    for page in range(1, pages + 1):
        try:
            items = crawler.crawl_items(page=page, limit=20)
            print(f"  Page {page}: {len(items)} items")
            all_items.extend(items)
        except Exception as e:
            logger.error(f"Error on page {page}: {e}")
    
    print(f"Total items: {len(all_items)}")
    
    # Download images
    print(f"\n[Images] Downloading images...")
    results = extract_and_download_images(
        all_items,
        image_field=image_field,
        subfolder='items',
        downloader=downloader
    )
    
    print(f"✓ Downloaded: {results['success_count']}")
    print(f"✗ Failed: {results['failed_count']}")
    
    # Save
    output_file = Path(f'data/{config_name}_with_images.json')
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Results: {output_file}")
    
    # Stats
    stats = downloader.get_download_stats()
    print(f"\n📊 Statistics: {stats['total_files']} images, {stats['total_size_mb']} MB")


# ============================================================================
# EXAMPLES - Chạy các ví dụ này
# ============================================================================

if __name__ == '__main__':
    import sys
    
    print("\n" + "=" * 70)
    print("WEB CRAWLER WITH IMAGE DOWNLOADS")
    print("=" * 70)
    print("\nAvailable examples:")
    print("  1. crawl_phimhay_with_images(pages=2, max_images=10)")
    print("  2. crawl_animehay_with_images(category='anime-1', pages=2)")
    print("  3. crawl_custom_website_with_images('phimhay', pages=2)")
    print("\nExample usage:")
    print("  python crawl_with_images.py")
    print("=" * 70 + "\n")
    
    # Run example
    try:
        print("Starting crawl_phimhay_with_images...")
        crawl_phimhay_with_images(pages=1, max_images=5, detail_crawl=False)
        
        print("\n" + "=" * 70)
        print("✓ Crawling completed!")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"Error: {e}")

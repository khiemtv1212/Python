"""
Batch image downloading examples
Tải nhiều hình cùng lúc vào 1 folder
"""

import json
from pathlib import Path
from utils.image_downloader import ImageDownloader, extract_and_download_images
from crawlers.flexible_crawler import FlexibleWebCrawler
from crawlers.animehay_crawler import AnimeHayCrawler
from config.crawler_config import ConfigManager
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# PHƯƠNG PHÁP 1: Tải nhiều hình song song (PARALLEL) - NHANH NHẤT
# ============================================================================

def batch_download_phimhay_parallel(pages=2, max_workers=8):
    """
    Crawl PhimHay + tải ALL hình CÙNG LÚC vào 1 folder
    
    Args:
        pages: Số trang crawl
        max_workers: Số hình tải song song (8 = tải 8 cái cùng 1 lúc)
    """
    print("=" * 70)
    print("PHIMHAY: CRAWL + BATCH DOWNLOAD (PARALLEL)")
    print("=" * 70)
    
    # Crawl dữ liệu
    print("\n[1/3] Crawling data...")
    config_mgr = ConfigManager()
    config = config_mgr.load_config('phimhay')
    crawler = FlexibleWebCrawler(config)
    
    all_items = []
    for page in range(1, pages + 1):
        items = crawler.crawl_items(page=page, limit=20)
        all_items.extend(items)
        print(f"  Page {page}: {len(items)} items")
    
    print(f"\nTotal: {len(all_items)} items")
    
    # Collect tất cả URLs hình
    print("\n[2/3] Collecting image URLs...")
    image_urls = [item.get('image') for item in all_items if item.get('image')]
    print(f"Found {len(image_urls)} images")
    
    # TẢI SONG SONG - MỘT LẦU
    print(f"\n[3/3] Downloading {len(image_urls)} images in parallel ({max_workers} workers)...")
    downloader = ImageDownloader('downloads/phimhay_batch', max_workers=max_workers)
    
    result = downloader.download_images_parallel(
        image_urls,
        subfolder='posters',
        max_workers=max_workers,
        show_progress=True
    )
    
    # Results
    print("\n" + "=" * 70)
    print(f"✓ Success: {result['success_count']}/{result['total_attempted']}")
    print(f"✗ Failed: {result['failed_count']}/{result['total_attempted']}")
    print(f"📊 Total size: {result['total_size_mb']} MB")
    print("=" * 70)
    
    # Add local paths to items
    local_paths = [r['local_path'] for r in result['results']]
    for item, local_path in zip(all_items, local_paths):
        if local_path:
            item['image_local'] = local_path
    
    # Save JSON
    output_file = Path('data/phimhay_batch_parallel.json')
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved to: {output_file}")
    return all_items, result


# ============================================================================
# PHƯƠNG PHÁP 2: Tải từng group hình vào 1 folder
# ============================================================================

def batch_download_animehay_parallel(category='anime-1', pages=2, max_workers=6):
    """
    Crawl AnimeHay + tải ALL poster + episodes vào 1 folder
    
    Args:
        category: Category anime (anime-1, cn-animation-34, etc.)
        pages: Số trang
        max_workers: Worker threads
    """
    print("=" * 70)
    print("ANIMEHAY: CRAWL + BATCH DOWNLOAD (PARALLEL)")
    print("=" * 70)
    
    # Crawl animes
    print("\n[1/2] Crawling animes...")
    crawler = AnimeHayCrawler()
    animes = crawler.crawl_category(category, pages=pages, limit=20)
    print(f"Found {len(animes)} animes")
    
    # Collect tất cả hình (poster + episodes)
    print("\n[2/2] Downloading all images in parallel...")
    downloader = ImageDownloader('downloads/animehay_batch', max_workers=max_workers)
    
    all_images = []
    
    # Poster hình
    poster_urls = [a.get('image') for a in animes if a.get('image')]
    all_images.extend(poster_urls)
    
    # Episode hình
    print(f"  Crawling episodes...")
    for i, anime in enumerate(animes, 1):
        try:
            anime_url = anime.get('url')
            if not anime_url:
                continue
            episodes = crawler.crawl_episodes(anime_url)
            anime['episodes'] = episodes
            
            # Collect episode images
            for ep in episodes:
                ep_image = ep.get('image')
                if ep_image:
                    all_images.append(ep_image)
            
            print(f"    [{i}] {len(episodes)} episodes")
        except Exception as e:
            logger.error(f"Error crawling episodes: {e}")
    
    print(f"\nTotal images to download: {len(all_images)}")
    
    # DOWNLOAD ALL CÙNG LÚC
    result = downloader.download_images_parallel(
        all_images,
        subfolder='images',
        max_workers=max_workers,
        show_progress=True
    )
    
    # Results
    print("\n" + "=" * 70)
    print(f"✓ Success: {result['success_count']}/{result['total_attempted']}")
    print(f"✗ Failed: {result['failed_count']}/{result['total_attempted']}")
    print(f"📊 Total size: {result['total_size_mb']} MB")
    print("=" * 70)
    
    # Save
    output_file = Path('data/animehay_batch_parallel.json')
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(animes, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved to: {output_file}")
    return animes, result


# ============================================================================
# PHƯƠNG PHÁP 3: Flexible batch download cho website bất kỳ
# ============================================================================

def batch_download_website(config_name, pages=1, max_workers=4):
    """
    Crawl + tải batch cho website tùy ý
    
    Args:
        config_name: Tên config (phimhay, animehay, etc.)
        pages: Số trang
        max_workers: Worker threads
    """
    print("=" * 70)
    print(f"WEBSITE: {config_name.upper()} - BATCH DOWNLOAD")
    print("=" * 70)
    
    # Load config
    config_mgr = ConfigManager()
    config = config_mgr.load_config(config_name)
    crawler = FlexibleWebCrawler(config)
    
    # Crawl
    print("\n[1/2] Crawling...")
    all_items = []
    for page in range(1, pages + 1):
        items = crawler.crawl_items(page=page, limit=20)
        all_items.extend(items)
        print(f"  Page {page}: {len(items)} items")
    
    # Collect images
    print("\n[2/2] Batch downloading images...")
    image_urls = [item.get('image') for item in all_items if item.get('image')]
    print(f"Total images: {len(image_urls)}")
    
    # Download parallel
    downloader = ImageDownloader(f'downloads/{config_name}_batch', max_workers=max_workers)
    result = downloader.download_images_parallel(
        image_urls,
        subfolder='items',
        max_workers=max_workers,
        show_progress=True
    )
    
    # Results
    print("\n" + "=" * 70)
    print(f"✓ Success: {result['success_count']}/{result['total_attempted']}")
    print(f"✗ Failed: {result['failed_count']}/{result['total_attempted']}")
    print(f"📊 Total size: {result['total_size_mb']} MB")
    print("=" * 70)
    
    # Add paths
    local_paths = [r['local_path'] for r in result['results']]
    for item, local_path in zip(all_items, local_paths):
        if local_path:
            item['image_local'] = local_path
    
    # Save
    output_file = Path(f'data/{config_name}_batch_parallel.json')
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved to: {output_file}")
    return all_items, result


# ============================================================================
# PHƯƠNG PHÁP 4: TẢI CHỈ TỪ DANH SÁCH URLs (SIÊU NHANH)
# ============================================================================

def batch_download_from_urls(image_urls, folder_name='batch_images', max_workers=8):
    """
    Tải một loạt hình từ danh sách URLs
    
    Args:
        image_urls: List of image URLs
        folder_name: Folder name để lưu
        max_workers: Worker threads
        
    Example:
        urls = [
            'https://example.com/img1.jpg',
            'https://example.com/img2.jpg',
            'https://example.com/img3.jpg',
        ]
        batch_download_from_urls(urls, 'my_images', max_workers=10)
    """
    print("=" * 70)
    print(f"BATCH DOWNLOAD: {len(image_urls)} images")
    print("=" * 70)
    
    downloader = ImageDownloader(f'downloads/{folder_name}', max_workers=max_workers)
    
    print(f"\nDownloading {len(image_urls)} images with {max_workers} workers...\n")
    
    result = downloader.download_images_parallel(
        image_urls,
        subfolder='images',
        max_workers=max_workers,
        show_progress=True
    )
    
    print("\n" + "=" * 70)
    print(f"✓ Success: {result['success_count']}/{result['total_attempted']}")
    print(f"✗ Failed: {result['failed_count']}/{result['total_attempted']}")
    print(f"📊 Total size: {result['total_size_mb']} MB")
    print(f"Location: downloads/{folder_name}/images/")
    print("=" * 70)
    
    return result


# ============================================================================
# EXAMPLES
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("BATCH IMAGE DOWNLOADER - Tải nhiều hình cùng lúc")
    print("=" * 70)
    print("\nAvailable methods:")
    print("  1. batch_download_phimhay_parallel(pages=2, max_workers=8)")
    print("  2. batch_download_animehay_parallel(category='anime-1', pages=2)")
    print("  3. batch_download_website('phimhay', pages=2, max_workers=4)")
    print("  4. batch_download_from_urls(urls, folder_name='my_images')")
    print("\n" + "=" * 70 + "\n")
    
    try:
        # Example 1: PhimHay batch download
        print("Running: batch_download_phimhay_parallel...")
        items, result = batch_download_phimhay_parallel(pages=1, max_workers=4)
        
        print("\n✓ Batch download completed successfully!")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"Error: {e}")

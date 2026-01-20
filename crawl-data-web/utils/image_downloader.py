"""
Image downloader utility for web crawling
Handles downloading and saving images with proper error handling
Supports concurrent downloads for better performance
"""

import os
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
from .logger import get_logger
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import threading

logger = get_logger(__name__)


class ImageDownloader:
    """Download and save images from URLs"""
    
    def __init__(self, base_dir='downloads/images', timeout=10, delay=0.5, 
                 max_workers=4):
        """
        Initialize image downloader
        
        Args:
            base_dir: Base directory to save images
            timeout: Request timeout in seconds
            delay: Delay between downloads in seconds (for single downloads)
            max_workers: Number of concurrent download threads (default: 4)
        """
        self.base_dir = Path(base_dir)
        self.timeout = timeout
        self.delay = delay
        self.max_workers = max_workers
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()  # Thread-safe file operations
        
    def download_image(self, url, subfolder='', filename=None):
        """
        Download a single image
        
        Args:
            url: Image URL to download
            subfolder: Subfolder within base_dir (e.g., 'phimhay', 'animehay')
            filename: Custom filename. If None, uses URL filename
            
        Returns:
            dict: {
                'success': bool,
                'url': original_url,
                'local_path': path/to/saved/file or None,
                'error': error message or None,
                'file_size': size in bytes
            }
        """
        try:
            if not url or not isinstance(url, str):
                return {
                    'success': False,
                    'url': url,
                    'local_path': None,
                    'error': 'Invalid URL',
                    'file_size': 0
                }
            
            # Make sure URL is absolute
            if url.startswith('/'):
                url = 'https:' + url if url.startswith('//') else 'https://example.com' + url
            
            # Create save directory
            save_dir = self.base_dir / subfolder if subfolder else self.base_dir
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine filename
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    # Use URL hash if no filename in URL
                    import hashlib
                    filename = hashlib.md5(url.encode()).hexdigest()[:12] + '.jpg'
            
            file_path = save_dir / filename
            
            # Skip if already exists
            if file_path.exists():
                logger.info(f"Image already exists: {file_path}")
                return {
                    'success': True,
                    'url': url,
                    'local_path': str(file_path),
                    'error': None,
                    'file_size': file_path.stat().st_size
                }
            
            # Download image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Save image
            file_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        file_size += len(chunk)
            
            logger.info(f"Downloaded image: {filename} ({file_size} bytes)")
            
            # Delay between downloads
            time.sleep(self.delay)
            
            return {
                'success': True,
                'url': url,
                'local_path': str(file_path),
                'error': None,
                'file_size': file_size
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'local_path': None,
                'error': str(e),
                'file_size': 0
            }
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'local_path': None,
                'error': str(e),
                'file_size': 0
            }
    
    def download_images_batch(self, images_data, subfolder=''):
        """
        Download multiple images (SINGLE THREADED - sequential)
        
        Args:
            images_data: List of dicts with 'url' and optional 'filename' keys
                        OR list of URLs
            subfolder: Subfolder for all images
            
        Returns:
            list: List of download results
        """
        results = []
        
        for i, img in enumerate(images_data, 1):
            # Handle both dict and string formats
            if isinstance(img, str):
                url = img
                filename = None
            else:
                url = img.get('url')
                filename = img.get('filename')
            
            if not url:
                continue
            
            logger.info(f"Downloading image {i}/{len(images_data)}: {url[:60]}...")
            result = self.download_image(url, subfolder, filename)
            results.append(result)
        
        return results
    
    def download_images_parallel(self, images_data, subfolder='', max_workers=None,
                                show_progress=True):
        """
        Download multiple images in parallel (CONCURRENT - faster!)
        
        Args:
            images_data: List of dicts with 'url' and optional 'filename' keys
                        OR list of URLs
            subfolder: Subfolder for all images
            max_workers: Number of concurrent threads (default: self.max_workers)
            show_progress: Show progress bar (requires tqdm)
            
        Returns:
            dict: {
                'results': list of download results,
                'success_count': number of successful downloads,
                'failed_count': number of failed downloads,
                'total_attempted': total number of images,
                'total_size_mb': total size downloaded
            }
        """
        if max_workers is None:
            max_workers = self.max_workers
        
        # Prepare image list
        images_to_download = []
        for img in images_data:
            if isinstance(img, str):
                images_to_download.append({'url': img, 'filename': None})
            else:
                images_to_download.append({
                    'url': img.get('url'),
                    'filename': img.get('filename')
                })
        
        # Remove None URLs
        images_to_download = [img for img in images_to_download if img['url']]
        
        results = []
        success_count = 0
        failed_count = 0
        total_size = 0
        
        logger.info(f"Starting parallel download of {len(images_to_download)} images "
                   f"with {max_workers} workers...")
        
        # Try to use progress bar if available
        try:
            from tqdm import tqdm
            iterator = tqdm(total=len(images_to_download), desc="Downloading images",
                          unit="img")
            use_progress = show_progress
        except ImportError:
            iterator = None
            use_progress = False
        
        # Download in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_img = {
                executor.submit(
                    self.download_image,
                    img['url'],
                    subfolder,
                    img['filename']
                ): img for img in images_to_download
            }
            
            # Process completed downloads
            for future in as_completed(future_to_img):
                result = future.result()
                results.append(result)
                
                if result['success']:
                    success_count += 1
                    total_size += result['file_size']
                else:
                    failed_count += 1
                
                if use_progress:
                    iterator.update(1)
                    iterator.set_postfix({
                        'success': success_count,
                        'failed': failed_count
                    })
        
        if use_progress and iterator:
            iterator.close()
        
        total_size_mb = round(total_size / (1024 * 1024), 2)
        
        logger.info(f"Parallel download completed: {success_count} success, "
                   f"{failed_count} failed ({total_size_mb} MB)")
        
        return {
            'results': results,
            'success_count': success_count,
            'failed_count': failed_count,
            'total_attempted': len(images_to_download),
            'total_size_mb': total_size_mb
        }
    
    def get_download_stats(self):
        """Get statistics about downloaded images"""
        total_size = 0
        total_files = 0
        
        for file in self.base_dir.rglob('*'):
            if file.is_file():
                total_files += 1
                total_size += file.stat().st_size
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'base_dir': str(self.base_dir)
        }


def extract_and_download_images(items, image_field='image', subfolder='items', 
                               downloader=None, max_images=None):
    """
    Helper function to extract image URLs from items and download them
    
    Args:
        items: List of item dicts containing image URLs
        image_field: Field name containing image URL (default: 'image')
        subfolder: Subfolder to save images
        downloader: ImageDownloader instance (creates new if None)
        max_images: Limit number of images to download
        
    Returns:
        dict: {
            'items': items with 'image_local' field added,
            'download_results': list of download results,
            'success_count': number of successful downloads,
            'failed_count': number of failed downloads
        }
    """
    if downloader is None:
        downloader = ImageDownloader()
    
    results = []
    success_count = 0
    failed_count = 0
    
    for i, item in enumerate(items):
        if max_images and i >= max_images:
            break
        
        image_url = item.get(image_field)
        if image_url:
            result = downloader.download_image(image_url, subfolder)
            results.append(result)
            
            # Add local path to item
            item['image_local'] = result['local_path']
            
            if result['success']:
                success_count += 1
            else:
                failed_count += 1
    
    return {
        'items': items,
        'download_results': results,
        'success_count': success_count,
        'failed_count': failed_count,
        'total_attempted': len(results)
    }

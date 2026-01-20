# Hướng dẫn: Crawl dữ liệu + Tải hình ảnh

## Tổng quan

Bây giờ bạn có thể:
1. **Crawl dữ liệu web** (tiêu đề, liên kết, mô tả)
2. **Tải hình ảnh tự động** (poster, thumbnail, ảnh chi tiết)
3. **Lưu cả dữ liệu và hình ảnh** vào folder

## 3 Cách sử dụng

### 1️⃣ Crawl PhimHay với hình ảnh

```python
from crawl_with_images import crawl_phimhay_with_images

# Crawl 2 trang, tải tối đa 10 hình
crawl_phimhay_with_images(pages=2, max_images=10, detail_crawl=True)
```

**Kết quả:**
- `data/phimhay_with_images.json` - Dữ liệu + đường dẫn hình ảnh
- `downloads/phimhay/list_images/` - Hình poster từ trang danh sách
- `downloads/phimhay/detail_images/` - Hình từ trang chi tiết

**JSON output:**
```json
[
  {
    "title": "Doraemon Movie",
    "url": "https://phimhay.co.in/...",
    "image": "https://...",
    "image_local": "downloads/phimhay/list_images/doraemon.jpg",
    "detail_image_local": "downloads/phimhay/detail_images/Doraemon Movie.jpg",
    "rating": "8.5",
    "year": "2024"
  }
]
```

---

### 2️⃣ Crawl AnimeHay với hình ảnh + episode

```python
from crawl_with_images import crawl_animehay_with_images

# Crawl anime, tải poster + thumbnail episode
crawl_animehay_with_images(category='anime-1', pages=2, max_images=5)
```

**Kết quả:**
- `data/animehay_with_images.json` - Anime + episodes + paths hình
- `downloads/animehay/anime_posters/` - Poster anime
- `downloads/animehay/episode_thumbnails/` - Thumbnail episode

**JSON output:**
```json
[
  {
    "title": "Demon Slayer",
    "url": "https://animehay.life/...",
    "image": "https://...",
    "image_local": "downloads/animehay/anime_posters/...",
    "year": "2024",
    "episodes": [
      {
        "episode_number": 1,
        "title": "Ep 1",
        "image": "https://...",
        "image_local": "downloads/animehay/episode_thumbnails/..."
      }
    ]
  }
]
```

---

### 3️⃣ Crawl website tùy chỉnh + hình ảnh

```python
from crawl_with_images import crawl_custom_website_with_images

# Dùng config 'phimhay' (hoặc website khác)
crawl_custom_website_with_images('phimhay', pages=2, image_field='image')
```

---

## 🚀 PHƯƠNG PHÁP BATCH: Tải nhiều hình cùng lúc (NHANH NHẤT!)

### 📌 Method 1: Tải song song (Parallel) - PHIMHAY

```python
from batch_download import batch_download_phimhay_parallel

# Tải 100 hình cùng 1 lúc vào 1 folder!
items, result = batch_download_phimhay_parallel(
    pages=2,          # Crawl 2 trang
    max_workers=8     # Tải 8 cái hình cùng lúc
)

print(f"Downloaded: {result['success_count']} images")
print(f"Total size: {result['total_size_mb']} MB")
```

**Output:**
```
[████████████████████] 50/50 images | success: 50, failed: 0

✓ Success: 50/50
✗ Failed: 0/50
📊 Total size: 125.5 MB
```

### 📌 Method 2: Tải song song - ANIMEHAY

```python
from batch_download import batch_download_animehay_parallel

# Tải poster anime + episode thumbnails cùng lúc!
animes, result = batch_download_animehay_parallel(
    category='anime-1',
    pages=2,
    max_workers=6     # 6 files cùng lúc
)

print(f"Downloaded: {result['total_size_mb']} MB")
```

### 📌 Method 3: Tải bất kỳ website nào

```python
from batch_download import batch_download_website

# Crawl + tải hình cho website config bất kỳ
items, result = batch_download_website(
    config_name='phimhay',
    pages=2,
    max_workers=4
)
```

### 📌 Method 4: TẢI SIÊU NHANH - Chỉ từ URLs (CHO TẤT CẢ)

```python
from batch_download import batch_download_from_urls

# Tải 1000 hình chỉ từ danh sách URLs!
urls = [
    'https://example.com/img1.jpg',
    'https://example.com/img2.jpg',
    'https://example.com/img3.jpg',
    # ... thêm tất cả URLs
]

result = batch_download_from_urls(
    urls,
    folder_name='my_images',
    max_workers=10  # 10 hình cùng lúc!
)

# Kết quả
print(result['success_count'])    # Tải được bao nhiêu
print(result['total_size_mb'])    # Tổng size
```

---



## 📁 Cấu trúc thư mục hình ảnh

```
downloads/
├── phimhay/
│   ├── list_images/     # Hình từ danh sách
│   │   ├── movie1.jpg
│   │   ├── movie2.jpg
│   │   └── ...
│   └── detail_images/   # Hình từ trang chi tiết
│       └── ...
├── animehay/
│   ├── anime_posters/   # Poster anime
│   │   └── ...
│   └── episode_thumbnails/  # Thumbnail episode
│       └── ...
└── [config_name]/
    └── items/
        └── ...
```

---

## 🔧 ImageDownloader - Chi tiết

### Khởi tạo downloader

```python
from utils.image_downloader import ImageDownloader

# Cơ bản
downloader = ImageDownloader()
# → Lưu vào: downloads/images/
# → max_workers: 4 (mặc định)

# Custom folder + workers
downloader = ImageDownloader(
    base_dir='my_images/phimhay',
    timeout=15,      # 15s timeout per image
    delay=1,         # 1s delay between single downloads
    max_workers=8    # 8 hình tải song song
)
```

### Tải 1 hình ảnh

```python
result = downloader.download_image(
    url='https://example.com/movie.jpg',
    subfolder='movies',
    filename='movie_2024.jpg'
)

print(result)
# {
#     'success': True,
#     'url': 'https://...',
#     'local_path': 'downloads/images/movies/movie_2024.jpg',
#     'error': None,
#     'file_size': 45000  # bytes
# }
```

### Tải nhiều hình SEQUENTIAL (Từng cái một)

```python
images_urls = [
    'https://example.com/img1.jpg',
    'https://example.com/img2.jpg',
    'https://example.com/img3.jpg'
]

results = downloader.download_images_batch(
    images_urls,
    subfolder='batch'
)

for result in results:
    print(f"{result['url']}: {result['success']}")
```

### ⚡ Tải nhiều hình PARALLEL (CÙNG LÚC - NHANH!)

```python
image_urls = [
    'https://example.com/img1.jpg',
    'https://example.com/img2.jpg',
    # ... 1000+ hình khác
]

# TẢI TẤT CẢ CÙNG LÚC!
result = downloader.download_images_parallel(
    image_urls,
    subfolder='fast_batch',
    max_workers=8,      # 8 hình cùng lúc
    show_progress=True  # Hiện progress bar
)

print(result)
# {
#     'success_count': 995,
#     'failed_count': 5,
#     'total_attempted': 1000,
#     'total_size_mb': 512.5
# }
```

### Helper: Extract + Download từ items

```python
from utils.image_downloader import extract_and_download_images

# Bạn đã crawl items này
items = [
    {'title': 'Movie 1', 'image': 'https://...', ...},
    {'title': 'Movie 2', 'image': 'https://...', ...},
]

# Extract hình + tải
result = extract_and_download_images(
    items=items,
    image_field='image',        # Trường chứa URL
    subfolder='my_movies',
    max_images=10              # Tải tối đa 10 cái
)

# Các items giờ có field mới
print(items[0]['image_local'])  # Path hình đã tải
print(f"Success: {result['success_count']}")
print(f"Failed: {result['failed_count']}")
```

---

## 📊 Kiểm tra thống kê

```python
stats = downloader.get_download_stats()
print(stats)

# Output:
# {
#     'total_files': 42,
#     'total_size_mb': 125.5,
#     'base_dir': 'downloads/images'
# }
```

---

## 🚀 Ví dụ thực tế

### Crawl + save + kiểm tra

```python
from crawl_with_images import crawl_phimhay_with_images
from utils.image_downloader import ImageDownloader

# 1. Crawl dữ liệu + tải hình
crawl_phimhay_with_images(
    pages=3,           # 3 trang
    max_images=50,     # Tối đa 50 hình
    detail_crawl=True  # Cũng crawl trang chi tiết
)

# 2. Kiểm tra kết quả
import json
with open('data/phimhay_with_images.json') as f:
    data = json.load(f)
    
print(f"Total items: {len(data)}")
print(f"Total images: {sum(1 for item in data if item.get('image_local'))}")

# 3. Kiểm tra size
downloader = ImageDownloader('downloads/phimhay')
stats = downloader.get_download_stats()
print(f"Downloaded: {stats['total_files']} images, {stats['total_size_mb']} MB")
```

---

## ⚙️ Cấu hình nâng cao

### Custom headers & cookies

```python
from crawlers.flexible_crawler import FlexibleWebCrawler
from config.crawler_config import ConfigManager
from utils.image_downloader import ImageDownloader

# Load config
config_mgr = ConfigManager()
config = config_mgr.load_config('phimhay')

# Modify headers for images
config.headers['Referer'] = 'https://phimhay.co.in/'

crawler = FlexibleWebCrawler(config)
items = crawler.crawl_items()

# Download with same headers
downloader = ImageDownloader('downloads/phimhay')
results = downloader.download_images_batch(
    [item['image'] for item in items],
    subfolder='images'
)
```

### Timeout cho trang chậm

```python
# Tăng timeout cho website chậm
downloader = ImageDownloader(
    base_dir='downloads/slow_site',
    timeout=30  # 30 giây
)
```

### Delay để respects website

```python
# Delay 2 giây giữa mỗi download (đẹp trai!)
downloader = ImageDownloader(
    base_dir='downloads/images',
    delay=2  # Thắng nhân loại
)
```

---

## ⚠️ Xử lý lỗi

```python
result = downloader.download_image(url)

if not result['success']:
    print(f"Error: {result['error']}")
    # Các lỗi có thể:
    # - "Invalid URL"
    # - "Connection timeout"
    # - "404 Not Found"
    # - "403 Forbidden"
    # - etc...
else:
    print(f"Saved to: {result['local_path']}")
    print(f"Size: {result['file_size']} bytes")
```

---

## 🎯 Tổng kết

| Tác vụ | Code | Tốc độ |
|--------|------|--------|
| **Crawl + download phimhay** | `crawl_phimhay_with_images()` | Normal |
| **Crawl + download anime** | `crawl_animehay_with_images()` | Normal |
| **Batch: Parallel phimhay** | `batch_download_phimhay_parallel()` | ⚡ NHANH |
| **Batch: Parallel animehay** | `batch_download_animehay_parallel()` | ⚡ NHANH |
| **Batch: Parallel website** | `batch_download_website()` | ⚡ NHANH |
| **Batch: Từ URLs** | `batch_download_from_urls()` | ⚡ SIÊU NHANH |
| **Download 1 hình** | `downloader.download_image()` | Normal |
| **Download nhiều (sequential)** | `downloader.download_images_batch()` | Normal |
| **Download nhiều (parallel)** | `downloader.download_images_parallel()` | ⚡ NHANH |

---

## 📝 Notes

1. **Hình đã tải sẽ bị bỏ qua** - Không tải lại nếu file đã tồn tại
2. **User-Agent tự động** - Tránh được một số website chặn
3. **Delay giữa downloads** - Respects website, không spam request
4. **Timeout mặc định 10s** - Điều chỉnh nếu cần
5. **Lỗi không dừng process** - Cứ tiếp tục tải các hình còn lại

---

## 🔗 File liên quan

- `utils/image_downloader.py` - Core ImageDownloader class
- `crawl_with_images.py` - Các ví dụ sẵn dùng
- `data/` - Output JSON files
- `downloads/` - Thư mục lưu hình ảnh

import os
from dotenv import load_dotenv

load_dotenv()

# Database Settings
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'movie_crawl')
DATABASE_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

# Crawler Settings
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))
RETRY_TIMES = int(os.getenv('RETRY_TIMES', 3))
DELAY_BETWEEN_REQUESTS = int(os.getenv('DELAY_BETWEEN_REQUESTS', 2))

# Logging Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/crawler.log')

# Selenium Settings
HEADLESS_BROWSER = os.getenv('HEADLESS_BROWSER', 'True').lower() == 'true'
BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chrome')

# Headers for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Target URLs
IMDB_URL = os.getenv('IMDB_URL', 'https://www.imdb.com')
ROTTENTOMATOES_URL = os.getenv('ROTTENTOMATOES_URL', 'https://www.rottentomatoes.com')

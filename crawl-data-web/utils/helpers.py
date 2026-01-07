import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.settings import REQUEST_TIMEOUT, RETRY_TIMES, HEADERS, DELAY_BETWEEN_REQUESTS
from utils.logger import get_logger

logger = get_logger(__name__)

def create_session():
    """Create a requests session with retry strategy"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=RETRY_TIMES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    
    return session

def fetch_page(url, session=None):
    """Fetch a page with error handling"""
    if session is None:
        session = create_session()
    
    try:
        time.sleep(DELAY_BETWEEN_REQUESTS)
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None

def safe_extract(soup, selector, attribute=None, default=''):
    """Safely extract data from BeautifulSoup element"""
    try:
        element = soup.select_one(selector)
        if element is None:
            return default
        
        if attribute:
            return element.get(attribute, default)
        else:
            return element.get_text(strip=True) if element else default
    except Exception as e:
        logger.error(f"Error extracting from selector {selector}: {str(e)}")
        return default

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ''
    return ' '.join(text.split())

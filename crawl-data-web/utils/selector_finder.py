"""
Guide and utilities for finding correct CSS selectors
"""

from bs4 import BeautifulSoup
from crawlers.base_crawler import BaseCrawler
from utils.logger import get_logger

logger = get_logger(__name__)

class SelectorFinder:
    """Help find correct CSS selectors for websites"""
    
    def __init__(self):
        self.crawler = BaseCrawler()
    
    def inspect_elements(self, url, limit=10):
        """
        Inspect elements on a page
        
        Args:
            url: URL to inspect
            limit: Maximum number of elements to show
        
        Returns:
            Dict with element information
        """
        logger.info(f"Inspecting page: {url}")
        soup = self.crawler.get_soup(url)
        
        if soup is None:
            return None
        
        result = {
            'page_title': soup.title.string if soup.title else 'N/A',
            'divs': self._get_element_info(soup, 'div', limit),
            'links': self._get_element_info(soup, 'a', limit),
            'images': self._get_element_info(soup, 'img', limit),
            'spans': self._get_element_info(soup, 'span', limit),
            'h1': self._get_element_info(soup, 'h1', limit),
            'h2': self._get_element_info(soup, 'h2', limit),
            'h3': self._get_element_info(soup, 'h3', limit),
        }
        
        return result
    
    def _get_element_info(self, soup, tag, limit=10):
        """Get information about elements"""
        elements = soup.find_all(tag, limit=limit)
        
        element_info = []
        for elem in elements:
            info = {
                'tag': tag,
                'text': elem.get_text(strip=True)[:100],  # First 100 chars
                'classes': elem.get('class', []),
                'id': elem.get('id', ''),
                'href': elem.get('href', ''),  # For links
                'src': elem.get('src', ''),     # For images
                'alt': elem.get('alt', ''),     # For images
            }
            
            # Build possible CSS selector
            css_selector = self._build_selector(elem)
            info['css_selector'] = css_selector
            
            element_info.append(info)
        
        return element_info
    
    def _build_selector(self, elem):
        """Build CSS selector for an element"""
        selectors = []
        
        # Try ID
        if elem.get('id'):
            return f"#{elem.get('id')}"
        
        # Try class
        classes = elem.get('class', [])
        if classes:
            class_selector = f"{elem.name}.{'.'.join(classes)}"
            selectors.append(class_selector)
        
        # Tag only
        selectors.append(elem.name)
        
        return selectors[0] if selectors else 'unknown'
    
    def extract_data_by_selector(self, url, selector):
        """
        Extract data from a page using a selector
        
        Args:
            url: URL to extract from
            selector: CSS selector
        
        Returns:
            List of extracted texts
        """
        soup = self.crawler.get_soup(url)
        
        if soup is None:
            return []
        
        try:
            elements = soup.select(selector)
            data = [elem.get_text(strip=True) for elem in elements]
            return data
        except Exception as e:
            logger.error(f"Error extracting with selector '{selector}': {str(e)}")
            return []
    
    def test_selectors(self, url, selector_dict):
        """
        Test multiple selectors on a page
        
        Args:
            url: URL to test
            selector_dict: Dict of selector_name -> css_selector
        
        Returns:
            Dict with test results
        """
        soup = self.crawler.get_soup(url)
        
        if soup is None:
            return {}
        
        results = {}
        
        for name, selector in selector_dict.items():
            try:
                elements = soup.select(selector)
                results[name] = {
                    'found': len(elements),
                    'sample': elements[0].get_text(strip=True)[:100] if elements else 'No match',
                    'valid': len(elements) > 0
                }
            except Exception as e:
                results[name] = {
                    'found': 0,
                    'error': str(e),
                    'valid': False
                }
        
        return results


def print_selector_guide():
    """Print guide on how to find CSS selectors"""
    
    guide = """
╔════════════════════════════════════════════════════════════════════════════╗
║                  HOW TO FIND CSS SELECTORS MANUALLY                        ║
╚════════════════════════════════════════════════════════════════════════════╝

1. USING BROWSER INSPECT TOOL:
   - Right-click on element in browser
   - Select "Inspect" or "Inspect Element"
   - Look at the HTML code to find patterns
   
2. COMMON CSS SELECTOR PATTERNS:
   
   By ID:
   - #my-id
   - div#my-id
   
   By Class:
   - .my-class
   - div.my-class
   - .class1.class2  (element with both classes)
   
   By Tag:
   - div
   - a
   - img
   
   By Attribute:
   - [data-id]
   - [href*="example"]  (href contains "example")
   - [class*="movie"]   (class contains "movie")
   
   Combinations:
   - div.movie-item a.title     (a with class "title" inside div.movie-item)
   - .container > .item         (direct child)
   - .container .item           (any descendant)

3. EXAMPLE PATTERNS:
   
   Movie container:    div.movie-item, li.film, .card
   Movie title:        h2.title, a.name, .film-name
   Movie URL:          a, a.link, a[href*="/movie/"]
   Movie image:        img, img.poster, img.cover
   Movie rating:       span.rating, .score, [data-rating]
   Movie description:  p.description, .synopsis, div.plot
   
4. TESTING YOUR SELECTORS:
   
   Use the SelectorFinder.test_selectors() method to verify selectors work

5. TIPS:
   
   - Be as specific as possible to avoid false matches
   - Use browser DevTools to test selectors in console:
     document.querySelectorAll('YOUR_SELECTOR')
   - If selector returns too many results, add parent context:
     .container .item instead of just .item
   - For images, check both 'src' and 'data-src' attributes

╔════════════════════════════════════════════════════════════════════════════╗
║                          EXAMPLE CONFIGURATION                            ║
╚════════════════════════════════════════════════════════════════════════════╝

{
  "name": "MyWebsite",
  "base_url": "https://example.com",
  "list_url": "https://example.com/movies",
  "selectors": {
    "item_container": "div.movie-item",
    "item_title": "h2.title",
    "item_url": "a.link",
    "item_image": "img.poster",
    "item_rating": "span.rating"
  },
  "detail_selectors": {
    "title": "h1.page-title",
    "description": "div.synopsis",
    "rating": "span.imdb-score",
    "genres": "span.genre"
  }
}
"""
    
    print(guide)


if __name__ == '__main__':
    print_selector_guide()

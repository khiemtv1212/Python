# Web Crawler for Movie Data

A comprehensive Python project for crawling movie information from various websites.

## Features

✨ **Multi-source Crawling**
- IMDB crawler with specific selectors
- General website crawler with custom selectors
- Support for movies, ratings, reviews, and cast information

📦 **Database Management**
- SQLAlchemy ORM for data storage
- Models for Movie, Rating, Review, and CastMember
- Automatic session management

🛠️ **Utilities**
- Robust error handling and logging
- Session management with retry strategy
- Safe data extraction helpers
- Request rate limiting

## Project Structure

```
crawl-data-web/
├── config/
│   └── settings.py          # Configuration settings
├── crawlers/
│   ├── base_crawler.py      # Base crawler class
│   ├── imdb_crawler.py      # IMDB specific crawler
│   └── general_crawler.py   # General website crawler
├── models/
│   └── movie.py             # Database models
├── utils/
│   ├── logger.py            # Logging configuration
│   └── helpers.py           # Helper functions
├── data/                    # Data output directory
├── database.py              # Database initialization
├── main.py                  # Main entry point
├── examples.py              # Usage examples
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure `.env` file with your database credentials:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=movie_crawl
   ```

## Usage

### Basic Usage (main.py)

```python
from main import crawl_imdb_top250, crawl_custom_website

# Crawl IMDB Top 250
crawl_imdb_top250()

# Or crawl a custom website
config = {
    'movie_selector': 'div.movie-item',
    'title_selector': 'h2.title',
}
crawl_custom_website('https://example.com', config)
```

### Finding Correct Selectors

To find CSS selectors for your target website:

1. Open website in browser
2. Right-click on element → Inspect
3. Find the CSS selector in HTML
4. Update your configuration

Example: If movie titles are in `<h2 class="movie-title">`, use selector `h2.movie-title`

### Using the General Crawler

```python
from crawlers.general_crawler import GeneralMovieCrawler

crawler = GeneralMovieCrawler()

# Define selectors based on target website
selectors = {
    'title': 'h1.title',
    'year': 'span.year',
    'rating': 'div.rating',
    'description': 'p.plot'
}

movie_data = crawler.crawl_movie_details('https://example.com/movie/1', selectors)
```

### Crawling Reviews

```python
reviews = crawler.crawl_reviews(
    url='https://example.com/reviews',
    review_selector='div.review',
    reviewer_selector='span.name',
    rating_selector='span.rating',
    content_selector='p.text'
)
```

## Database Models

### Movie
- `id`: Primary key
- `title`: Movie title
- `year`: Release year
- `director`: Director name
- `duration`: Duration in minutes
- `description`: Plot description
- `genres`: Comma-separated genres
- `imdb_url`: Source URL
- `poster_url`: Poster image URL

### Rating
- `id`: Primary key
- `movie_id`: Foreign key to Movie
- `source`: Rating source (imdb, rottentomatoes, etc.)
- `score`: Numerical rating
- `vote_count`: Number of votes

### Review
- `id`: Primary key
- `movie_id`: Foreign key to Movie
- `reviewer_name`: Name of reviewer
- `rating`: Reviewer's rating
- `content`: Review text

### CastMember
- `id`: Primary key
- `movie_id`: Foreign key to Movie
- `actor_name`: Actor name
- `character_name`: Character name

## Configuration

Edit `.env` file to configure:

- **Database**: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
- **Crawler**: REQUEST_TIMEOUT, RETRY_TIMES, DELAY_BETWEEN_REQUESTS
- **Logging**: LOG_LEVEL, LOG_FILE
- **Browser**: HEADLESS_BROWSER, BROWSER_TYPE

## Logging

Logs are saved to `logs/crawler.log` and printed to console. Log level can be configured in `.env`.

## Best Practices

1. **Always use delays** between requests (default: 2 seconds)
2. **Check website's robots.txt** and terms of service
3. **Use custom User-Agent** headers
4. **Handle errors gracefully**
5. **Store data responsibly**
6. **Test with small limits** before large crawls

## Troubleshooting

**Connection errors**: Check internet connection and target website availability

**Database errors**: Verify database credentials in `.env` and ensure MySQL is running

**Selector errors**: Use browser inspect tool to find correct CSS selectors

**Timeout errors**: Increase REQUEST_TIMEOUT in `.env`

## License

MIT

## Notes

- This crawler respects website resources with delays between requests
- Always check website's terms of service before crawling
- For websites with robots.txt, ensure your crawler follows it
- Consider using this crawler for educational and research purposes

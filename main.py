from startup_scraper import scraper
from link_crawler import link_crawler

START_URL = 'https://www.startupofyear.com/alumni'

if __name__ == '__main__': 
    link_crawler(START_URL, link_regex=None, scraper_callback=scraper)
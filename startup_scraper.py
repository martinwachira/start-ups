import os
from lxml.html import fromstring
import os
import pandas as pd
from throttle import Throttle
from utils import is_location_in_north_america

SLEEP_TIME = 2
CURRENT_DIR = os.getcwd()
throttle = Throttle(3)

# name
STARTUP_NAME_XPATH = './/div[contains(@class, "s-item-title")]//div[contains(@class, "s-component-content")]'

# link
STARTUP_LINK_XPATH = './/div[contains(@class, "s-item-title")]//a/@href'

# location
STARTUP_LOCATION_XPATH = './/div[contains(@class, "s-item-subtitle")]//div[contains(@class, "s-component-content")]'


def scraper(url, html):
    STARTUPS = []
    
    tree = fromstring(html)
    # List of elements containing startup items
    startup_items = tree.xpath('//div[contains(@class, "s-repeatable")]//div[contains(@class, "s-repeatable-item")]')
    
    for item in startup_items:
        name = item.xpath(STARTUP_NAME_XPATH)
        if not name:
            continue
        name = name[0].text_content()
        
        try:
            name, location = name.split('|')
            name = name.strip()
            location = location.strip()
        except (IndexError, ValueError):
            location = None
            
        link = item.xpath(STARTUP_LINK_XPATH) or None
        if link:
            link = link[0]
        
        if not location:
            location = item.xpath(STARTUP_LOCATION_XPATH)
            if location:
                location = location[0].text_content().strip()
                
        location_in_north_america = is_location_in_north_america(location)
        if not location_in_north_america:
            print(f'({location or ""}) : Location Not in North America. Skipping....')
            continue
            
                
        print(f'Saving {name}')     
        
        STARTUPS.append((name, location, link))
        
    print(f'Total: {len(STARTUPS)}')
        
    df  = pd.DataFrame(STARTUPS, columns=['Name', 'Location', 'Link'], index=None)
    df.to_csv('data.csv')
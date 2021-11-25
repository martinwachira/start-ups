import re
from urllib import robotparser
import requests


USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'

def download(url, num_retries=3, user_agent=USER_AGENT, proxies=None):
    print('Downloading:', url)
    headers = {'User-Agent': user_agent}
    try:
        resp = requests.get(url, headers=headers, proxies=proxies)
        html = resp.text
        if resp.status_code >= 400:
            print('Download error:', resp.text)
            html = None
            if num_retries and 500 <= resp.status_code < 600:
                # recursively retry 5xx HTTP errors
                return download(url, num_retries - 1)
    except requests.exceptions.RequestException as e:
        print('Download error:', e)
        html = None
    return html


def get_robots_parser(robots_url):
    " Return the robots parser object using the robots_url "
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp

def get_links(html):
    webpage_regex = re.compile("""<a[^>]+href=["'](.*?)["']""", re.IGNORECASE)
    return webpage_regex.findall(html)

def remove_html_tags(text):
    html_tags = re.compile('<.*?>')
    return re.sub(html_tags, '', text)

def is_location_in_north_america(location_value):
    if not location_value:
        return None
    city, state = None, None
    locations = []
    if ';' in location_value:
        locations = location_value.split(';')
    else:
        locations = location_value.split('&')
    try:
        for location in locations:
            city, state = get_city_and_state(location)
            if state in STATES_IN_AMERICA or city.strip() in STATES_IN_AMERICA:
                cleaned_location = clean_location_value(locations)
                return cleaned_location
    except ValueError:
        print(f'Error checking location: {location_value}')
        pass

def process_state(state):
    """ 
    Cleans poorly formatted state strings
    """
    state = state or ''
    state = state.strip()
    if re.search(r'\d+', state):
        return state[:2]
    return state

def get_city_and_state(location):
    location_dict = dict(enumerate(location.split(',')))
    city = location_dict.get(0) or ''
    state = process_state(location_dict.get(1)) or ''
    return city, state
    
def clean_location_value(locations):
    location_value_cleaned = ''
    for location in locations:
        city, state = get_city_and_state(location)
        location_value_cleaned += f'{city}, {state};'
    return location_value_cleaned[:-1]
    

STATES_IN_AMERICA = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    'California',
    'Colorado',
    'Connecticut',
    'Delaware',
    'Florida',
    'Georgia',
    'Hawaii',
    'Idaho',
    'Illinois',
    'Indiana',
    'Iowa',
    'Kansas',
    'Kentucky',
    'Louisiana',
    'Maine',
    'Maryland',
    'Massachusetts',
    'Michigan',
    'Minnesota',
    'Mississippi',
    'Missouri',
    'Montana',
    'Nebraska',
    'Nevada',
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
    "Washington DC",
    "Canada",
    "Ontario",
    "Mexico",
    "Cuba",
    "AK",
    "AL",
    "AR",
    "AZ",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "IA",
    "ID",
    "IL",
    "IN",
    "KS",
    "KY",
    "LA",
    "MA",
    "MD",
    "ME",
    "MI",
    "MN",
    "MO",
    "MS",
    "MT",
    "NC",
    "ND",
    "NE",
    "NH",
    "NJ",
    "NM",
    "NV",
    "NY",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VA",
    "VT",
    "WA",
    "WI",
    "WV",
    "WY",
    "DC"
]
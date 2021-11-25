import re
import socket
from urllib.parse import urljoin, urlparse
from utils import download, get_links, get_robots_parser, USER_AGENT
from throttle import Throttle

socket.setdefaulttimeout(120)


def link_crawler(start_url, link_regex=None, robots_url=None, user_agent=USER_AGENT,
                 max_depth=-1, delay=3, proxies=None, num_retries=2, cache=None,
                 scraper_callback=None):

    #: Initialze a crawl queue with a seed url to start the crawl from
    crawl_queue = [start_url]

    #: keep track of seen urls
    seen = {}

    robots = {}

    throttle = Throttle(delay)

    #: start the crawl
    while crawl_queue:
        url = crawl_queue.pop()

        #: robots.txt
        robots_file_present = False
        if 'http' not in url:
            continue

        #: Get the domain
        domain = '{}://{}'.format(urlparse(url).scheme, urlparse(url).netloc)

        #: Get the robot parser for this domain from the robots dictionary
        robot_parser = robots.get(domain)

        #: set a default robots url and a parser for it if there isn't one
        if not robot_parser and domain not in robots:
            robots_url = '{}/robots.txt'.format(domain)
            robot_parser = get_robots_parser(robots_url)
            if not robot_parser:
                #: continue to crawl even if there are problems finding robots.txt
                #: file
                robots_file_present = True
            # associate each domain with a corresponding parser, whether 
            # present or not
            robots[domain] = robot_parser

        elif domain in robots:
            robots_file_present = True

        #: crawl only when url passes robots.txt restrictions
        if robots_file_present or robot_parser.can_fetch(user_agent, url):
            depth = seen.get(url, 0)
            if depth == max_depth:
                #: Skip link if you have crawled it more than max depth
                print('Skipping %s due to depth' % url)
                continue
            throttle.wait(url)
            #: Download html content
            html= download(url, num_retries=num_retries)
            if not html:
                continue
            
            #: Scrape data off of the downloaded html
            if scraper_callback:
                scraper_callback(url, html)

            #: Get all links from page and filter only those matching given pattern
            if link_regex:
                for link in get_links(html):
                    if re.search(link_regex, link):
                        if 'http' not in link:
                            # check if link is well formed and correct
                            if link.startswith('//'):
                                link = '{}:{}'.format(urlparse(url).scheme, link)
                            elif link.startswith('://'):
                                link = '{}{}'.format(urlparse(url).scheme, link)
                            else:
                                link = urljoin(domain, link)

                        if link not in seen:
                            seen[link] = depth + 1
                            crawl_queue.append(link)
        else:
            print('Blocked by robots.txt:', url)
## Python 3.5 required for requests library

## End variable URLS with trailing slash

import requests
from bs4 import BeautifulSoup
import settings

#TODO: Change user agent to RosieBot
#TODO: AJAX
#TODO: Headless browsing

# Configure for testing in settings
base_urls = settings.base_urls
limit = settings.limit

class Crawler():
    '''
    Crawlers keep one page_list of all of the URL tails and GUIDs they encounter, which the scraper will go through to save pages.
    For API searches, a limit parameter is necessary for testing.

    URL tails:
    - Homepage content
    - Homepage links

    API searches:
    - Nodes
    - Users
    - Institutions

    The Crawler.crawl() function calls all of these piece crawls.

    '''
    def __init__(self):
        global base_urls
        self.page_list = []
        self.node_list = []
        self.http_base = base_urls[0]
        self.api_base = base_urls[1]
        self.headers = {
            'User-Agent': 'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
            # 'User-Agent' : 'ROSIEBot/1.0 (+http://github.com/zamattiac/ROSIEBot)'
        }

    # Accesses complete list of nodes from API and appends list of GUIDs, appends a node-only list for file and wiki seraching
    def crawl_nodes(self, limit=0):
        print("Crawling Nodes API")
        with requests.Session() as s:
            cur_url = self.api_base + 'nodes/'
            ctr = 1

            while True:
                current_page = s.get(cur_url)
                parsed_json = current_page.json()
                for x in range(0, len(parsed_json['data'])):
                    if parsed_json['data'][x]['attributes']['public']:
                        self.node_list.append(str(parsed_json['data'][x]['id']))
                        self.page_list.append(str(parsed_json['data'][x]['id']))
                        self.page_list.append(str(parsed_json['data'][x]['id']) + '/registrations')
                        self.page_list.append(str(parsed_json['data'][x]['id']) + '/forks')
                        self.page_list.append(str(parsed_json['data'][x]['id']) + '/analytics')

                cur_url = parsed_json['links']['next']

                if parsed_json['links']['next'] == parsed_json['links']['last']:
                    break
                if limit == ctr:
                    break
                ctr += 1

    # Accesses complete list of users from API and appends list of GUIDs
    def crawl_users(self, limit=0):
        print("Crawling Users API")
        with requests.Session() as s:
            cur_url = self.api_base + 'users/'
            ctr = 1

            while True:
                current_page = s.get(cur_url)
                parsed_json = current_page.json()
                for x in range(0, len(parsed_json['data'])):
                    self.page_list.append(str(parsed_json['data'][x]['id']))

                cur_url = parsed_json['links']['next']

                if parsed_json['links']['next'] == parsed_json['links']['last']:
                    break
                if limit == ctr:
                    break
                ctr += 1

    # Accesses complete list of institutions from API and appends list of URL tails
    def crawl_institutions(self, limit=0):
        print("Crawling Institutions API")
        with requests.Session() as s:
            cur_url = self.api_base + 'institutions/'
            ctr = 1

            while True:
                current_page = s.get(cur_url)
                parsed_json = current_page.json()
                for x in range(0, len(parsed_json['data'])):
                    self.page_list.append('institutions/' + str(parsed_json['data'][x]['id']))
                cur_url = parsed_json['links']['next']

                if parsed_json['links']['next'] == parsed_json['links']['last']:
                    break
                if limit == ctr:
                    break
                ctr += 1

    # Accesses general site pages and appends the URL tails
    def crawl_root(self):
        print('Crawling Homepage')
        with requests.Session() as s:
            cur_link = self.http_base
            g = s.get(cur_link)

            c = g.content
            soup = BeautifulSoup(c, "html.parser")
            links = soup.find_all("a", href=True)
            for a in links:
                link = a['href']
                url_tail = link.replace((self.http_base), '').lstrip('//')
                if url_tail not in self.page_list and not 'www' in url_tail and not url_tail.startswith('http'):
                    self.page_list.append(url_tail)

    # Access node pages and snoop around for children
    # Works, but way too slow for actual use
    def crawl_wiki(self, nodes):
        print("Crawling Nodes for Wiki")
        for node in nodes:
            node_url = self.http_base + node + '/wiki/'
            with requests.Session() as s:
                r = s.get(node_url)
                new_r = s.get(r.url, headers=self.headers)
                soup = BeautifulSoup(new_r.text, 'html.parser')
                for link in soup.find_all(class_ = 'fg-file-links'):
                    self.page_list.append(link)

    def crawl(self, limit=0):
        self.crawl_root()
        self.crawl_nodes(limit)
        self.crawl_users(limit)
        self.crawl_institutions(limit)
        # self.crawl_wiki(self.node_list)
        return self.page_list
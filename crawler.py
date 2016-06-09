## Python 3.5 required for requests library

## End variable URLS with trailing slash

import asyncio
import aiohttp
import json
import datetime
import requests


# For development, API access is localhost:8000 by default and HTTP access is localhost:5000
base_urls = ['https://osf.io/', 'https://api.osf.io/v2/']
#base_urls = ['http://localhost:5000/', 'http://localhost:8000/v2/']


#TODO: Command line interface
#TODO: Change user agent to RosieBot
#TODO: AJAX
#TODO: Directories
#TODO: Static content

class Crawler():
    '''
    Crawlers keep one node_list of all of the URL tails and GUIDs they encounter, which the scraper will go through to save pages.
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
        self.url_list = []
        self.headers = {
            'User-Agent' : 'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
            # 'User-Agent' : 'ROSIEBot/1.0 (+http://github.com/zamattiac/ROSIEBot)'
        }
        self.node_url_list = []
        self.user_url_list = []
        self.institution_url_list = []
        self.http_base = base_urls[0]
        self.api_base = base_urls[1]

    def call_node_api_pages(self, pages=0):
        tasks = []
        for i in range(1, pages + 1):
            tasks.append(asyncio.ensure_future(self.call_and_parse_api_page(self.api_base + 'nodes/?page=' + str(i))))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    async def call_and_parse_api_page(self, url):
        async with aiohttp.ClientSession() as s:
            print('API request sent')
            response = await s.get(url)
            body = await response.read()
            response.close()
            json_body = json.loads(body.decode('utf-8'))
            data = json_body['data']
            for element in data:
                if element['attributes']['public'] is True:
                    self.node_url_list.append('http://localhost/' + element['id'] + '/')

    def crawl_all_nodes(self):
        tasks = []
        print(self.node_url_list)
        for url in self.node_url_list:
            tasks.append(asyncio.ensure_future(self.crawl_node_page(url)))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    async def crawl_node_page(self, url):
        print(url)
        async with aiohttp.ClientSession() as s:
            response = await s.get(url, headers=self.headers)
            body = await response.read()
            response.close()
            if response.status is 200:
                string = url.split('//')
                filename = string[1].split('/')
                file = open(filename[1] + '.html', 'wb+')
                file.write(body)
                file.close()
                print("finished crawling " + url)

a = datetime.datetime.now()
c = Crawler()
c.call_node_api_pages(pages=1)
c.crawl_all_nodes()
b = datetime.datetime.now()
print(b - a)
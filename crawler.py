import asyncio
import aiohttp
import json
import datetime
import os, sys
import requests
from bs4 import BeautifulSoup
import settings

#TODO: Change user agent to RosieBot
#TODO: AJAX
#TODO: Headless browsing

# Configure for testing in settings
base_urls = settings.base_urls
limit = settings.limit
verbose = settings.verbose


class Crawler:
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
            tasks.append(asyncio.ensure_future(self.call_and_parse_api_page(
                self.api_base + 'nodes/?page=' + str(i),
                node=True
            )))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    def call_user_api_pages(self, pages=0):
        tasks = []
        for i in range(1, pages + 1):
            tasks.append(asyncio.ensure_future(self.call_and_parse_api_page(
                self.api_base + 'users/?page=' + str(i),
                user=True
            )))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    def call_institution_api_pages(self, pages=0):
        tasks = []
        for i in range(1, pages + 1):
            tasks.append(asyncio.ensure_future(self.call_and_parse_api_page(
                self.api_base + 'institutions/?page=' + str(i),
                institution=True
            )))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    async def call_and_parse_api_page(self, url, node=False, user=False, institution=False):

        if node is True:
            async with aiohttp.ClientSession() as s:
                print('Nodes API request sent')
                response = await s.get(url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for element in data:
                    if element['attributes']['public'] is True:
                        self.node_url_list.append(self.http_base + element['id'] + '/')
                        self.node_url_list.append(self.http_base + element['id'] + '/files/')
                        self.node_url_list.append(self.http_base + element['id'] + '/registrations/')
                        self.node_url_list.append(self.http_base + element['id'] + '/forks/')
                        self.node_url_list.append(self.http_base + element['id'] + '/analytics/')
                        self.node_url_list.append(self.http_base + element['id'] + '/wiki/home/')

        if user is True:
            async with aiohttp.ClientSession() as s:
                print('Users API request sent')
                response = await s.get(url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for element in data:
                    self.user_url_list.append(self.http_base + element['id'] + '/')

        if institution is True:
            async with aiohttp.ClientSession() as s:
                print('Users API request sent')
                response = await s.get(url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for element in data:
                    self.institution_url_list.append(self.http_base + 'institutions' + element['id'] + '/')

    def scrape_all_nodes(self):
        sem = asyncio.BoundedSemaphore(value=4)
        tasks = []
        print(self.node_url_list)
        for url in self.node_url_list:
            tasks.append(asyncio.ensure_future(self.scrape_url(url, sem)))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    def scrape_all_users(self):
        sem = asyncio.BoundedSemaphore(value=4)
        tasks = []
        print(self.user_url_list)
        for url in self.user_url_list:
            tasks.append(asyncio.ensure_future(self.scrape_url(url, sem)))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    def scrape_all_institutions(self):
        sem = asyncio.BoundedSemaphore(value=4)
        tasks = []
        print(self.institution_url_list)
        for url in self.institution_url_list:
            tasks.append(asyncio.ensure_future(self.scrape_url(url, sem)))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    async def scrape_url(self, url, sem):
        async with sem:
            async with aiohttp.ClientSession() as s:
                print(url)
                response = await s.get(url, headers=self.headers)
                body = await response.read()
                response.close()
                if response.status is 200:
                    save_html(body, url)
                    # string = url.split('//')
                    # filename = string[1].split('/')
                    # file = open('archive/' + filename[1] + '.html', 'wb+')
                    # file.write(body)
                    # file.close()
                    print("finished crawling " + url)


def save_html(html, page):
    print(page)
    page = page.split('//', 1)[1]
    self.make_dirs(page)
    f = open(page + 'index.html', 'wb')
    f.write(html)
    f.close()
    os.chdir(sys.path[0])

def make_dirs(sfilename):
    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        os.makedirs(folder)


a = datetime.datetime.now()
c = Crawler()
c.call_node_api_pages(pages=1)
c.call_user_api_pages(pages=1)
# c.call_user_api_pages(pages=10)
#c.call_institution_api_pages(pages=1)
c.scrape_all_nodes()
c.scrape_all_users()
b = datetime.datetime.now()
print(b - a)
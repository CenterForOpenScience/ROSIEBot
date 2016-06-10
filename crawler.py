import asyncio
import aiohttp
import json
import datetime
import os, sys
import requests
from bs4 import BeautifulSoup
import settings

# Configure for testing in settings.py
base_urls = settings.base_urls
limit = settings.limit
verbose = settings.verbose


class Crawler:
    """
    Crawler asynchronously accesses the APIs for nodes, users, and institutions.
    The crawler generates separate lists of the GUIDs of each,
     asynchronously accesses the page content,
     and calls static functions below to save the HTML and preserve directory format.

    API aspects:
    - Nodes
    - Users
    - Institutions

    The Crawler.crawl() function calls all of these piece crawls.

    """
    def __init__(self):
        global base_urls
        self.url_list = []
        self.headers = {
            'User-Agent' : 'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
        }
        self.http_base = base_urls[0]
        self.api_base = base_urls[1]

        self.node_url_list = []
        self.user_url_list = []
        # Shoehorn index in:
        self.institution_url_list = [self.http_base]

    def call_api_pages(self, api_aspect, pages=0):
        tasks = []
        for i in range(1, pages + 1):
            tasks.append(asyncio.ensure_future(self.call_and_parse_api_page(
                self.api_base + api_aspect + '/?page=' + str(i),
                node=True
            )))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    # def call_user_api_pages(self, pages=0):
    #     tasks = []
    #     for i in range(1, pages + 1):
    #         tasks.append(asyncio.ensure_future(self.call_and_parse_api_page(
    #             self.api_base + 'users/?page=' + str(i),
    #             user=True
    #         )))
    #
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(asyncio.wait(tasks))
    #
    # def call_institution_api_pages(self, pages=0):
    #     tasks = []
    #     for i in range(1, pages + 1):
    #         tasks.append(asyncio.ensure_future(self.call_and_parse_api_page(
    #             self.api_base + 'institutions/?page=' + str(i),
    #             institution=True
    #         )))
    #
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(asyncio.wait(tasks))

    # async def call_and_parse_api_page(self, url, node=False, user=False, institution=False):
    async def call_and_parse_api_page(self, url, node=False):

        if node:
            async with aiohttp.ClientSession() as s:
                print('Nodes API request sent')
                response = await s.get(url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for element in data:
                    self.node_url_list.append(self.http_base + element['id'] + '/')
                    self.node_url_list.append(self.http_base + element['id'] + '/files/')
                    self.node_url_list.append(self.http_base + element['id'] + '/registrations/')
                    self.node_url_list.append(self.http_base + element['id'] + '/forks/')
                    self.node_url_list.append(self.http_base + element['id'] + '/analytics/')
                    self.node_url_list.append(self.http_base + element['id'] + '/wiki/home/')

        # if user:
        #     async with aiohttp.ClientSession() as s:
        #         print('Users API request sent')
        #         response = await s.get(url)
        #         body = await response.read()
        #         response.close()
        #         json_body = json.loads(body.decode('utf-8'))
        #         data = json_body['data']
        #         for element in data:
        #             self.user_url_list.append(self.http_base + element['id'] + '/')
        #
        # if institution:
        #     async with aiohttp.ClientSession() as s:
        #         print('Users API request sent')
        #         response = await s.get(url)
        #         body = await response.read()
        #         response.close()
        #         json_body = json.loads(body.decode('utf-8'))
        #         data = json_body['data']
        #         for element in data:
        #             self.institution_url_list.append(self.http_base + 'institutions' + element['id'] + '/')

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
    make_dirs(page)
    f = open(page + 'index.html', 'wb')
    f.write(html)
    f.close()
    os.chdir(sys.path[0])


def make_dirs(filename):
    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        os.makedirs(folder)


# Execution

a = datetime.datetime.now()
c = Crawler()
c.call_api_pages(pages=limit)
c.call_user_api_pages(pages=limit)
# c.call_user_api_pages(pages=10)
#c.call_institution_api_pages(pages=1)
c.scrape_all_nodes()
c.scrape_all_users()
b = datetime.datetime.now()
print(b - a)
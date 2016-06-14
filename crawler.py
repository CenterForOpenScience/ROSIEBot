import asyncio
import aiohttp
import json
import datetime
import os, sys
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

    """
    def __init__(self):
        global base_urls
        self.url_list = []
        self.headers = {
            'User-Agent':
                'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
        }
        self.http_base = base_urls[0]
        self.api_base = base_urls[1]

        self.node_url_list = []
        self.user_url_list = []
        # Shoehorns index in to list of pages to scrape:
        self.institution_url_list = [self.http_base]

# API Crawling

    def call_api_pages(self, api_aspect, pages=5):
        tasks = []
        for i in range(1, pages + 1):
            tasks.append(asyncio.ensure_future(self.call_and_parse_api_page(
                self.api_base + api_aspect + '/?page=' + str(i), api_aspect
            )))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    async def call_and_parse_api_page(self, api_url, api_aspect):
        print('API request sent')

        async with aiohttp.ClientSession() as s:
            response = await s.get(api_url)
            body = await response.read()
            response.close()
            json_body = json.loads(body.decode('utf-8'))
            print(api_url)
            data = json_body['data']
            for element in data:
                if api_aspect == 'nodes':
                    self.node_url_list.append(self.http_base + element['id'] + '/')
                    self.node_url_list.append(self.http_base + element['id'] + '/files/')
                    self.node_url_list.append(self.http_base + element['id'] + '/registrations/')
                    self.node_url_list.append(self.http_base + element['id'] + '/forks/')
                    self.node_url_list.append(self.http_base + element['id'] + '/analytics/')

                    # TODO: Call to crawl wiki
                    self.node_url_list.append(self.http_base + element['id'] + '/wiki/')
                    self.node_url_list.append(self.http_base + element['id'] + '/wiki/home/')

                elif api_aspect == 'users':
                    self.user_url_list.append(self.http_base + element['id'] + '/')

                elif api_aspect == 'institutions':
                    self.institution_url_list.append(self.http_base + element['id'] + '/')

    def scrape_pages(self, aspect_list):
        sem = asyncio.BoundedSemaphore(value=4)
        tasks = []
        for url in aspect_list:
            tasks.append(asyncio.ensure_future(self.scrape_url(url, sem)))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

# Page scraping (through execution)

    async def scrape_url(self, url, sem):
        async with sem:
            async with aiohttp.ClientSession() as s:
                print(url)
                response = await s.get(url, headers=self.headers)
                body = await response.read()
                response.close()
                if response.status is 200:
                    save_html(body, url)
                    print("Finished crawling " + url)
                else:
                    sem2 = asyncio.BoundedSemaphore(value=4)
                    await self.scrape_url(url, sem2)


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

start = datetime.datetime.now()
rosie = Crawler()

# Get URLs from API and add them to the async tasks
rosie.call_api_pages('nodes', pages=1)
rosie.call_api_pages('users', pages=1)

# Don't call this in localhost:
# rosie.call_api_pages('institutions', pages=1)

# Get content from URLs using async methods
rosie.scrape_pages(rosie.node_url_list)
rosie.scrape_pages(rosie.user_url_list)
rosie.scrape_pages(rosie.institution_url_list)

end = datetime.datetime.now()
print(end - start)

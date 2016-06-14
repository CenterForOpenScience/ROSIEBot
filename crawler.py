import asyncio
import aiohttp
import json
import datetime
import os, sys
import settings
import requests
import math

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

        # List of node and node-related pages:
        self.node_dashboard_page_list = [] # Node overview page ("osf.io/node/mst3k/")
        self.node_files_page_list = []
        self.node_wiki_page_list = []
        self.node_analytics_page_list = []
        self.node_registrations_page_list = [] # Page on node that links to registrations
        self.node_forks_page_list = []
        # TODO: Add wiki list

        self.registration_dashboard_page_list = []
        self.registration_files_page_list = []
        self.registration_wiki_page_list = []
        self.registration_analytics_page_list = []
        self.registration_forks_page_list = []

        self.user_profile_page_list = [] # User profile page ("osf.io/profile/mst3k/")
        # Shoehorn index in to list of pages to scrape:
        self.institution_url_list = [self.http_base] # Institution page ("osf.io/institution/cos")

# API Crawling

    # TODO: Investigate making semaphore an instance object

    def crawl_nodes_api(self, page_limit=0):
        sem = asyncio.BoundedSemaphore(value=10)
        # Request number of pages in nodes API
        with requests.Session() as s:
            response = s.get(self.api_base + 'nodes/')
            j = response.json()
            num_pages = math.ceil(j['links']['meta']['total'] / j['links']['meta']['per_page'])
            if num_pages < page_limit or page_limit == 0:
                page_limit = num_pages
        tasks = []
        for i in range(1, page_limit + 1):
            tasks.append(asyncio.ensure_future(self.parse_nodes_api(
                self.api_base + 'nodes/?page=' + str(i),
                sem
            )))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    # Wiki api call requires special code from Cameron's branch (feature/wiki)

    def crawl_registrations_api(self, page_limit=0):
        sem = asyncio.BoundedSemaphore(value=10)

        # Request number of pages in nodes API
        with requests.Session() as s:
            response = s.get(self.api_base + 'registrations/')
            j = response.json()
            num_pages = math.ceil(j['links']['meta']['total'] / j['links']['meta']['per_page'])
            if j['links']['meta']['total'] == 0:
                print("No registrations.")
                return
            if num_pages < page_limit or page_limit == 0:
                page_limit = num_pages
        tasks = []
        for i in range(1, page_limit + 1):
            tasks.append(asyncio.ensure_future(self.parse_registrations_api(
                self.api_base + 'registrations/?page=' + str(i),
                sem
            )))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    def crawl_users_api(self, page_limit=0):
        sem = asyncio.BoundedSemaphore(value=10)

        # Request number of pages in nodes API
        with requests.Session() as s:
            response = s.get(self.api_base + 'users/')
            j = response.json()
            num_pages = math.ceil(j['links']['meta']['total'] / j['links']['meta']['per_page'])
            if num_pages < page_limit or page_limit == 0:
                page_limit = num_pages
        tasks = []
        for i in range(1, page_limit + 1):
            tasks.append(asyncio.ensure_future(self.parse_users_api(
                self.api_base + 'users/?page=' + str(i),
                sem
            )))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    def crawl_institutions_api(self, page_limit=0):
        sem = asyncio.BoundedSemaphore(value=10)

        # Request number of pages in nodes API
        with requests.Session() as s:
            response = s.get(self.api_base + 'institutions/')
            j = response.json()
            num_pages = math.ceil(j['links']['meta']['total'] / j['links']['meta']['per_page'])
            if j['links']['meta']['total'] == 0:
                print("No institutions.")
                return
            if num_pages < page_limit or page_limit == 0:
                page_limit = num_pages
        tasks = []
        for i in range(1, page_limit + 1):
            tasks.append(asyncio.ensure_future(self.parse_institutions_api(
                self.api_base + 'institutions/?page=' + str(i),
                sem
            )))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    # Go through pages for each API endpoint

    async def parse_nodes_api(self, api_url, sem):
        print('API request sent')
        async with sem:
            async with aiohttp.ClientSession() as s:
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                print(api_url)
                data = json_body['data']
                for element in data:
                    self.node_dashboard_page_list.append(self.http_base + 'project/' + element['id'] + '/')
                    self.node_files_page_list.append(self.http_base + 'project/' + element['id'] + '/files/')
                    self.node_analytics_page_list.append(self.http_base + 'project/' + element['id'] + '/analytics/')
                    self.node_registrations_page_list.append(self.http_base + 'project/' + element['id'] + '/registrations/')
                    self.node_forks_page_list.append(self.http_base + 'project/' + element['id'] + '/forks/')

    async def parse_registrations_api(self, api_url, sem):
        print('API request sent')
        async with sem:
            async with aiohttp.ClientSession() as s:
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                print(api_url)
                data = json_body['data']
                for element in data:
                    self.registration_dashboard_page_list.append(self.http_base + element['id'] + '/')
                    self.registration_files_page_list.append(self.http_base + element['id'] + '/files/')
                    self.registration_analytics_page_list.append(self.http_base + element['id'] + '/analytics/')
                    self.registration_forks_page_list.append(self.http_base + element['id'] + '/forks/')

    async def parse_users_api(self, api_url, sem):
        print('API request sent')

        async with sem:
            async with aiohttp.ClientSession() as s:
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                print(api_url)
                data = json_body['data']
                for element in data:
                    self.node_dashboard_page_list.append(self.http_base + 'profile/' + element['id'] + '/')
                    self.node_files_page_list.append(self.http_base + 'profile/' + element['id'] + '/files/')
                    self.node_analytics_page_list.append(self.http_base + 'profile/' + element['id'] + '/analytics/')
                    self.node_registrations_page_list.append(self.http_base + 'profile/' + element['id'] + '/registrations/')
                    self.node_forks_page_list.append(self.http_base + 'profile/' + element['id'] + '/forks/')

    async def parse_institutions_api(self, api_url, sem):
        print('API request sent')

        async with sem:
            async with aiohttp.ClientSession() as s:
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                print(api_url)
                data = json_body['data']
                for element in data:
                    self.node_dashboard_page_list.append(self.http_base + 'institution/' + element['id'] + '/')
                    self.node_files_page_list.append(self.http_base + 'institution/' + element['id'] + '/files/')
                    self.node_analytics_page_list.append(self.http_base + 'institution/' + element['id'] + '/analytics/')
                    self.node_registrations_page_list.append(self.http_base + 'institution/' + element['id'] + '/registrations/')
                    self.node_forks_page_list.append(self.http_base + 'institution/' + element['id'] + '/forks/')

    # Get page content
    def scrape_pages(self, aspect_list):
        sem = asyncio.BoundedSemaphore(value=5)
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
                if response.status == 200:
                    save_html(body, url)
                    print("Finished crawling " + url)
                elif response.status == 504:
                    sem_2 = asyncio.BoundedSemaphore(value=5)
                    await self.scrape(self, url, sem_2)

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
rosie.crawl_nodes_api()
rosie.crawl_registrations_api()
rosie.crawl_users_api()
rosie.crawl_institutions_api()

# List of node and node-related pages:
rosie.scrape_pages(rosie.node_dashboard_page_list)  # Node overview page ("osf.io/node/mst3k/")
rosie.scrape_pages(rosie.node_files_page_list)
rosie.scrape_pages(rosie.node_wiki_page_list)
rosie.scrape_pages(rosie.node_analytics_page_list)
rosie.scrape_pages(rosie.node_registrations_page_list)  # Page on node that links to registrations
rosie.scrape_pages(rosie.node_forks_page_list)
# TODO: Add wiki list

rosie.scrape_pages(rosie.registration_dashboard_page_list)
rosie.scrape_pages(rosie.registration_files_page_list)
rosie.scrape_pages(rosie.registration_wiki_page_list)
rosie.scrape_pages(rosie.registration_analytics_page_list)
rosie.scrape_pages(rosie.registration_forks_page_list)

rosie.scrape_pages(rosie.user_profile_page_list)  # User profile page ("osf.io/profile/mst3k/")
rosie.scrape_pages(rosie.institution_url_list)  # Institution page ("osf.io/institution/cos")


end = datetime.datetime.now()
print(end - start)

import asyncio
import aiohttp
import json
import datetime
import os, sys
import settings
import requests
import math
import collections
import logging
import urllib.parse
import shelve

# Configure for testing in settings.py
base_urls = settings.base_urls
# limit = settings.limit


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

    def __init__(self, date_modified=None, db=None):
        self.headers = {
            'User-Agent':
                'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
        }
        self.http_base = base_urls[0]
        self.api_base = base_urls[1]

        if date_modified is not None:
            self.date_modified_marker = date_modified

        self.node_urls = []  # urls for the node-related pages, in time order from oldest to newest, grouped by node
        self.registration_urls = []
        self._node_wikis_by_parent_guid = collections.defaultdict(list)  # private instance variable for wiki utils
        self._registration_wikis_by_parent_guid = collections.defaultdict(list)

        # For sorting
        self.node_url_tuples = []
        self.registration_url_tuples = []

        self.user_profile_page_urls = [] # User profile page ("osf.io/profile/mst3k/")
        # Shoehorn index in to list of pages to scrape:
        self.institution_urls = [self.http_base] # Institution page ("osf.io/institution/cos")

        # List of 504s:
        self.error_list = []

        # Logging utils

        logging.basicConfig(level=logging.DEBUG)
        # Logger for all debug infos
        self.debug_logger = logging.getLogger('debug')
        self.debug_logger.propagate = 0
        # Console handler for debug logger
        self.console_log_handler = logging.StreamHandler()
        self.console_log_handler.setLevel(logging.DEBUG)
        # Debug file handler for debug logger
        self.debug_log_handler = logging.FileHandler(settings.DEBUG_LOG_FILENAME, mode='w')
        self.debug_log_handler.setLevel(logging.DEBUG)
        # Error file handler for debug logger
        self.error_log_handler = logging.FileHandler(settings.ERROR_LOG_FILENAME, mode='w')
        self.error_log_handler.setLevel(logging.ERROR)
        # Adding handlers to debug logger
        self.debug_logger.addHandler(self.console_log_handler)
        self.debug_logger.addHandler(self.debug_log_handler)
        self.debug_logger.addHandler(self.error_log_handler)

        # Database for persistent saving
        if db is None:
            self.database = shelve.open("tmp.task", writeback=True)
        else:
            self.database = db

    def _truncate_node_url_tuples(self):
        if self.date_modified_marker is not None:
            self.node_url_tuples = [x for x in self.node_url_tuples if x[1] >= self.date_modified_marker]
            self.debug_logger.info("node_url_tuples truncated according to date_modified_marker: " +
                                   str(self.date_modified_marker))

    def _truncate_registration_url_tuples(self):
        if self.date_modified_marker is not None:
            self.registration_url_tuples = [x for x in self.registration_url_tuples if x[1] >= self.date_modified_marker]
            self.debug_logger.info("registration_url_tuples truncated according to date_modified_marker: " +
                                   str(self.date_modified_marker))

# API Crawling

    # TODO: Investigate making semaphore an instance object

    def crawl_nodes_api(self, page_limit=0):
        self.debug_logger.info("Start crawling nodes API pages")
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
        self._truncate_node_url_tuples()

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
        self._truncate_registration_url_tuples()

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

# API Scraping

    async def parse_nodes_api(self, api_url, sem):
        async with sem:
            async with aiohttp.ClientSession() as s:
                self.debug_logger.info("Crawling nodes api, url = " + api_url)
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for element in data:
                    date_str = element['attributes']['date_modified']
                    if '.' in date_str:
                        date = datetime.datetime.strptime(date_str,"%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                    self.node_url_tuples.append((self.http_base + 'project/' + element['id'] + '/', date))
                    self.node_url_tuples.sort(key=lambda x: x[1])

    async def parse_registrations_api(self, api_url, sem):
        async with sem:
            async with aiohttp.ClientSession() as s:
                self.debug_logger.info("Crawling registrations api, url = " + api_url)
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for element in data:
                    date_str = element['attributes']['date_modified']
                    # TODO: probably not a good long term solution. should change this
                    if date_str is None:
                        date_str = element['attributes']['date_registered']
                    if '.' in date_str:
                        date = datetime.datetime.strptime(date_str,"%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                    self.registration_url_tuples.append((self.http_base + element['id'] + '/', date))
                    self.registration_url_tuples.sort(key=lambda x: x[1])

    async def parse_users_api(self, api_url, sem):
        async with sem:
            async with aiohttp.ClientSession() as s:
                self.debug_logger.info("Crawling users api, url = " + api_url)
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for element in data:
                    self.user_profile_page_urls.append(self.http_base + 'profile/' + element['id'] + '/')

    async def parse_institutions_api(self, api_url, sem):
        async with sem:
            async with aiohttp.ClientSession() as s:
                self.debug_logger.info("Crawling institutions api, url = " + api_url)
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for element in data:
                    self.institution_urls.append(self.http_base + 'institutions/' + element['id'] + '/')

# Generating URLs for Nodes and Registrations

    def generate_node_urls(self, all_pages=True, dashboard=False, files=False,
                           wiki=False, analytics=False, registrations=False, forks=False):

        if all_pages or wiki:
            self.crawl_node_wiki()

        self.debug_logger.info("Generating node urls")
        self.debug_logger.info(" all_pages = " + str(all_pages) +
                               " dashboard = " + str(dashboard) +
                               " files = " + str(files) +
                               " wiki = " + str(wiki) +
                               "analytics = " + str(analytics) +
                               " registrations = " + str(registrations) +
                               " forks = " + str(forks)
                               )

        url_list = [x[0] for x in self.node_url_tuples]

        for base_url in url_list:
            if all_pages or dashboard:
                self.node_urls.append(base_url)
            if all_pages or files:
                self.node_urls.append(base_url + 'files/')
            if all_pages or wiki:
                wiki_name_list = self._node_wikis_by_parent_guid[base_url.strip("/").split("/")[-1]]
                wiki_url_list = [base_url + 'wiki/' + urllib.parse.quote(x) + '/' for x in wiki_name_list]
                self.node_urls += wiki_url_list

                # the strip split -1 bit returns the last section of the base_url, which is the GUId
            if all_pages or analytics:
                self.node_urls.append(base_url + 'analytics/')
            if all_pages or registrations:
                self.node_urls.append(base_url + 'registrations/')
            if all_pages or forks:
                self.node_urls.append(base_url + 'forks/')

    def generate_registration_urls(self, all_pages=True, dashboard=False, files=False,
                                wiki=False, analytics=False, forks=False):

        if all_pages or wiki:
            self.crawl_registration_wiki()

        self.debug_logger.info("Generating registration urls")
        self.debug_logger.info(" all_pages = " + str(all_pages) +
                               " dashboard = " + str(dashboard) +
                               " files = " + str(files) +
                               " wiki = " + str(wiki) +
                               "analytics = " + str(analytics) +
                               " forks = " + str(forks)
                               )

        url_list = [x[0] for x in self.registration_url_tuples]

        for base_url in url_list:
            if all_pages or dashboard:
                self.registration_urls.append(base_url)
            if all_pages or files:
                self.registration_urls.append(base_url + 'files/')
            if all_pages or wiki:
                # the strip split -1 bit returns the last section of the base_url, which is the GUId
                wiki_name_list = self._registration_wikis_by_parent_guid[base_url.strip("/").split("/")[-1]]
                wiki_url_list = [base_url + 'wiki/' + urllib.parse.quote(x) + '/' for x in wiki_name_list]
                self.registration_urls += wiki_url_list
            if all_pages or analytics:
                self.registration_urls.append(base_url + 'analytics/')
            if all_pages or forks:
                self.registration_urls.append(base_url + 'forks/')

# Resolving wiki links for Nodes

    def crawl_node_wiki(self):
        tasks = []
        sem = asyncio.BoundedSemaphore(value=5)
        for node_url in [x[0] for x in self.node_url_tuples]:
            tasks.append(asyncio.ensure_future(self.get_node_wiki_names(node_url.strip('/').split('/')[-1], sem)))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    # Async method called by crawl_wiki

    async def get_node_wiki_names(self, parent_node, sem):
        async with sem:
            async with aiohttp.ClientSession() as s:
                u = self.api_base + 'nodes/' + parent_node + '/wikis/'
                self.debug_logger.info("Crawling nodes api, url = " + u)
                response = await s.get(u)
                body = await response.read()
                response.close()
                if response.status <= 200:
                    json_body = json.loads(body.decode('utf-8'))
                    data = json_body['data']
                    for datum in data:
                        try:
                            self._node_wikis_by_parent_guid[parent_node].append(datum['attributes']['name'])
                        except KeyError:
                            self.debug_logger.critical("Fail api call on " + u)


# Resolving wiki links for Registrations

    def crawl_registration_wiki(self):
        tasks = []
        sem = asyncio.BoundedSemaphore(value=5)
        for node_url in [x[0] for x in self.registration_url_tuples]:
            tasks.append(asyncio.ensure_future(self.get_registration_wiki_names(node_url.strip('/').split('/')[-1], sem)))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    # Async method called by crawl_wiki
    async def get_registration_wiki_names(self, parent_node, sem):
        async with sem:
            async with aiohttp.ClientSession() as s:
                u = self.api_base + 'registrations/' + parent_node + '/wikis/'
                self.debug_logger.info("Crawling registrations api, url = " + u)
                response = await s.get(u)
                body = await response.read()
                response.close()
                if response.status <= 200:
                    json_body = json.loads(body.decode('utf-8'))
                    data = json_body['data']
                    for datum in data:
                        try:
                            self._registration_wikis_by_parent_guid[parent_node].append(datum['attributes']['name'])
                        except:
                            pass


# Wrapper methods for scraping different type of pages

# Wrapper methods for scraping different types of pages
    def scrape_nodes(self, async=True):
        self.debug_logger.info("Scraping nodes, async = " + str(async))
        if async:
            self._scrape_pages(self.node_urls)
        else:
            for elem in self.node_url_tuples:
                lst = []
                while len(self.node_urls) > 0 and elem[0] in self.node_urls[0]:
                    lst.append(self.node_urls.pop(0))
                if len(lst) > 0:
                    self._scrape_pages(lst)

    def scrape_registrations(self, async=True):
        self.debug_logger.info("Scraping registrations, async = " + str(async))
        if async:
            self._scrape_pages(self.registration_urls)
        else:
            for elem in self.registration_url_tuples:
                lst = []
                while len(self.registration_urls) > 0 and elem[0] in self.registration_urls:
                    lst.append(self.registration_urls.pop(0))
                self._scrape_pages(lst)

    def scrape_users(self):
        self.debug_logger.info("Scraping users")
        self._scrape_pages(self.user_profile_page_urls)

    def scrape_institutions(self):
        self.debug_logger.info("Scraping institutions")
        self._scrape_pages(self.institution_urls)

# Wrapper method for scraping a list of pages
    def _scrape_pages(self, aspect_list):
        sem = asyncio.BoundedSemaphore(value=5)
        tasks = []
        for url in aspect_list:
            tasks.append(asyncio.ensure_future(self.scrape_url(url, sem)))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

# Async method for actual scraping
    async def scrape_url(self, url, sem):
        async with sem:
            async with aiohttp.ClientSession() as s:
                response = await s.get(url, headers=self.headers)
                body = await response.read()
                response.close()
                if response.status == 200:
                    self.debug_logger.debug("Finished : " + url)
                    self.record_milestone(url)
                    save_html(body, url)
                else:
                    self.debug_logger.debug(str(response.status) + " on : " + url)
                    self.error_list.append(url)
                    self.database['error_list'] = self.error_list

# Method to record the milestone
    def record_milestone(self, url):
        self.database['milestone'] = url


def save_html(html, page):
    page = page.split('//', 1)[1]
    if page[-1] != '/':
        page += '/'
    make_dirs(page)
    f = open(page + 'index.html', 'wb+')
    f.write(html)
    f.close()
    os.chdir(sys.path[0])


def make_dirs(filename):
    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        os.makedirs(folder)

import asyncio
import aiohttp
import json
import datetime
import os
import sys
import settings
import requests
import math
import collections
import logging
import tqdm

# Configure for testing in settings.py
from settings import base_urls


class Crawler:
    """
    A Crawler class for crawling and scraping OSF's API V2 and scrape different pages.
    A CLI is designed to work with this crawler. However, in case of needs you may use
    the crawler instance in an ad-hoc manner.
    Basic Workflow:
        Init -> crawl the API -> scrape pages
        During the API crawl, page urls will be stored in:
            self.node_urls
            self.registration_urls
            self.user_urls
            self.institution_urls
        and methods for scraping pages will scrape according to
        the urls stored in those lists.
    """

    def __init__(self, date_modified=None, db=None, dictionary=None):
        """
        Constructor for the Crawler class

        :param date_modified: Cut off date for scraping. Nodes modified prior to this date is ignored during scraping
        :param db: File descriptor for reading information from persistent file
        :param dictionary: A dictionary that stores copy of persistent file
        """
        # Use this header in request to trigger Prerender
        self.headers = {
            'User-Agent':
                'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
        }
        self.http_base = base_urls[0]
        self.api_base = base_urls[1]

        if date_modified is not None:
            self.date_modified_marker = date_modified
        else:
            self.date_modified_marker = datetime.datetime.strptime('1970-01-01T00:00:00', "%Y-%m-%dT%H:%M:%S")

        # Stores all the urls generated by generate_node_urls()
        self.node_urls = []  # urls for the node-related pages, in time order from oldest to newest, grouped by node
        # Stores all the urls generated by generate_registration_urls()
        self.registration_urls = []
        # Stores all the urls for user profile pages
        self.user_urls = []  # User profile page ("osf.io/profile/mst3k/")
        # Stores all the urls for institutions
        self.institution_urls = [self.http_base]  # Institution page ("osf.io/institution/cos")
        # General pages
        self.general_urls = [self.http_base, self.http_base + 'support/']
        # List of 504s:
        self.error_list = []
        # For sorting
        self.node_url_tuples = []
        self.registration_url_tuples = []

        # Utility lists for use by wiki-related api Crawls
        self._node_wikis_by_parent_guid = collections.defaultdict(list)  # private instance variable for wiki utils
        self._registration_wikis_by_parent_guid = collections.defaultdict(list)

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

        # File descriptor for persistent saving
        if db is None:
            self.database = None
        else:
            self.database = db

        # Holds temporary copy of persistent file in memory
        self.dictionary = dictionary

    def _truncate_registration_url_tuples(self):
        """
        Called by crawl_registrations_api() to truncate self.registration_url_tuples according to
        self.date_modified_marker so that registrations that are updated before the date_modified_marker
        chronologically will be discarded
        """
        if self.date_modified_marker is not None:
            self.registration_url_tuples = [x for x in self.registration_url_tuples if x[1] >= self.date_modified_marker]
            self.debug_logger.info("registration_url_tuples truncated according to date_modified_marker: " +
                                   str(self.date_modified_marker))

    async def _wait_with_progress_bar(self, tasks):
        for task in tqdm.tqdm(tasks, total=len(tasks)):
            await task

# API Crawling
    def crawl_nodes_api(self, page_limit=0):
        """
        The runner method that runs parse_nodes_api(), which will populate the list of self.node_url_tuples.
        After self.node_url_tuples is populated, _truncate_node_url_tuples() will be called to truncate the list
        according to self.date_modified_marker.
        :param page_limit: Number of pages of API to crawl. If page_limit=0, then crawl all pages.
        """
        self.debug_logger.info("Start crawling nodes API pages")
        sem = asyncio.BoundedSemaphore(value=10)
        # Request number of pages in nodes API
        with requests.Session() as s:
            response = s.get(self.api_base + 'nodes/' + '?filter[date_modified][gte]=' + self.date_modified_marker.isoformat(sep='T'))
            j = response.json()
            num_pages = math.ceil(j['links']['meta']['total'] / j['links']['meta']['per_page'])
            if num_pages < page_limit or page_limit == 0:
                page_limit = num_pages
        tasks = []
        for i in range(1, page_limit + 1):
            tasks.append(asyncio.ensure_future(self.parse_nodes_api(
                self.api_base + 'nodes/' + '?filter[date_modified][gte]=' +
                self.date_modified_marker.isoformat(sep='T') +
                '&page=' + str(i),
                sem
            )))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._wait_with_progress_bar(tasks))

    def crawl_registrations_api(self, page_limit=0):
        """
        The runner method that runs parse_registrations_api(), which will populate the list of
        self.registration_url_tuples.
        After self.registration_url_tuples is populated, _truncate_registration_url_tuples() will be called to truncate
        the list according to self.date_modified_marker.
        :param page_limit: Number of pages of API to crawl. If page_limit=0, then crawl all pages.
        """
        # Setting a semaphore for rate limiting
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
        loop.run_until_complete(self._wait_with_progress_bar(tasks))
        self._truncate_registration_url_tuples()

    def crawl_users_api(self, page_limit=0):
        """
        The runner method that runs parse_users_api(), which will populate the list of self.user_urls.
        :param page_limit: Number of pages of API to crawl. If page_limit=0, then crawl all pages.
        """
        # Setting a semaphore for rate limiting
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
        loop.run_until_complete(self._wait_with_progress_bar(tasks))

    def crawl_institutions_api(self, page_limit=0):
        """
        The runner method that runs parse_institutions_api(), which will populate the list of self.institution_urls.
        :param page_limit: Number of pages of API to crawl. If page_limit=0, then crawl all pages.
        """
        # Setting a semaphore for rate limiting
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
        loop.run_until_complete(self._wait_with_progress_bar(tasks))

# API Scraping

    async def parse_nodes_api(self, api_url, sem):
        """
        Asynchronous scraping method that scrapes the V2 Nodes API for list of public facing nodes
        (excluding registrations). Called by crawl_nodes_api(), which is the runner method for crawling the nodes API.
        Compiles a list of self.node_url_tuples that stores tuples as list elements in the format of (url, datetime)
        e.g. ('http://osf.io/project/mst3k', datetime.datetime(2016, 6, 24, 9, 13, 59, 254173))
        self.node_url_tuples will be sorted in ascending order according to the datetime object in the tuple.
        (The tuple that contains earliest datetime object comes first)
        :param api_url: list of V2 Nodes API endpoints to scrape
        :param sem: rate limiting semaphore
        """
        async with sem:
            async with aiohttp.ClientSession() as s:
                # self.debug_logger.info("Crawling nodes api, url = " + api_url)
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for element in data:
                    date_str = element['attributes']['date_modified']
                    if '.' in date_str:
                        date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                    self.node_url_tuples.append((self.http_base + 'project/' + element['id'] + '/', date))
                    self.node_url_tuples.sort(key=lambda x: x[1])

    async def parse_registrations_api(self, api_url, sem):
        """
        Asynchronous scraping method that scrapes the V2 Registrations API for list of registrations
        Called by crawl_registrations_api(), which is the runner method for crawling the Registrations API.
        Compiles a list of self.registration_url_tuples that stores tuples as list elements in the format of
        (url, datetime) e.g. ('http://osf.io/project/mst3k', datetime.datetime(2016, 6, 24, 9, 13, 59, 254173))
        self.registration_url_tuples will be sorted in ascending order according to the datetime object in the tuple.
        (The tuple that contains earliest datetime object comes first)
        :param api_url: list of V2 Registrations API endpoints to scrape
        :param sem: rate limiting semaphore
        """
        async with sem:
            async with aiohttp.ClientSession() as s:
                # self.debug_logger.info("Crawling registrations api, url = " + api_url)
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
                        date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                    self.registration_url_tuples.append((self.http_base + element['id'] + '/', date))
                    self.registration_url_tuples.sort(key=lambda x: x[1])

    async def parse_users_api(self, api_url, sem):
        """
        Asynchronous scraping method that scrapes the V2 Users API for list of users.
        Called by crawl_users_api(), which is the runner method for crawling the Users API.
        Compiles a list of self.user_urls.
        Note: self.user_urls does not persist any order.
        :param api_url: list of V2 Users API endpoints to scrape
        :param sem: rate limiting semaphore
        """
        async with sem:
            async with aiohttp.ClientSession() as s:
                # self.debug_logger.info("Crawling users api, url = " + api_url)
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for element in data:
                    self.user_urls.append(self.http_base + 'profile/' + element['id'] + '/')

    async def parse_institutions_api(self, api_url, sem):
        """
        Asynchronous scraping method that scrapes the V2 Users API for list of users.
        Called by crawl_users_api(), which is the runner method for crawling the Users API.
        Compiles a list of self.user_urls.
        Note: self.user_urls does not persist any order.
        :param api_url: list of V2 Users API endpoints to scrape
        :param sem: rate limiting semaphore
        """
        async with sem:
            async with aiohttp.ClientSession() as s:
                # self.debug_logger.info("Crawling institutions api, url = " + api_url)
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
        """
        Called by the CLI explicitly to generate a list of self.node_urls form self.node_url_tuples.
        If wiki=True or all_pages=True, invoke crawl_node_wiki() to find all the wiki pages of the nodes and add urls
        to self.node_urls

        :param all_pages: whether to scrape all pages of a node
        :param dashboard: whether to scrape node dashboard page
        :param files: whether to scrape node files page
        :param wiki: whether to scrape node wiki page
        :param analytics: whether to scrape node analytics page
        :param registrations: whether to scrape node registrations page
        :param forks: whether to scrape node forks page
        """

        if all_pages or wiki:
            self.crawl_node_wiki()

        self.debug_logger.info("Generating node urls")
        self.debug_logger.info(" all_pages = " + str(all_pages) +
                               " dashboard = " + str(dashboard) +
                               " files = " + str(files) +
                               " wiki = " + str(wiki) +
                               " analytics = " + str(analytics) +
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
                wiki_url_list = [base_url + 'wiki/' + x + '/' for x in wiki_name_list]
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
        """
        Called by the CLI explicitly to generate a list of self.registration_urls form self.registration_url_tuples.

        :param all_pages:
        :param dashboard:
        :param files:
        :param wiki:
        :param analytics:
        :param forks:
        :return:
        """

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
                wiki_url_list = [base_url + 'wiki/' + x + '/' for x in wiki_name_list]
                self.registration_urls += wiki_url_list
            if all_pages or analytics:
                self.registration_urls.append(base_url + 'analytics/')
            if all_pages or forks:
                self.registration_urls.append(base_url + 'forks/')

# Resolving wiki links for Nodes

    def crawl_node_wiki(self):
        """
        Called by generate_node_urls if necessary. This is the runner method to run get_node_wiki_names() in order to
        get the urls of wikis of a node. The urls of wikis will be added to self.node_urls
        """
        tasks = []
        sem = asyncio.BoundedSemaphore(value=5)
        for node_url in [x[0] for x in self.node_url_tuples]:
            tasks.append(asyncio.ensure_future(self.get_node_wiki_names(node_url.strip('/').split('/')[-1], sem)))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._wait_with_progress_bar(tasks))

    # Async method called by crawl_wiki

    async def get_node_wiki_names(self, parent_node, sem):
        """
        Asynchronous scraping method for scraping the V2 Node Wikis API.
        :param parent_node: list of parent nodes to which wiki pages are attached
        :param sem: rate limiting semaphore
        """
        async with sem:
            async with aiohttp.ClientSession() as s:
                u = self.api_base + 'nodes/' + parent_node + '/wikis/'
                # self.debug_logger.info("Crawling nodes api, url = " + u)
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
        """
        Called by generate_registration_urls if necessary. This is the runner method to run
        get_registration_wiki_names() in order to get the urls of wikis of a registration.
        The urls of wikis will be added to self.registration_urls
        """
        tasks = []
        sem = asyncio.BoundedSemaphore(value=5)
        for node_url in [x[0] for x in self.registration_url_tuples]:
            tasks.append(asyncio.ensure_future(self.get_registration_wiki_names(node_url.strip('/').split('/')[-1], sem)))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._wait_with_progress_bar(tasks))

    # Async method called by crawl_wiki
    async def get_registration_wiki_names(self, parent_node, sem):
        """
        Asynchronous scraping method for scraping the V2 Registrations Wikis API.
        :param parent_node: list of parent nodes to which wiki pages are attached
        :param sem: rate limiting semaphore
        """
        async with sem:
            async with aiohttp.ClientSession() as s:
                u = self.api_base + 'registrations/' + parent_node + '/wikis/'
                # self.debug_logger.info("Crawling registrations api, url = " + u)
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
        """
        Wrapper method that scrape all urls in self.node_urls. Calls _scrape_pages().
        :param async: if False, will finish all pages of one node before starting pages of next node
        """
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
        """
        Wrapper method that scrape all urls in self.registration_urls. Calls _scrape_pages().
        :param async: if False, will finish all pages of one registration before starting pages of next registration
        """
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
        """
        Wrapper method that scrape all urls in self.user_urls. Calls _scrape_pages().
        """
        self.debug_logger.info("Scraping users")
        self._scrape_pages(self.user_urls)

    def scrape_institutions(self):
        """
        Wrapper method that scrape all institution_urls. Calls _scrape_pages().
        """
        self.debug_logger.info("Scraping institutions")
        self._scrape_pages(self.institution_urls)

    def scrape_general(self):
        """ Index and support page """
        self._scrape_pages(self.general_urls)

# Wrapper method for scraping a list of pages
    def _scrape_pages(self, aspect_list):
        """
        Runner method that runs scrape_url()
        :param aspect_list: list of url of pages to scrape
        """
        sem = asyncio.BoundedSemaphore(value=1)
        tasks = []
        for url in aspect_list:
            tasks.append(asyncio.ensure_future(self.scrape_url(url, sem)))

        loop = asyncio.get_event_loop()
        if len(tasks) > 0:
            loop.run_until_complete(self._wait_with_progress_bar(tasks))
        else:
            print("No pages to scrape.")

# Async method for actual scraping
    async def scrape_url(self, url, sem):
        """
        Asynchronous method that scrape page. Calls save_html() to save scraped page to file.
        Calls record_milestone() to save progress
        :param url: url to scrape
        :param sem: rate limitin semaaphore.
        :return:
        """
        async with sem:
            async with aiohttp.ClientSession() as s:
                response = await s.get(url, headers=self.headers)
                body = await response.text()
                response.close()
                if response.status == 200:
                    # self.debug_logger.debug("Finished : " + url)
                    self.record_milestone(url)
                    save_html(body, url)
                else:
                    self.debug_logger.debug(str(response.status) + " on : " + url)
                    if self.database is not None:
                        self.error_list.append(url)
                        self.dictionary['error_list'] = self.error_list
                        self.database.seek(0)
                        self.database.truncate()
                        json.dump(self.dictionary, self.database, indent=4)
                        self.database.flush()

# Method to record the milestone
    def record_milestone(self, url):
        """
        Called by scrape_url to keep track of progress.
        :param url: url of the page that finished
        """
        if self.database is not None:
            self.dictionary['milestone'] = url
            self.database.seek(0)
            self.database.truncate()
            json.dump(self.dictionary, self.database, indent=4)
            self.database.flush()


def save_html(html, page):
    # Mirror warning
    mirror_warning = """
        <div style="position:fixed;    bottom:0;left:0;    border-top-right-radius: 8px;    color:  white;
        background-color: red;  padding: .5em;">
            This is a read-only mirror of the OSF. Some features may not be available.
        </div>
        """

    # Remove the footer
    old_footer = """<div id="footerSlideIn" style="display: block;">"""
    new_footer = """<div id="footerSlideIn" style="display: none;">"""

    page = page.split('//', 1)[1]
    page = page.split('/', 1)[1]
    page = 'archive/' + page
    if page[-1] != '/':
        page += '/'
    make_dirs(page)

    html = html.replace(old_footer, new_footer) + mirror_warning

    f = open(page + 'index.html', 'w')
    f.write(html)
    f.close()
    os.chdir(sys.path[0])


def make_dirs(filename):
    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        os.makedirs(folder)

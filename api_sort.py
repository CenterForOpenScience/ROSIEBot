import asyncio
import aiohttp
import json
import datetime
import os, sys
import settings
import requests
import math
from random import shuffle
import collections

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

    def __init__(self, date_modified=None):
        self.headers = {
            'User-Agent':
                'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
        }
        self.http_base = base_urls[0]
        self.api_base = base_urls[1]

        if date_modified is not None:
            self.date_modified_marker = date_modified

        self.node_urls = []

        self.wikis_by_parent_guid = collections.defaultdict(list)

        # for sorting
        self.node_url_tuples = []
        self.log = open("error_log.txt", "w+")
        self.crawled_url_log = None
        self.goal_urls = None

        # if os.path.isfile('goal_urls.txt') and os.path.isfile('crawled_url_log.txt'):
        #     self.scrape_diff()

    def __del__(self):
        if self.log is not None:
            self.log.close()
        if self.crawled_url_log is not None:
            self.crawled_url_log.close()
        if self.goal_urls is not None:
            self.goal_urls.close()

    def scrape_diff(self):
        s1 = set(open("goal_urls.txt").readlines())
        s2 = set(open("crawled_url_log.txt").readlines())
        d = list(s1.difference(s2))
        for x in d:
            print(x)
        if len(d) > 0:
            self._scrape_pages(d)
        else:
            print("no diff :)")

    def truncate_node_url_tuples(self):
        if self.date_modified_marker is not None:
            self.node_url_tuples = [x for x in self.node_url_tuples if x[1] > self.date_modified_marker]
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
        # print('API request sent')
        async with sem:
            async with aiohttp.ClientSession() as s:
                response = await s.get(api_url)
                body = await response.read()
                response.close()
                json_body = json.loads(body.decode('utf-8'))
                print(api_url)
                data = json_body['data']
                for element in data:
                    date_str = element['attributes']['date_modified']
                    # print(date_str)
                    if '.' in date_str:
                        date = datetime.datetime.strptime(element['attributes']['date_modified'], "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        date = datetime.datetime.strptime(element['attributes']['date_modified'], "%Y-%m-%dT%H:%M:%S")
                    # >> .%f
                    self.node_url_tuples.append((self.http_base + 'project/' + element['id'] + '/', date))

                    rosie.node_url_tuples.sort(key=lambda x: x[1])

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

    def generate_node_urls(self, all_pages=True, dashboard=False, files=False, wiki=False, analytics=False, registrations=False, forks=False):
        url_list = [x[0] for x in self.node_url_tuples]

        for base_url in url_list:
            if all_pages or dashboard:
                self.node_urls.append(base_url)
            if all_pages or files:
                self.node_urls.append(base_url + 'files/')
            if all_pages or wiki:
                self.node_urls += self.wikis_by_parent_guid[base_url.strip("/").split("/")[-1]]
                # the strip split -1 bit returns the last section of the base_url, which is the GUId
            if all_pages or analytics:
                self.node_urls.append(base_url + 'analytics/')
            if all_pages or registrations:
                self.node_urls.append(base_url + 'registrations/')
            if all_pages or forks:
                self.node_urls.append(base_url + 'forks/')

    # call this method after tuple list truncation and before generate_node_urls
    def crawl_wiki(self):
        tasks = []
        for node in [x[0] for x in self.node_url_tuples]:
            tasks.append(asyncio.ensure_future(self.get_wiki_names(node)))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        print(self.wikis_by_parent_guid)

    async def get_wiki_names(self, parent_node):
        async with aiohttp.ClientSession() as s:
            response = await s.get(self.api_base + 'nodes/' + parent_node + '/wikis/')
            print("GET'd " + self.api_base + 'nodes/' + parent_node + '/wikis/')
            body = await response.read()
            response.close()
            if response.status <= 200:
                json_body = json.loads(body.decode('utf-8'))
                data = json_body['data']
                for datum in data:
                    self.wikis_by_parent_guid[parent_node].append(datum['attributes']['name'])
            else:
                print('Status Code: ', response.status)

    # async def get_wiki_real_link(self, parent_node, name):
    #     async with aiohttp.ClientSession() as s:
    #         response = await s.request('get', self.http_base + 'project/' + parent_node + '/wiki/' + name)
    #         self.wiki_url_list.append(self.http_base + 'project/' + parent_node + '/wiki/' + name)
    #         print(response.url)
    #         response.close()

    def scrape_nodes(self, async=True):
        if async:
            self._scrape_pages(self.node_urls)
        else:
            for elem in self.node_url_tuples:
                list = []
                while len(self.node_urls) > 0 and elem[0] in self.node_urls[0]:
                    list.append(self.node_urls.pop(0))
                self._scrape_pages(list)

    # Get page content
    def _scrape_pages(self, aspect_list):
        sem = asyncio.BoundedSemaphore(value=5)
        tasks = []
        for url in aspect_list: # TODO: change to "if weekday mod % 7 == 1"
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
                    # self.crawled_url_log.write(url+"\n")
                elif response.status == 504:
                    # output url to log
                    print("504")
                    # self.log.write("504 TIMEOUT: " + url + "\n")
                    pass
                else:
                    print(str(response.status))


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

#
# # Execution
#
rosie = Crawler()
#
# # Get URLs from API and add them to the async tasks
# rosie.scrape_diff()
rosie.crawl_nodes_api(page_limit=1)
rosie.generate_node_urls(all_pages=True)
rosie.scrape_nodes(async=False)
# rosie.crawl_registrations_api()
# rosie.crawl_users_api()
# rosie.crawl_institutions_api()
#
# # List of node and node-related pages:
# rosie.scrape_pages(rosie.node_dashboard_page_list)  # Node overview page ("osf.io/node/mst3k/")
# rosie.scrape_pages(rosie.node_files_page_list)
# rosie.scrape_pages(rosie.node_wiki_page_list)
# rosie.scrape_pages(rosie.node_analytics_page_list)
# rosie.scrape_pages(rosie.node_registrations_page_list)  # Page on node that links to registrations
# rosie.scrape_pages(rosie.node_forks_page_list)
# # TODO: Add wiki list
#
# rosie.scrape_pages(rosie.registration_dashboard_page_list)
# rosie.scrape_pages(rosie.registration_files_page_list)
# rosie.scrape_pages(rosie.registration_wiki_page_list)
# rosie.scrape_pages(rosie.registration_analytics_page_list)
# rosie.scrape_pages(rosie.registration_forks_page_list)
#
# rosie.scrape_pages(rosie.user_profile_page_list)  # User profile page ("osf.io/profile/mst3k/")
# rosie.scrape_pages(rosie.institution_url_list)  # Institution page ("osf.io/institution/cos")
#
#

# datetime.datetime.strptime( "2007-03-04T21:08:12", "%Y-%m-%dT%H:%M:%S" )

# dt = datetime.datetime.strptime('2012-04-01T15:49:07.702000', "%Y-%m-%dT%H:%M:%S.%f")
# print(dt.isoweekday())


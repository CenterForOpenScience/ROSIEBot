import asyncio
import aiohttp
import os
import sys

absolute_python_root = sys.path[0]
from settings import base_urls

class Rescraper:
    def __init__(self):
        self.http_base = base_urls[0]
        self.failed_urls = []
        self.tries = 3
        self.headers = {
            'User-Agent':
                'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
        }

    def scrape(self, async=True):
        self._scrape_pages(self.failed_urls)

    # Get page content
    def _scrape_pages(self, aspect_list):
        sem = asyncio.BoundedSemaphore(value=5)
        tasks = []
        for url in aspect_list:
            tasks.append(asyncio.ensure_future(self.scrape_url(url, sem)))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    # Page scraping (through to execution)

    async def scrape_url(self, url, sem):
        async with sem:
            async with aiohttp.ClientSession() as s:
                response = await s.get(url, headers=self.headers)
                body = await response.read()
                response.close()
                if response.status == 200:
                    save_html(body, url)
                    message = [url.replace(self.http_base, ''), 'Success: ', str(response.status), '\n']
                else:
                    message = [url.replace(self.http_base, ''), 'Failure: ', str(response.status), '\n']


def save_html(html, page):
    print(page)
    page = page.split('//', 1)[1]
    if page[-1] != '/':
        page += '/'
    make_dirs(page)
    f = open(page + 'index.html', 'wb+')
    f.write(html)
    f.close()
    os.chdir(sys.path[0])


def make_dirs(filename):
    os.chdir(absolute_python_root)
    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        os.makedirs(folder)

"""
Step 4: Try again for failed pages.
"""
from Verification.spot_check import send_to_retry as new_tasks
from Verification.initialize_list import mirror_path ,absolute_python_root
from settings import base_urls
import asyncio
import aiohttp
import os
import sys

success_log = open('Verification/Logs/retry_success.log', 'a')
failure_log = open('Verification/Logs/retry_failure.log', 'a')


class Rescraper:
    def __init__(self):
        self.failed_urls = []
        self.tries = 3
        self.headers = {
            'User-Agent':
                'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
        }
        self.http_base = base_urls[0]
        self.api_base = base_urls[1]
        for task in new_tasks:
            tail = task.replace(mirror_path, '')
            url = self.http_base + tail
            self.failed_urls.append(url)
        print(self.failed_urls)

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
                    success_log.write('\t'.join(message))
                else:
                    message = [url.replace(self.http_base, ''), 'Failure: ', str(response.status), '\n']
                    failure_log.write('\t'.join(message))


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

success_log.close(), failure_log.close()


import json, codecs
import os
import sys
from bs4 import BeautifulSoup
from settings import base_urls
# from rescraper import Rescraper

"""
Pages engineered to fail:

verify_page_exists: 3tmge/files/index.html
size_comparison: 5dewf/files/index.html should be 340 KB
"""

# TODO: put this in settings
NUM_RETRIES = 2
TASK_FILE = '201606231548.json'
MIRROR = '127.0.0.1/'


with codecs.open(TASK_FILE, mode='r', encoding='utf-8') as file:
    run_info = json.load(file)


class Page:
    def __init__(self, url, error=False):
        self.url = url
        self.error = error
        if not error:
            self.path = MIRROR + url.replace(base_urls[0], '') + 'index.html'
            self.file_size = os.path.getsize(self.path)
        else:
            self.path = ''
            self.file_size = 0

    def __str__(self):
        return self.path

    def get_content(self):
        name = file.split('/')[-3] + '/' + file.split('/')[-2]
        soup = BeautifulSoup(open(file), 'html.parser')
        return soup


class ProjectDashboardPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class ProjectFilesPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class ProjectWikiPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class ProjectFilesPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class ProjectAnalyticsPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class ProjectRegistrationsPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class ProjectForksPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class RegistrationDashboardPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class RegistrationFilesPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class RegistrationWikiPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class RegistrationAnalyticsPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class RegistrationForksPage(Page):
    def __int__(self, url, error=False):
        Page.__init__(self, url, error)


class Verifier:
    def __init__(self):
        self.pages = []
        self.minimum_size = 0
        self.page_elements = []
        self.failed_pages = []

    # First actual check
    # Check that each file path in the dictionary actually exists
    def verify_files_exist(self):
        for page in self.pages:
            print(page.path)
            if not os.path.exists(page.path):
                print('Failed: verify_files_exist(): ', page)
                self.failed_pages.append(page)                                  # Add to naughty list
                self.pages.pop(page)                                            # Remove from nice list
        return

    # Second check
    # Compare page size to page-specific minimum that any fully-scraped page should have
    def size_comparison(self):
        for page in self.pages:
            if not page.file_size > self.minimum_size:
                print('Failed: size_comparison(): ', page, ' has size: ', page.file_size)
                self.failed_pages.append(page)
                self.pages.pop(page)
        return

    # Third check
    # Check that specified elements are present and non-empty in each page
    def spot_check(self):
        for page in self.pages:
            soup = page.get_content()
            for element in self.page_elements:
                result = soup.select(element)
                if len(result) == 0 or len(result[0].contents) == 0:    # No results or empty results
                    print('Failed: spot_check(): ', page)
                    self.failed_pages.append(page)
                    self.pages.pop(page)
        return


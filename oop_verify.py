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

retry_list = []

with codecs.open(TASK_FILE, mode='r', encoding='utf-8') as file:
    run_info = json.load(file)


class Page:
    def __init__(self, url):
        self.url = url
        self.path = MIRROR + url.replace(base_urls[0], '') + 'index.html'
        # Set size attribute, inherently checks if file exists
        try:
            self.file_size = os.path.getsize(self.path)
        except FileNotFoundError:
            raise FileNotFoundError

    def __str__(self):
        return self.path

    def get_content(self):
        soup = BeautifulSoup(open(self.path), 'html.parser')
        return soup


class ProjectDashboardPage(Page):
    def __int__(self, url):
        super().__init__(url)


class ProjectFilesPage(Page):
    def __int__(self, url):
        super().__init__(url)


class ProjectWikiPage(Page):
    def __int__(self, url):
        super().__init__(url)


class ProjectAnalyticsPage(Page):
    def __int__(self, url):
        super().__init__(url)


class ProjectRegistrationsPage(Page):
    def __int__(self, url):
        super().__init__(url)


class ProjectForksPage(Page):
    def __int__(self, url):
        super().__init__(url)


class RegistrationDashboardPage(Page):
    def __int__(self, url):
        super().__init__(url)


class RegistrationFilesPage(Page):
    def __int__(self, url):
        super().__init__(url)


class RegistrationWikiPage(Page):
    def __int__(self, url):
        super().__init__(url)


class RegistrationAnalyticsPage(Page):
    def __int__(self, url):
        super().__init__(url)


class RegistrationForksPage(Page):
    def __int__(self, url):
        super().__init__(url)


class UserProfilePage(Page):
    def __int__(self, url):
        super().__init__(url)


class InstitutionProfilePage(Page):
    def __init__(self, url):
        super().__init__(url)


class Verifier:
    def __init__(self):
        self.pages = []
        self.minimum_size = 0
        self.page_elements = []
        self.failed_pages = []

    # Populate self.pages with the relevant files
    def harvest_pages(self, json_list, url_end, page_class):
        """
        :param json_list: The list in the task file of found URLs
        :param url_end: The json_list is non segregated by page type
        :param page_class: The subclass for the specific page type
        :return: Null, but self.pages is populated.
        """
        for url in json_list:
            print(url)
            if url.endswith(url_end):
                print('rel: ', url)
                if url in run_info['error_list']:
                    retry_list.append(url)
                    print('eror: ', url)
                else:
                    try:
                        obj = page_class(url)
                        self.pages.append(obj)
                    except FileNotFoundError:
                        retry_list.append(url)
                json_list.remove(url)

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

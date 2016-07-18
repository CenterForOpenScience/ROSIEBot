""" The page superclass and subclasses for verifier"""

from bs4 import BeautifulSoup
from settings import base_urls
import os
MIRROR = 'archive/'


# Superclass for page-specific page instances
class Page:
    def __init__(self, url):
        self.url = url
        self.path = self.get_path_from_url(url)
        # Set size attribute in KB, inherently checks if file exists
        try:
            self.file_size = os.path.getsize(self.path) / 1000
        except FileNotFoundError:
            raise FileNotFoundError

    def __str__(self):
        return self.path

    # Takes a URL and produces its relative file name.
    def get_path_from_url(self, url):
        # Remove http://domain
        tail = url.replace(base_urls[0], '') + 'index.html'
        path = MIRROR + tail
        return path

    def get_content(self):
        soup = BeautifulSoup(open(self.path), 'html.parser')
        return soup


# Page-specific subclasses
class ProjectDashboardPage(Page):
    def __init__(self, url):
        super().__init__(url)


class ProjectFilesPage(Page):
    def __init__(self, url):
        super().__init__(url)


class ProjectWikiPage(Page):
    def __init__(self, url):
        super().__init__(url)


class ProjectAnalyticsPage(Page):
    def __init__(self, url):
        super().__init__(url)


class ProjectRegistrationsPage(Page):
    def __init__(self, url):
        super().__init__(url)


class ProjectForksPage(Page):
    def __init__(self, url):
        super().__init__(url)


class RegistrationDashboardPage(Page):
    def __init__(self, url):
        super().__init__(url)


class RegistrationFilesPage(Page):
    def __init__(self, url):
        super().__init__(url)


class RegistrationWikiPage(Page):
    def __init__(self, url):
        super().__init__(url)


class RegistrationAnalyticsPage(Page):
    def __init__(self, url):
        super().__init__(url)


class RegistrationForksPage(Page):
    def __init__(self, url):
        super().__init__(url)


class UserProfilePage(Page):
    def __init__(self, url):
        super().__init__(url)


class InstitutionDashboardPage(Page):
    def __init__(self, url):
        super().__init__(url)
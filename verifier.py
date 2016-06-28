import json, codecs
import os
import sys
from bs4 import BeautifulSoup
from settings import base_urls

# from rescraper import Rescraper

"""
Pages engineered to fail:

verify_page_exists: //3tmge/files/index.html
size_comparison: //5dewf/files/index.html should be 340 KB
no instance at all: //68fqs

"""

# TODO: put this in settings
NUM_RETRIES = 2
TASK_FILE = '201606231548.json'
MIRROR = '127.0.0.1/'

with codecs.open(TASK_FILE, mode='r', encoding='utf-8') as file:
    run_info = json.load(file)


# Takes a URL and produces its relative file name.
def get_path_from_url(self, url):
    # Remove http://domain
    tail = url.replace(base_urls[0], '') + 'index.html'
    path = MIRROR + tail
    return path


# Creates a dictionary with filename : URL for all the URLs found by the crawler in the API
def generate_page_dictionary(self):
    for url in self.json_list:
        if url.endswith(self.page + '/') and url not in run_info['error_list']:
            key = self.get_path_from_url(url)
            self.paths[key] = url
            self.json_list.remove(url)
    return


# Superclass for page-specific page instances

class Page:
    def __init__(self, url):
        self.url = url
        self.path = MIRROR + url.replace(base_urls[0], '') + 'index.html'
        # Set size attribute in KB, inherently checks if file exists
        try:
            self.file_size = os.path.getsize(self.path) / 1000
        except FileNotFoundError:
            raise FileNotFoundError

    def __str__(self):
        return self.path

    def get_content(self):
        soup = BeautifulSoup(open(self.path), 'html.parser')
        return soup


# Page-specific subclasses

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


class InstitutionDashboardPage(Page):
    def __init__(self, url):
        super().__init__(url)


# Verifier superclass

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
                    self.failed_pages.append(url)
                    print('eror: ', url)
                else:
                    try:
                        obj = page_class(url)
                        self.pages.append(obj)
                    except FileNotFoundError:
                        self.failed_pages.append(url)
                json_list.remove(url)

    # First check
    # Compare page size to page-specific minimum that any fully-scraped page should have
    def size_comparison(self):
        for page in self.pages:
            print(page)
            print(page.file_size)
            if not page.file_size > self.minimum_size:
                print('Failed: size_comparison(): ', page, ' has size: ', page.file_size)
                self.failed_pages.append(page.url)
        return

    # Second check
    # Check that specified elements are present and non-empty in each page
    def spot_check(self):
        for page in self.pages:
            soup = page.get_content()
            for element in self.page_elements:
                result = soup.select(element)
                if len(result) == 0 or len(result[0].contents) == 0:  # No results or empty results
                    print('Failed: spot_check(): ', page)
                    self.failed_pages.append(page.url)
        return


# Verifier subclasses

class ProjectDashboardVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 410
        self.page_elements = [
            '#nodeTitleEditable',  # Title
            '#contributors span.date.node-last-modified-date',  # Last modified
            '#contributorsList > ol',  # Contributor list
            '#nodeDescriptionEditable',  # Description
            '#tb-tbody',  # File list
            '#logScope > div > div > div.panel-body > span > dl'  # Activity
        ]
        self.harvest_pages(run_info['node_urls'], '', ProjectDashboardPage)
        self.size_comparison()
        self.spot_check()


class ProjectFilesVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 380
        self.page_elements = [
            '.fg-file-links',  # Links to files (names them)
        ]
        self.harvest_pages(run_info['node_urls'], 'files/', ProjectFilesPage)
        self.size_comparison()
        self.spot_check()


class ProjectWikiVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 410
        self.page_elements = [
            '#wikiViewRender',  # Links to files (names them)
            '#viewVersionSelect option',  # Current version date modified
            '.fg-file-links'  # Links to other pages (names them)
        ]
        self.harvest_pages(run_info['node_urls'], 'wiki/', ProjectWikiPage)
        self.size_comparison()
        self.spot_check()


class ProjectAnalyticsVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 380
        self.page_elements = [
            '#wikiViewRender',  # Links to files (names them)
            '#viewVersionSelect option:nth-child(2)',  # Current version date modified
            '.fg-file-links'  # Links to other pages (names them)
        ]
        self.harvest_pages(run_info['node_urls'], 'analytics/', ProjectAnalyticsPage)
        self.size_comparison()
        self.spot_check()


class ProjectRegistrationsVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 390
        self.page_elements = [
            'body > div.watermarked > div > div.row > div.col-xs-9.col-sm-8'  # List
        ]
        self.harvest_pages(run_info['node_urls'], 'registrations/', ProjectRegistrationsPage)
        self.size_comparison()
        self.spot_check()


class ProjectForksVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 380
        self.page_elements = [
            'body > div.watermarked > div > div.row > div.col-xs-9.col-sm-8'  # List
        ]
        self.harvest_pages(run_info['node_urls'], 'forks/', ProjectForksPage)
        self.size_comparison()
        self.spot_check()


class RegistrationDashboardVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 410
        self.page_elements = [
            '#nodeTitleEditable',  # Title
            '#contributors span.date.node-last-modified-date',  # Last modified
            '#contributorsList > ol',  # Contributor list
            '#nodeDescriptionEditable',  # Description
            '#tb-tbody',  # File list
            '#logScope > div > div > div.panel-body > span > dl'  # Activity
        ]
        self.harvest_pages(run_info['registration_urls'], '', RegistrationDashboardPage)
        self.size_comparison()
        self.spot_check()


class RegistrationFilesVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 380
        self.page_elements = [
            '.fg-file-links',  # Links to files (names them)
        ]
        self.harvest_pages(run_info['registration_urls'], 'files/', RegistrationFilesPage)
        self.size_comparison()
        self.spot_check()


class RegistrationWikiVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 410
        self.page_elements = [
            '#wikiViewRender',  # Links to files (names them)
            '#viewVersionSelect option:nth-child(2)',  # Current version date modified
            '.fg-file-links'  # Links to other pages (names them)
        ]
        self.harvest_pages(run_info['registration_urls'], 'wiki/', RegistrationWikiPage)
        self.size_comparison()
        self.spot_check()


class RegistrationAnalyticsVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 380
        self.page_elements = [
            '#wikiViewRender',  # Links to files (names them)
            '#viewVersionSelect option:nth-child(2)',  # Current version date modified
            '.fg-file-links'  # Links to other pages (names them)
        ]
        self.harvest_pages(run_info['registration_urls'], 'analytics/', RegistrationAnalyticsPage)
        self.size_comparison()
        self.spot_check()


class RegistrationForksVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 380
        self.page_elements = [
            'body > div.watermarked > div > div.row > div.col-xs-9.col-sm-8'  # List
        ]
        self.harvest_pages(run_info['registration_urls'], 'forks/', RegistrationForksPage)
        self.size_comparison()
        self.spot_check()


class UserProfileVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 80
        self.page_elements = [
            '#projects',
            '#projects li',  # Specific project list item
            'body div.panel-body',  # Component list
            'body h2'  # Activity points, project count
        ]
        self.harvest_pages(run_info['user_profile_page_urls'], '', UserProfilePage)
        self.size_comparison()
        self.spot_check()


class InstitutionDashboardVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.pages = []
        self.minimum_size = 350
        self.page_elements = [
            '#fileBrowser > div.db-infobar > div > div',  # Project preview
            '#tb-tbody'  # Project browser
        ]
        self.harvest_pages(run_info['institution_urls'], '', InstitutionProfilePage)
        self.size_comparison()
        self.spot_check()


def main():
    # for modularization and then concatenate lists
    rescrape_list = []
    for i in range(NUM_RETRIES):
        if run_info['scrape_nodes']:
            if run_info['include_files']:
                project_files = ProjectFilesVerifier()
                rescrape_list.append(project_files.failed_pages)
            if run_info['include_wiki']:
                project_wiki = ProjectWikiVerifier()
                rescrape_list.append(project_wiki.failed_pages)
            if run_info['include_analytics']:
                project_analytics = ProjectAnalyticsVerifier()
                rescrape_list.append(project_analytics.failed_pages)
            if run_info['include_registrations']:
                project_registrations = ProjectRegistrationsVerifier()
                rescrape_list.append(project_registrations.failed_pages)
            if run_info['include_forks']:
                project_forks = ProjectForksVerifier()
                rescrape_list.append(project_forks.failed_pages)
            if run_info['include_dashboard']:  # This must go last because its URLs don't have a specific ending.
                project_dashboards = ProjectDashboardVerifier()
                rescrape_list.append(project_dashboards.failed_pages)
        if run_info['scrape_registrations']:
            # Must run all page types automatically
            registration_files = RegistrationFilesVerifier()
            registration_wiki = RegistrationWikiVerifier()
            registration_analytics = RegistrationAnalyticsVerifier()
            registration_forks = RegistrationForksVerifier()
            registration_dashboards = RegistrationDashboardVerifier()
            rescrape_list.extend((registration_files.failed_pages, registration_wiki.failed_pages,
                                  registration_analytics.failed_pages, registration_forks.failed_pages,
                                  registration_dashboards.failed_pages))
        if run_info['scrape_users']:
            user_profiles = UserProfileVerifier()
            rescrape_list.append(user_profiles.failed_pages)
        if run_info['scrape_institutions']:
            institution_dashboards = InstitutionDashboardVerifier()
            rescrape_list.append(institution_dashboards.failed_pages)


if __name__ == "__main__": main()

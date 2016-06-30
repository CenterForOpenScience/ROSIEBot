import json, codecs
import os
import sys
from bs4 import BeautifulSoup
from settings import base_urls
from crawler import Crawler

# from rescraper import Rescraper

"""
Pages engineered to fail:

verify_page_exists: //2aqxv/files/index.html
size_comparison: //4cs6x/files/index.html should be 340 KB
no instance at all: //5ney2
no file div: 
empty file div:
wiki contains backup:

"""

# TODO: put this in settings
#NUM_RETRIES = 2
TASK_FILE = '201606291542.json'
MIRROR = 'archive/'

# with codecs.open(TASK_FILE, mode='r', encoding='utf-8') as file:
#     run_info = json.load(file)


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


# Verifier superclass

class Verifier:
    def __init__(self):
        self.pages = []
        self.minimum_size = 0
        self.page_elements = {}
        self.failed_pages = []

    # Populate self.pages with the relevant files
    def harvest_pages(self, json_filename, json_list, url_end, page_class):
        """
        :param json_list: The list in the json file of found URLs
        :param url_end: The json_list is non segregated by page type
        :param page_class: The subclass for the specific page type
        :return: Null, but self.pages is populated.
        """
        for url in json_list:
            if url_end in url:
                print('rel: ', url)
                if url in json_filename['error_list']:
                    self.failed_pages.append(url)
                    print('error: ', url)
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
            # print(page)
            # print(page.file_size)
            if not page.file_size > self.minimum_size:
                print('Failed: size_comparison(): ', page, ' has size: ', page.file_size)
                self.failed_pages.append(page.url)
        return

    # Second check
    # Check that specified elements are present and non-empty in each page
    # Check that specified elements or their alternates are present and non-empty in each page
    # Alternate: different elements appear if there isn't supposed to be content, so it has to check both
    # Format: Filled-in : Alternate
    def spot_check(self):
        for page in self.pages:
            soup = page.get_content()
            for element in self.page_elements:
                alt = self.page_elements[element]
                result = soup.select(element)
                # No results or empty results
                if (len(result) == 0 or len(result[0].contents) == 0) and alt != '':
                    print("Failed: first spot_check(): ", page, element, "Retrying with alt.")
                    result = soup.select(self.page_elements[element])

                    # Element's alternate has no or empty results
                    if len(result) == 0 or len(result[0].contents) == 0:
                        print("Failed: alternate spot_check(): ", page, alt)
                        self.failed_pages.append(page.url)

                elif len(result) == 0 or len(result[0].contents) == 0 and alt == '':
                    print('Failed: spot_check(): ', page, "No alt.")
                if len(result) == 0 or len(result[0].contents) == 0:  # No results or empty results
                    print('Failed: spot_check(): ', page)
                    self.failed_pages.append(page.url)
        return


# Verifier subclasses

class ProjectDashboardVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 410
        self.page_elements = {
            '#nodeTitleEditable': '',  # Title
            '#contributors span.date.node-last-modified-date': '',  # Last modified
            '#contributorsList > ol': '',  # Contributor list
            '#nodeDescriptionEditable': '',  # Description
            '#tb-tbody': '',  # File list
            '#logScope > div > div > div.panel-body > span > dl': ''  # Activity
        }
        # self.harvest_pages(run_info['node_urls'], '', ProjectDashboardPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self,json_filename, json_list):
        self.harvest_pages(json_filename, json_list, '', ProjectDashboardPage)
        self.size_comparison()
        self.spot_check()


class ProjectFilesVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 380
        self.page_elements = {
            '.fg-file-links': '',  # Links to files (names them)
        }
        # self.harvest_pages(run_info['node_urls'], 'files/', ProjectFilesPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, 'files/', ProjectFilesPage)
        self.size_comparison()
        self.spot_check()


class ProjectWikiVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 410
        self.page_elements = {
            'pre': '#wikiViewRender > p > em',  # Wiki content / `No wiki content`
            '#viewVersionSelect option': '',  # Current version date modified
            '.fg-file-links': ''  # Links to other pages (names them)
        }
        # self.harvest_pages(run_info['node_urls'], wiki/', ProjectWikiPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, 'wiki/', ProjectWikiPage)
        self.size_comparison()
        self.spot_check()


class ProjectAnalyticsVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 380
        self.page_elements = {
            '#adBlock': 'body > div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # Warning about AdBlock
            'iframe': 'body > div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # External frame for analytics
        }
        # self.harvest_pages(run_info['node_urls'], 'analytics/', ProjectAnalyticsPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, 'analytics/', ProjectAnalyticsPage)
        self.size_comparison()
        self.spot_check()


class ProjectRegistrationsVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 390
        self.page_elements = {
            '#renderNode': '#registrations > div > div > p'  # List of nodes
        }
        # self.harvest_pages(run_info['node_urls'], 'registrations/', ProjectRegistrationsPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, 'registrations/', ProjectRegistrationsPage)
        self.size_comparison()
        self.spot_check()


class ProjectForksVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 380
        self.page_elements = {
            '#renderNode': 'body > div.watermarked > div > div.row > div.col-xs-9.col-sm-8 > p'  # List
        }
        # self.harvest_pages(run_info['node_urls'], 'forks/', ProjectForksPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, 'forks/', ProjectForksPage)
        self.size_comparison()
        self.spot_check()


class RegistrationDashboardVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 410
        self.page_elements = {
            '#nodeTitleEditable': '',  # Title
            '#contributors span.date.node-last-modified-date': '',  # Last modified
            '#contributorsList > ol': '',  # Contributor list
            '#nodeDescriptionEditable': '',  # Description
            '#tb-tbody': '',  # File list
            '#logScope > div > div > div.panel-body > span > dl': ''  # Activity
        }
        # self.harvest_pages(run_info['registration_urls'], '', RegistrationDashboardPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, '', RegistrationDashboardPage)
        self.size_comparison()
        self.spot_check()


class RegistrationFilesVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 380
        self.page_elements = {
            '.fg-file-links': '',  # Links to files (names them)
        }
        # self.harvest_pages(run_info['registration_urls'], 'files/', RegistrationFilesPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, 'files/', RegistrationFilesPage)
        self.size_comparison()
        self.spot_check()


class RegistrationWikiVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 410
        self.page_elements = {
            'pre': '#wikiViewRender > p > em',  # Wiki content / `No wiki content`
            '#viewVersionSelect option': '',  # Current version date modified
            '.fg-file-links': ''  # Links to other pages (names them)
        }
        # self.harvest_pages(run_info['registration_urls'], 'wiki/', RegistrationWikiPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, 'wiki/', RegistrationWikiPage)
        self.size_comparison()
        self.spot_check()


class RegistrationAnalyticsVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 380
        self.page_elements = {
            '#adBlock': 'body > div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # Warning about AdBlock
            'iframe': 'body > div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # External frame for analytics
        }
        # self.harvest_pages(run_info['registration_urls'], 'analytics/', RegistrationAnalyticsPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, 'analytics/', RegistrationAnalyticsPage)
        self.size_comparison()
        self.spot_check()


class RegistrationForksVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 380
        self.page_elements = {
            '#renderNode': 'body > div.watermarked > div > div.row > div.col-xs-9.col-sm-8 > p'  # List
        }
        # self.harvest_pages(run_info['registration_urls'], 'forks/', RegistrationForksPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, 'forks/', RegistrationForksPage)
        self.size_comparison()
        self.spot_check()


class UserProfileVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 80
        self.page_elements = {
            '#projects': 'div.help-block > p',  # Project list / "You have no projects"
            'body div.panel-body': 'div.help-block > p',  # Component list / "You have no components"
            'body h2': ''  # Activity points, project count
        }
        # self.harvest_pages(run_info['user_profile_page_urls'], '', UserProfilePage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, '', UserProfilePage)
        self.size_comparison()
        self.spot_check()


class InstitutionDashboardVerifier(Verifier):
    def __init__(self):
        Verifier.__init__(self)
        self.minimum_size = 350
        self.page_elements = {
            '#fileBrowser > div.db-infobar > div > div': '#fileBrowser > div.db-infobar > div > div',  # Project preview
            '#tb-tbody': '#fileBrowser > div.db-main > div.db-non-load-template.m-md.p-md.osf-box'  # Project browser
        }
        # self.harvest_pages(run_info['institution_urls'], '', InstitutionDashboardPage)
        # self.size_comparison()
        # self.spot_check()

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list, '', InstitutionDashboardPage)
        self.size_comparison()
        self.spot_check()


# first verification and then scraping the failed pages
def initial_verification(json_file):
    with codecs.open(json_file, mode='r', encoding='utf-8') as failure_file:
        run_info = json.load(failure_file)
    with codecs.open(json_file, mode='r', encoding='utf-8') as failure_file:
        run_copy = json.load(failure_file)
    if run_info['scrape_finished']:
        if run_info['scrape_nodes']:
            nodes_list_verified = []
            if run_info['include_files']:
                project_files_verifier = ProjectFilesVerifier()
                project_files_verifier.run_verifier(run_info,run_info['node_urls'])
                project_files = project_files_verifier.failed_pages
                nodes_list_verified += project_files
            if run_info['include_wiki']:
                project_wiki_verifier = ProjectWikiVerifier()
                project_wiki_verifier.run_verifier(run_info, run_info['node_urls'])
                project_wiki = project_wiki_verifier.failed_pages
                nodes_list_verified += project_wiki
            if run_info['include_analytics']:
                project_analytics_verifier = ProjectAnalyticsVerifier()
                project_analytics_verifier.run_verifier(run_info, run_info['node_urls'])
                project_analytics = project_analytics_verifier.failed_pages
                nodes_list_verified += project_analytics
            if run_info['include_registrations']:
                project_registrations_verifier = ProjectRegistrationsVerifier()
                project_registrations_verifier.run_verifier(run_info, run_info['node_urls'])
                project_registrations = project_registrations_verifier.failed_pages
                nodes_list_verified += project_registrations
            if run_info['include_forks']:
                project_forks_verifier = ProjectForksVerifier()
                project_forks_verifier.run_verifier(run_info, run_info['node_urls'])
                project_forks = project_forks_verifier.failed_pages
                nodes_list_verified += project_forks
            if run_info['include_dashboard']:  # This must go last because its URLs don't have a specific ending.
                project_dashboards_verifier = ProjectDashboardVerifier()
                project_dashboards_verifier.run_verifier(run_info, run_info['node_urls'])
                project_dashboards = project_dashboards_verifier.failed_pages
                nodes_list_verified += project_dashboards
            run_copy['node_urls_verified'] = nodes_list_verified
        if run_info['scrape_registrations']:
            # Must run all page types automatically
            registration_files_verifier = RegistrationFilesVerifier()
            registration_files_verifier.run_verifier(run_info, run_info['registration_urls'])
            registration_files = registration_files_verifier.failed_pages

            registration_wiki_verifier = RegistrationWikiVerifier()
            registration_wiki_verifier.run_verifier(run_info, run_info['registration_urls'])
            registration_wiki = registration_wiki_verifier.failed_pages

            registration_analytics_verifier = RegistrationAnalyticsVerifier()
            registration_analytics_verifier.run_verifier(run_info, run_info['registration_urls'])
            registration_analytics = registration_analytics_verifier.failed_pages

            registration_forks_verifier = RegistrationForksVerifier()
            registration_forks_verifier.run_verifier(run_info, run_info['registration_urls'])
            registration_forks = registration_forks_verifier.failed_pages

            registration_dashboards_verifier = RegistrationDashboardVerifier()
            registration_dashboards_verifier.run_verifier(run_info, run_info['registration_urls'])
            registration_dashboards = registration_dashboards_verifier.failed_pages

            registrations_list_verified = registration_files + registration_wiki + registration_analytics + \
                registration_forks + registration_dashboards
            run_copy['registration_urls_verified'] = registrations_list_verified
        if run_info['scrape_users']:
            user_profiles_verifier = UserProfileVerifier()
            user_profiles_verifier.run_verifier(run_info, run_info['user_profile_page_urls'])
            user_profiles = user_profiles_verifier.failed_pages
            run_copy['user_profile_page_urls_verified'] = user_profiles
        if run_info['scrape_institutions']:
            institution_dashboards_verifier = InstitutionDashboardVerifier()
            institution_dashboards_verifier.run_verifier(run_info, run_info['institution_urls'])
            institution_dashboards = institution_dashboards_verifier.failed_pages
            run_copy['institution_urls_verified'] = institution_dashboards

        # truncates json and dumps new lists
        with codecs.open(TASK_FILE, mode='w', encoding='utf-8') as file:
            json.dump(run_copy, file, indent=4)

        # Rescraping

        second_chance = Crawler()

    if run_info['scrape_nodes']:
        second_chance.node_urls = run_copy['node_urls_verified']
        second_chance.scrape_nodes()
    if run_info['scrape_registrations']:
        second_chance.registration_urls = run_copy['registration_urls_verified']
    if run_info['scrape_users']:
        second_chance.user_profile_page_urls = run_copy['user_profile_page_urls_verified']
    if run_info['scrape_institutions']:
        second_chance.institution_urls = run_copy['institution_urls_verified']
    return run_copy


def subsequent_verifications(dict_file, num_retries):
    if dict_file['scrape_finished']:
        for i in range(num_retries):
            if dict_file['scrape_nodes']:
                nodes_list_verified = []
                if dict_file['include_files']:
                    project_files_verifier = ProjectFilesVerifier()
                    project_files_verifier.run_verifier(dict_file, dict_file['node_urls_verified'])
                    project_files = project_files_verifier.failed_pages
                    nodes_list_verified += project_files
                if dict_file['include_wiki']:
                    project_wiki_verifier = ProjectWikiVerifier()
                    project_wiki_verifier.run_verifier(dict_file, dict_file['node_urls_verified'])
                    project_wiki = project_wiki_verifier.failed_pages
                    nodes_list_verified += project_wiki
                if dict_file['include_analytics']:
                    project_analytics_verifier = ProjectAnalyticsVerifier()
                    project_analytics_verifier.run_verifier(dict_file, dict_file['node_urls_verified'])
                    project_analytics = project_analytics_verifier.failed_pages
                    nodes_list_verified += project_analytics
                if dict_file['include_registrations']:
                    project_registrations_verifier = ProjectRegistrationsVerifier()
                    project_registrations_verifier.run_verifier(dict_file, dict_file['node_urls_verified'])
                    project_registrations = project_registrations_verifier.failed_pages
                    nodes_list_verified += project_registrations
                if dict_file['include_forks']:
                    project_forks_verifier = ProjectForksVerifier()
                    project_forks_verifier.run_verifier(dict_file, dict_file['node_urls_verified'])
                    project_forks = project_forks_verifier.failed_pages
                    nodes_list_verified += project_forks
                if dict_file['include_dashboard']:  # This must go last because its URLs don't have a specific ending.
                    project_dashboards_verifier = ProjectDashboardVerifier()
                    project_dashboards_verifier.run_verifier(dict_file, dict_file['node_urls_verified'])
                    project_dashboards = project_dashboards_verifier.failed_pages
                    nodes_list_verified += project_dashboards
                dict_file['node_urls_verified'] = nodes_list_verified
            if dict_file['scrape_registrations']:
                # Must run all page types automatically
                registration_files_verifier = RegistrationFilesVerifier()
                registration_files_verifier.run_verifier(dict_file, dict_file['registration_urls_verified'])
                registration_files = registration_files_verifier.failed_pages

                registration_wiki_verifier = RegistrationWikiVerifier()
                registration_wiki_verifier.run_verifier(dict_file, dict_file['registration_urls_verified'])
                registration_wiki = registration_wiki_verifier.failed_pages

                registration_analytics_verifier = RegistrationAnalyticsVerifier()
                registration_analytics_verifier.run_verifier(dict_file, dict_file['registration_urls_verified'])
                registration_analytics = registration_analytics_verifier.failed_pages

                registration_forks_verifier = RegistrationForksVerifier()
                registration_forks_verifier.run_verifier(dict_file, dict_file['registration_urls_verified'])
                registration_forks = registration_forks_verifier.failed_pages

                registration_dashboards_verifier = RegistrationDashboardVerifier()
                registration_dashboards_verifier.run_verifier(dict_file, dict_file['registration_urls_verified'])
                registration_dashboards = registration_dashboards_verifier.failed_pages

                registrations_list_verified = registration_files + registration_wiki + registration_analytics + \
                    registration_forks + registration_dashboards
                dict_file['registration_urls_verified'] = registrations_list_verified
            if dict_file['scrape_users']:
                user_profiles_verifier = UserProfileVerifier()
                user_profiles_verifier.run_verifier(dict_file, dict_file['user_profile_page_urls_verified'])
                user_profiles = user_profiles_verifier.failed_pages
                dict_file['user_profile_page_urls_verified'] = user_profiles
            if dict_file['scrape_institutions']:
                institution_dashboards_verifier = InstitutionDashboardVerifier()
                institution_dashboards_verifier.run_verifier(dict_file, dict_file['institution_urls_verified'])
                institution_dashboards = institution_dashboards_verifier.failed_pages
                dict_file['institution_urls_verified'] = institution_dashboards

            # truncates json and dumps new lists
            with codecs.open(TASK_FILE, mode='w', encoding='utf-8') as file:
                json.dump(dict_file, file, indent=4)

            # Rescraping

            second_chance = Crawler()

            if dict_file['scrape_nodes']:
                second_chance.node_urls = dict_file['node_urls_verified']
                second_chance.scrape_nodes()
            if dict_file['scrape_registrations']:
                second_chance.registration_urls = dict_file['registration_urls_verified']
            if dict_file['scrape_users']:
                second_chance.user_profile_page_urls = dict_file['user_profile_page_urls_verified']
            if dict_file['scrape_institutions']:
                second_chance.institution_urls = dict_file['institution_urls_verified']


def main():
    # FOR TESTING
    json_filename = '201606291542.json'
    num_retries = 2
    # call two verification/scraping methods depending on num retries
    if num_retries > 1:
        run_file = initial_verification(json_filename)
        subsequent_verifications(run_file, num_retries)
    if num_retries == 1:
        initial_verification(json_filename)


if __name__ == "__main__": main()

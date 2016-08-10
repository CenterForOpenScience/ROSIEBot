import json
import codecs
from crawler import Crawler
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
        print(tail)
        path = MIRROR + tail
        return path

    def get_content(self):
        soup = BeautifulSoup(open(self.path), 'html.parser')
        return soup


# Verifier superclass
class Verifier:
    def __init__(self):
        """
        :param min_size: File size minimum for a page. Anything below this couldn't possibly be a complete file.
        :param pg_type: The class to instantiate page objects with.
        :param end: Indentifier in the URL, e.g. 'files/', 'end' is a misnomer ('wiki/' in the middle of a URL)
        """
        self.minimum_size = 8
        # self.page_type = pg_type
        # self.url_end = end

        self.pages = []  # All the page objects
        self.failed_pages = []

    # Populate self.pages with the relevant files
    def harvest_pages(self, json_dictionary, json_list, first_run):
        """
        :param json_dictionary: The dictionary created from the json file
        :param json_list: The list in the json file of found URLs
        :return: Null, but self.pages is populated.
        """
        if json_dictionary['error_list'] is not None:
            for url in json_list[:]:
                # if self.url_end in url:
                print('rel: ', url)
                if url in json_dictionary['error_list'] and first_run:
                    self.failed_pages.append(url)
                    print('error: ', url)
                else:
                    try:
                        obj = Page(url)
                        self.pages.append(obj)
                        print(obj.path)
                    except FileNotFoundError:
                        print("Failed harvest_pages ", url)
                        self.failed_pages.append(url)
                json_list.remove(url)

    # Compare page size to page-specific minimum that any fully-scraped page should have
    def size_comparison(self):
        for page in self.pages[:]:
            print("Size comparison on ", page)
            print(page.file_size)
            if not page.file_size > self.minimum_size:
                print('Failed: size_comparison(): ', page, ' has size: ', page.file_size)
                self.failed_pages.append(page.url)
                self.pages.remove(page)
        return

    def run_verifier(self, json_filename, json_list, first_run):
        self.harvest_pages(json_filename, json_list, first_run)
        self.size_comparison()


# Called when json file had scrape_nodes = true
# Checks for all the components of a project and if they were scraped
# Verifies them and returns a list of the failed pages
def verify_nodes(verification_dictionary, list_name, first_run):
    nodes_list_verified = []
    if verification_dictionary['include_files']:
        project_files_verifier = Verifier()
        project_files_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
        project_files = project_files_verifier.failed_pages
        nodes_list_verified += project_files
    if verification_dictionary['include_wiki']:
        project_wiki_verifier = Verifier()
        project_wiki_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
        project_wiki = project_wiki_verifier.failed_pages
        nodes_list_verified += project_wiki
    if verification_dictionary['include_analytics']:
        project_analytics_verifier = Verifier()
        project_analytics_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
        project_analytics = project_analytics_verifier.failed_pages
        nodes_list_verified += project_analytics
    if verification_dictionary['include_registrations']:
        project_registrations_verifier = Verifier()
        project_registrations_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
        project_registrations = project_registrations_verifier.failed_pages
        nodes_list_verified += project_registrations
    if verification_dictionary['include_forks']:
        project_forks_verifier = Verifier()
        project_forks_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
        project_forks = project_forks_verifier.failed_pages
        nodes_list_verified += project_forks
    if verification_dictionary['include_dashboard']:  # This must go last because its URLs don't have a specific ending.
        project_dashboards_verifier = Verifier()
        project_dashboards_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
        project_dashboards = project_dashboards_verifier.failed_pages
        nodes_list_verified += project_dashboards
    return nodes_list_verified


# Called when json file had scrape_registrations = true
# Verifies the components of a registration and returns a list of the failed pages
def verify_registrations(verification_dictionary, list_name, first_run):
    # Must run all page types automatically
    registration_files_verifier = Verifier()
    registration_files_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    registration_files = registration_files_verifier.failed_pages

    registration_wiki_verifier = Verifier()
    registration_wiki_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    registration_wiki = registration_wiki_verifier.failed_pages

    registration_analytics_verifier = Verifier()
    registration_analytics_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    registration_analytics = registration_analytics_verifier.failed_pages

    registration_forks_verifier = Verifier()
    registration_forks_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    registration_forks = registration_forks_verifier.failed_pages

    registration_dashboards_verifier = Verifier()
    registration_dashboards_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    registration_dashboards = registration_dashboards_verifier.failed_pages

    registrations_list_verified = registration_files + registration_wiki + registration_analytics + \
        registration_forks + registration_dashboards
    return registrations_list_verified


# Called when json file had scrape_users = true
# Verifies all user profile pages and returns a list of the failed pages
def verify_users(verification_dictionary, list_name, first_run):
    user_profiles_verifier = Verifier()
    user_profiles_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    user_profiles = user_profiles_verifier.failed_pages
    return user_profiles


# Called when json file had scrape_institutions = true
# Verifies all user profile pages and returns a list of the failed pages
def verify_institutions(verification_dictionary, list_name, first_run):
    institution_dashboards_verifier = Verifier()
    institution_dashboards_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    institution_dashboards = institution_dashboards_verifier.failed_pages
    return institution_dashboards


def call_rescrape(verification_json_dictionary):
    print("Called rescrape.")
    second_chance = Crawler()
    second_chance.scrape_pages(verification_json_dictionary['error_list'])


def setup_verification(json_dictionary, first_run):
    verification_list = []
    print("Check verification")
    if json_dictionary['scrape_nodes']:
        if first_run:
            list_name = 'node_urls'
        else:
            list_name = 'error_list'
        verification_list += verify_nodes(json_dictionary, list_name, first_run)
    if json_dictionary['scrape_registrations']:
        if first_run:
            list_name = 'registration_urls'
        else:
            list_name = 'error_list'
        verification_list += verify_registrations(json_dictionary, list_name, first_run)
    if json_dictionary['scrape_users']:
        if first_run:
            list_name = 'user_urls'
        else:
            list_name = 'error_list'
        verification_list += verify_users(json_dictionary, list_name, first_run)
    if json_dictionary['scrape_institutions']:
        if first_run:
            list_name = 'institution_urls'
        else:
            list_name = 'error_list'
        verification_list += verify_institutions(json_dictionary, list_name, first_run)

    return verification_list


def run_verification(json_file, i):
    with codecs.open(json_file, mode='r', encoding='utf-8') as failure_file:
        run_info = json.load(failure_file)
    with codecs.open(json_file, mode='r', encoding='utf-8') as failure_file:
        run_copy = json.load(failure_file)
    if i == 0:
        print("Begun 1st run")
        if run_info['scrape_finished']:
            run_copy['error_list'] = setup_verification(run_info, True)
            run_copy['1st_verification_finished'] = True
            with codecs.open(json_file, mode='w', encoding='utf-8') as file:
                json.dump(run_copy, file, indent=4)
                print("Dumped json run_copy 1st verify")
        call_rescrape(run_copy)
    else:
        print("Begun next run")
        run_copy['error_list'] = setup_verification(run_copy, False)
        # truncates json and dumps new lists
        with codecs.open(json_file, mode='w', encoding='utf-8') as file:
            json.dump(run_copy, file, indent=4)
        call_rescrape(run_copy)


def resume_verification(json_filename):
        with codecs.open(json_filename, mode='r', encoding='utf-8') as failure_file:
            run_copy = json.load(failure_file)
        print("Resumed verification.")
        run_copy['error_list'] = setup_verification(run_copy, False)
        # truncates json and dumps new lists
        with codecs.open(json_filename, mode='w', encoding='utf-8') as file:
            json.dump(run_copy, file, indent=4)
        call_rescrape(run_copy)


def main(json_filename, num_retries):
    # For testing:
    # num_retries = 2
    # call two verification/scraping methods depending on num retries
    run_verification(json_filename, num_retries)

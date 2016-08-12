import json
import codecs
from crawler import Crawler
from bs4 import BeautifulSoup
from settings import base_urls
import os

MIRROR = 'archive/'


# Superclass for page-specific page instances
class Page:
    """
        A Page class is designed to hold an instance of a page scraped.
        It's attributes are:
            url = the url of the page
            path = the file path of the page
    """

    def __init__(self, url):
        """
            Constructor for the Page class

            :param url: The url of the page
        """
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
        """
            Specifies the file path the page scraped is meant to have.

            :param url: The url of the page
        """
        # Remove http://domain
        tail = url.replace(base_urls[0], '') + 'index.html'
        path = MIRROR + tail
        return path

    def get_content(self):
        """
            Returns the content of the page scraped.
        """
        soup = BeautifulSoup(open(self.path), 'html.parser')
        return soup


# Verifier superclass
class Verifier:
    """
        A Verifier class for verification of the OSF Mirror.
        A CLI is designed to work with this verifier in order to ensure that everything that is scraped, is verified.
        Basic Workflow:
            1. Init
            2. All urls from json file run through harvest_pages. Failed pages get sent to rescrape.
            3. Remaining urls run through size_comparison. Failed pages get sent to rescrape.
            4. Rescrape failed urls.
            5. Verify the pages that were just rescraped.

        """

    def __init__(self):
        """
        Constructor for the Verifier class

            min_size: File size minimum for a page. Anything below this couldn't possibly be a complete file.
            pages: All the page objects
            failed_pages: Pages that failed verification and are being sent to rescrape.
        """
        self.minimum_size = 8
        self.pages = []  # All the page objects
        self.failed_pages = []

    # Populate self.pages with the relevant files
    def harvest_pages(self, json_dictionary, json_list, first_run):
        """
        On the first run of verification, puts all urls in error_list directly into failed_pages.
        Otherwise, tries to create page objects unless scraped file cannot be found in which case the url is added
        to failed pages.

        :param json_dictionary: The dictionary created from the json file
        :param json_list: The list in the json file of found URLs
        :param first_run: True if the first_run of verification has been completed. False, otherwise.
        """
        if json_dictionary['error_list'] is not None:
            for url in json_list[:]:
                # print('rel: ', url)
                if url in json_dictionary['error_list'] and first_run:
                    self.failed_pages.append(url)
                    # print('error: ', url)
                else:
                    try:
                        obj = Page(url)
                        self.pages.append(obj)
                    except FileNotFoundError:
                        # print("Failed harvest_pages ", url)
                        self.failed_pages.append(url)
                json_list.remove(url)

    # Compare page size to page-specific minimum that any fully-scraped page should have
    def size_comparison(self):
        """
            Checks the file size of every page instance against the minimum size specified in the constructor.
            Pages that fail get added to failed_pages to be sent to rescrape.
        """
        for page in self.pages[:]:
            if not page.file_size > self.minimum_size:
                # print('Failed: size_comparison(): ', page, ' has size: ', page.file_size)
                self.failed_pages.append(page.url)
                self.pages.remove(page)
        return

    def run_verifier(self, json_dictionary, json_list, first_run):
        """
            Runs the verifier.

            :param json_dictionary: The dictionary created from the json file
            :param json_list: The list in the json file of found URLs
            :param first_run: True if the first_run of verification has been completed. False, otherwise.
        """
        self.harvest_pages(json_dictionary, json_list, first_run)
        self.size_comparison()


# Called when json file had scrape_nodes = true
def verify_nodes(verification_dictionary, list_name, first_run):
    """
       Called when scrape_nodes = True

       :param verification_dictionary: The dictionary created from the json file.
       :param list_name: The list in the json file of found URLs.
       :param first_run: True if the first_run of verification has been completed. False, otherwise.
       :return: nodes_list_failed_verification: List of all the node urls that need to be rescraped.
    """
    projects_verifier = Verifier()
    projects_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    nodes_list_failed_verification = projects_verifier.failed_pages

    return nodes_list_failed_verification


# Called when json file had scrape_registrations = true
def verify_registrations(verification_dictionary, list_name, first_run):
    """
        Called when scrape_registrations = True

        :param verification_dictionary: The dictionary created from the json file.
        :param list_name: The list in the json file of found URLs.
        :param first_run: True if the first_run of verification has been completed. False, otherwise.
        :return: registrations_list_failed_verification: List of all the registration urls that need to be rescraped.
     """
    # Must run all page types automatically
    registrations_verifier = Verifier()
    registrations_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    registrations_list_failed_verification = registrations_verifier.failed_pages

    return registrations_list_failed_verification


# Called when json file had scrape_users = true
# Verifies all user profile pages and returns a list of the failed pages
def verify_users(verification_dictionary, list_name, first_run):
    """
        Called when scrape_users = True

        :param verification_dictionary: The dictionary created from the json file.
        :param list_name: The list in the json file of found URLs.
        :param first_run: True if the first_run of verification has been completed. False, otherwise.
        :return: user_profiles_failed_verification: List of all the user urls that need to be rescraped.
     """
    user_profiles_verifier = Verifier()
    user_profiles_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    user_profiles_failed_verification = user_profiles_verifier.failed_pages
    return user_profiles_failed_verification


# Called when json file had scrape_institutions = true
# Verifies all user profile pages and returns a list of the failed pages
def verify_institutions(verification_dictionary, list_name, first_run):
    """
        Called when scrape_institutions = True

        :param verification_dictionary: The dictionary created from the json file.
        :param list_name: The list in the json file of found URLs.
        :param first_run: True if the first_run of verification has been completed. False, otherwise.
        :return: institutions_dashboards_failed_verification: List of all the institution urls that need to be rescraped.
     """
    institution_dashboards_verifier = Verifier()
    institution_dashboards_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name], first_run)
    institution_dashboards_failed_verification = institution_dashboards_verifier.failed_pages
    return institution_dashboards_failed_verification


def call_rescrape(verification_dictionary):
    """
        Rescrapes all urls that failed verification
        Creates an instance of the crawler and calls scrape_pages on all urls dumped into 'error_list' in the json file

        :param verification_dictionary: The dictionary created from the json file.
     """
    print("Called rescrape.")
    second_chance = Crawler()
    second_chance.scrape_pages(verification_dictionary['error_list'])


def setup_verification(json_dictionary, first_run):
    """
        Specified which lists in the json task file need to be read from based on conditions specified in the json task
        file. Also, if its after the first run of verification all urls to be verified are read from error_list.

        :param json_dictionary: The dictionary created from the json file.
        :param first_run: True if the first_run of verification has been completed. False, otherwise.
        :return: failed_verification_list: List of all the urls that need to be rescraped.

     """
    failed_verification_list = []
    print("Check verification")
    if json_dictionary['scrape_nodes']:
        if first_run:
            list_name = 'node_urls'
        else:
            list_name = 'error_list'
        failed_verification_list += verify_nodes(json_dictionary, list_name, first_run)
    if json_dictionary['scrape_registrations']:
        if first_run:
            list_name = 'registration_urls'
        else:
            list_name = 'error_list'
        failed_verification_list += verify_registrations(json_dictionary, list_name, first_run)
    if json_dictionary['scrape_users']:
        if first_run:
            list_name = 'user_urls'
        else:
            list_name = 'error_list'
        failed_verification_list += verify_users(json_dictionary, list_name, first_run)
    if json_dictionary['scrape_institutions']:
        if first_run:
            list_name = 'institution_urls'
        else:
            list_name = 'error_list'
        failed_verification_list += verify_institutions(json_dictionary, list_name, first_run)

    return failed_verification_list


def run_verification(json_file, retry_number):
    """
        CLI Endpoint for a normal run of verification.
        Controls the main workflow of verification.
            Two copies of the json task file are opened. One to preserve the original lists of urls to be verified,
            and one to alter to dump all urls to be rescraped into.
            On the first run of verification, certain conditions in the json file are checked to determine what lists
            in the json file to read from based on what was scraped. An additional condition is added to the json file
            when the first run of verification is finished to specify that all subsequent runs of verification need only
            read from and dump to the list 'error_list'.

        :param json_file: Name of the json task file.
        :param retry_number: Number of what iteration of verification is being run.
     """
    with codecs.open(json_file, mode='r', encoding='utf-8') as failure_file:
        run_info = json.load(failure_file)
    with codecs.open(json_file, mode='r', encoding='utf-8') as failure_file:
        run_copy = json.load(failure_file)
    if retry_number == 0:
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


def resume_verification(json_file):
    """
        CLI Endpoint for resuming interrupted verification

        :param json_file: The dictionary created from the json file.
     """
        with codecs.open(json_file, mode='r', encoding='utf-8') as failure_file:
            run_copy = json.load(failure_file)
        print("Resumed verification.")
        run_copy['error_list'] = setup_verification(run_copy, False)
        # truncates json and dumps new lists
        with codecs.open(json_file, mode='w', encoding='utf-8') as file:
            json.dump(run_copy, file, indent=4)
        call_rescrape(run_copy)

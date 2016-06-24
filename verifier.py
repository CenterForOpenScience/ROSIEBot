import json, codecs
import os
import sys
from settings import base_urls
# from rescraper import Rescraper

# TODO: put this in settings
NUM_RETRIES = 2
TASK_FILE = '201606231548.json'
MIRROR = '127.0.0.1/'

# This is the bad guy list! It's not page-specific.
# Name of the game: put URLs on this list.
send_to_retry = []

with codecs.open(TASK_FILE, mode='r', encoding='utf-8') as file:
    run_info = json.load(file)


# Directly adds error_list from JSON to send_to_retry
def handle_errors():
    """ Test that send_to_retry length has increased by length of error_list. """
    for failed_url in run_info['error_list']:
        print("Failed: handle_errors() ", failed_url)
        send_to_retry.append(failed_url)
    return


# Superclass for page-specific classes
class Verifier:
    """
    Methods:
    1 Get all the URLS for a given page
    2 Create a dictionary of those URLS and their file paths
    3 Verify file exists at each path
    4 Size comparison (is the file big enough to in theory be cmoplete?)
    5 Spot check (are certain areas in the file, like title, present?)

     """
    def __init__(self):
        self.paths = {}
        self.json_list = []
        self.page = ''
        self.minimum_size = 0
        self.page_elements = {}

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
        return

    # Check that each file path in the dictionary actually exists
    def verify_files_exist(self):
        for path in self.paths:
            if not os.path.exists(path):
                print('Failed: verify_files_exist(): ', path)

        # 3. Verify each path exists
        # a. Send_to_retry
        # b. sort by page
        return

    def size_comparison(self):
        return

    def spot_check(self):
        return


# Asynchronously re-download all the files that were unacceptable/missing
def rescrape():
    # khepri = Rescraper()                                    # Khepri is the Egyptian god of rebirth
    # khepri.failed_urls = send_to_retry
    # khepri.scrape()
    # TODO: Recall verify
    pass


# Exectuion
if run_info['scrape_finished']:
    handle_errors()
    v = Verifier()
    v.page = 'files'
    v.json_list = run_info['node_urls']
    v.generate_page_dictionary()
    v.verify_files_exist()
    print(v.paths)


    for i in range(NUM_RETRIES):
        if run_info['scrape_nodes']:
            if run_info['include_dashboard']:
                pass
            if run_info['include_files']:
                pass
            if run_info['include_wiki']:
                pass
            if run_info['include_analytics']:
                pass
            if run_info['include_registrations']:
                pass
            if run_info['include_forks']:
                pass
            pass
        if run_info['scrape_registrations']:
            # Must run all page types automatically
            pass
        if run_info['scrape_users']:
            pass
        if run_info['scrape_institutions']:
            pass

        pass
    # 2.

    # Notes:
    #  - we need to identify which mirror we're looking at
import json, codecs
import os
import sys
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
        self.page_elements = []

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

    # First actual check
    # Check that each file path in the dictionary actually exists
    def verify_files_exist(self):
        for path in self.paths:
            print(path)
            if not os.path.exists(path):
                print('Failed: verify_files_exist(): ', path)
                send_to_retry.append(self.paths[path])              # Add to naughty list
                self.paths.pop(path)                                # Remove from nice list
        return

    # Second check
    # Compare page size to page-specific minimum that any fully-scraped page should have
    def size_comparison(self):
        for path in self.paths:
            file_size = os.path.getsize(path) / 1000                # in KB
            if not file_size > self.minimum_size:
                print('Failed: size_comparison(): ', path, ' has size: ', file_size)
                send_to_retry.append(self.paths[path])
                self.paths.pop(path)
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
    handle_errors()         # Always run
    v = Verifier()
    v.page = 'files'
    v.json_list = run_info['node_urls']
    v.minimum_size = 380
    v.generate_page_dictionary()
    v.verify_files_exist()
    v.size_comparison()
    print(v.paths)

    for i in range(NUM_RETRIES):
        if run_info['scrape_nodes']:
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
            if run_info['include_dashboard']:       # This must go last because its URLs don't have a specific ending.
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
import json, codecs
import os
import sys
from settings import base_urls

NUM_RETRIES = 2
TASK_FILE = '201606231548.json'

send_to_retry = {}

with codecs.open(TASK_FILE, mode='r', encoding='utf-8') as file:
    body = json.load(file)
    print(body)


def handle_504():
    # Add 504s to retry dictionary
    return


def get_path_from_url(url):
    # 1. Method that produces path from URL
    # a. URL .replace(http base, mirror path) + index.html
    return ''


def generate_page_dictionary(page):
    # 1. Take in URL list for each type
    # 2. Construct URL/path dictionary
    return {}


def verify_files_exist(path):
    # 3. Verify each path exists
    # a. Send_to_retry
    # b. sort by page
    return {}


#4 . Dictionary of page instances goes to size comparison
    #a. Send to retry
    #b. Add to dictionary to send to spot czech

#5. Dictionary of passing page instance goes to spot czech
    #a. Send to retry
    #b. Log success!


#1. Scrape
#2. Save
#3. Call verify steps 3 - end a set number of times


# 2.

# Notes:
#  - we need to identify which mirror we're looking at

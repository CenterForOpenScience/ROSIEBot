import shelve # (temp)
import os
import sys
# 1. Take in a list of pages at which to look.
# 2.

# Notes:
#  - we need to identify which mirror we're looking at

# A - Initialize lists from task file (or whatever it's going to be)
# B - Identify Problems
#   1 - Existence Check
#   2 - Size Comparison
#   3 - Spot Check
# C - Correct Problems (scrape all pages identified in B)
# D - Repeat


# temporary settings:
NUM_RETRIES = 2

with shelve.open('201606221420.task') as db:
    node_list = [x.split('//', 1)[1] for x in db['node_urls']]
    registration_list = db['registration_urls']
    user_list = db['user_profile_page_urls']
    institution_list = db['institution_urls']


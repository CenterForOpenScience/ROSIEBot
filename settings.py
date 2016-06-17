""" Configurations for a testing environment"""

# For development, API access is localhost:8000 by default and HTTP access is localhost:5000
# base_urls = ['http://127.0.0.1/', 'http://127.0.0.1:8000/v2/']
# base_urls = ['https://staging.osf.io/', 'https://staging-api.osf.io/v2/']
base_urls = ['https://osf.io/', 'https://api.osf.io/v2/']

# Limit number of API pages to go through
# limit = 1
# limit = 0

# Configure print statements
# verbose = True
# verbose = False

DEBUG_LOG_FILENAME = "debug_log.txt"
ERROR_LOG_FILENAME = "error_log.txt"
# GOAL_LOG_FILENAME = "goal_log.txt"
# SCRAPED_LOG_FILENAME = "scraped_log.txt"
MILESTONE_LOG_FILENAME = "milestone_log.txt"

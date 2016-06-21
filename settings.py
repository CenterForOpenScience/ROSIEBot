""" Configurations for a testing environment"""

# For development, API access is localhost:8000 by default and HTTP access is localhost:5000
base_urls = ['http://127.0.0.1:70/', 'http://127.0.0.1:8000/v2/']
# base_urls = ['https://staging.osf.io/', 'https://staging-api.osf.io/v2/']
# base_urls = ['https://osf.io/', 'https://api.osf.io/v2/']

# Limit number of API pages to go through
# Should be commented out for production
limit = 1

# Configure print statements
# verbose = True
# verbose = False

DEBUG_LOG_FILENAME = "debug_log.txt"
ERROR_LOG_FILENAME = "error_log.txt"


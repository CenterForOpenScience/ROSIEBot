"""
Step 4: Try again for failed pages.
"""
from Verification.spot_check import send_to_retry as new_tasks
from Verification.initialize_list import mirror_path
from settings import base_urls
import requests

http_base = base_urls[0]

# # Number of times to retry download before giving up.
tries = 3

retry_success_log = open('Logs/retry_success.log', 'a')
retry_failure_log = open('Logs/retry_failure.log', 'a')

for task in new_tasks:
    tail = task.replace(mirror_path, '')
    url = http_base + tail
    #TODO: redownload

retry_success_log.close(), retry_failure_log.close()

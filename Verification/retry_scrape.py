"""
Step 4: Try again for failed pages.
"""
import datetime
import Verification.spot_check as spot_check
import Verification.initialize_list as initialize
import settings
import requests

http_base = settings.base_urls[0]

mirror_path = initialize.mirror_path

new_tasks = spot_check.send_to_retry

# # Number of times to retry download before giving up.
tries = 3

retry_success_log = open('Logs/retry_success.log', 'a')
retry_failure_log = open('Logs/retry_failure.log', 'a')

for task in new_tasks:
    tail = task.replace(mirror_path, '')
    url = http_base + tail
    #TODO: redownload

retry_success_log.close(), retry_failure_log.close()

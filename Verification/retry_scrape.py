"""
Step 4: Try again for failed pages.
"""
import datetime

# Number of times to retry download before giving up.
tries = 3

success_log = open('Logs/retry_success.log', 'a')
failure_log = open('Logs/retry_failure.log', 'a')


retry_log.close()
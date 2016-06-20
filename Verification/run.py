#
# # Run through to rescraping, or partially to only document issues.
#

import datetime
print(datetime.datetime.now())

success_log = open('Logs/test_success.log', 'a')
failure_log = open('Logs/test_failure.log', 'a')
retry_success_log = open('Logs/retry_success.log', 'a')
retry_failure_log = open('Logs/retry_failure.log', 'a')

logs = [success_log, failure_log, retry_success_log, retry_failure_log]
for log in logs:
    log.write('\n' + str(datetime.datetime.now()) + '\n')
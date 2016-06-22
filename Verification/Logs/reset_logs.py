import sys
absolute = sys.path[0]

test_header = 'PROCESS_NAME\tTYPE\tINSTANCE\tSPOT\tSTATUS\n'

test_logs = [absolute+'/Verification/Logs/test_success.log', absolute+'/Verification/Logs/test_failure.log']

for log in test_logs:
    file = open(log, 'w')
    file.write(test_header)
    file.close()
    print(log, 'cleared.')

retry_header = 'FILE\t\tRETRY\tDATE\n'

retry_logs = [absolute+'/Verification/Logs/retry_success.log', absolute+'/Verification/Logs/retry_failure.log']

for log in retry_logs:
    file = open(log, 'w')
    file.write(retry_header)
    file.close()
    print(log, 'cleared.')

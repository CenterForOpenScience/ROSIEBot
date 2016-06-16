test_header = 'PROCESS_NAME\tTYPE\tINSTANCE\tSPOT\tSTATUS\n'

logs = ['success.log', 'failure.log']

for log in logs:
    file = open(log, 'w')
    file.write(test_header)
    file.close()
    print(log, 'cleared.')

retry_header = 'FILE\t\tRETRY\tDATE\n'
retry = open('retry.log', 'w')
retry.write(retry_header)
retry.close()
print('retry.log cleared.')

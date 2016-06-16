header = 'PROCESS_NAME\tTYPE\tINSTANCE\tSPOT\tSTATUS\n'

logs = ['success.log', 'failure.log']

for log in logs:
    file = open(log, 'w')
    file.write(header)
    file.close()
    print(log, 'cleared.')
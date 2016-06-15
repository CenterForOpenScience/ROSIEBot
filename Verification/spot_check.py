"""
Step 2: Check important elements on each page to ensure they aren't empty.
"""
from bs4 import BeautifulSoup
import os, sys
import Verification.size_comparison as size_comp

# CONSTRUCTION DETOUR - get_files is in size_comparison bc it will be the first step eventually.
# Let's pretend it's in here.
get_files = size_comp.get_files

success_log = open('Logs/success.log', 'a')
failure_log = open('Logs/failure.log', 'a')


class ElementValueIdentifier:
    def __init__(self):
        self.elements = []
        self.files = []

    def identify_values(self):
        for file in self.files:
            print(file)
            name = file.split('/')[-3] + '\t' + file.split('/')[-2]
            content = BeautifulSoup(open(file), 'html.parser')
            print(content)
            for element in self.elements:
                result = content.find_all(element)
                print(result)
                # if result == '':
                #     message = ['SPOT_CHECK', name, element, 'EMPTY.', '\n']
                #     failure_log.write('\t'.join(message))
                # else:
                #     message = ['SPOT_CHECK', name, element, 'found.', result, '\n']
                #     success_log.write('\t'.join(message))
    print('Spot checked.')


class ProjectDashboard(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '#nodeTitleEditable',                           # Title
            '#contributors',                                # Contributors, description, dates modified and created
            '#markdownRender',                              # Wiki list
            '#tb-tbody',                                    # File list
            '.list-group m-md sortable ui-sortable',        # Component list
            '.logs'                                         # Log
        ]
        self.files = get_files('project/')

dashboard = ProjectDashboard()
dashboard.identify_values()

success_log.close()
failure_log.close()
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


# Introduces relevant spot checking functions.
class ElementValueIdentifier:
    """
    self.elements is for HTML IDs of things to look for (not classes)
    self.files is the list of absolute paths to relevant pages.
    """
    def __init__(self):
        self.elements = []
        self.files = []

    def identify_values(self):
        for file in self.files:
            print(file)
            name = file.split('/')[-3] + '\t' + file.split('/')[-2]
            soup = BeautifulSoup(open(file), 'html.parser')
            for element in self.elements:
                result = soup.find(id=element)
                if result is None:
                        message = ['SPOT_CHECK', name, element, 'NOT FOUND', '\n']
                        failure_log.write('\t'.join(message))
                elif len(result.contents) == 0:
                    message = ['SPOT_CHECK', name, element, 'EMPTY', '\n']
                    failure_log.write('\t'.join(message))
                else:
                    message = ['SPOT_CHECK', name, element, 'OK', '\n']
                    success_log.write('\t'.join(message))
        print('Spot checked.')


class ProjectDashboard(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [                                  # IDs ONLY
            'projectSubnav',                               # Navbar
            'nodeTitleEditable',                           # Title
            'contributors',                                # Contributors, description, dates modified and created
            'contributorsList',                            # Contributor list
            'tb-tbody',                                    # File list
        ]
        self.files = get_files('project/')

dashboard = ProjectDashboard()
dashboard.identify_values()

success_log.close()
failure_log.close()
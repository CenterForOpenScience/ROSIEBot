"""
Step 2: Check important elements on each page to ensure they aren't empty.

Types of pages:

- Dashboard (project and registration)
- Files (project and registration)
- Wiki (project and registration)
- Analytics (project and registration)
- Forks (project and registration)
- Registrations

- Profile (user and institution)

"""
from bs4 import BeautifulSoup
import os, sys
import Verification.size_comparison as size_comp

# CONSTRUCTION DETOUR - get_files is in size_comparison bc it will be the first step eventually.
# Let's pretend it's in here.
get_files = size_comp.get_files

success_log = open('Logs/success.log', 'a')
failure_log = open('Logs/failure.log', 'a')


# Parent class - Introduces relevant spot checking functions.
class ElementValueIdentifier:
    """
    self.elements is for HTML IDs of things to look for (not classes)
    self.files is the list of absolute paths to relevant pages.
    """
    def __init__(self):
        self.elements = []
        self.files = []
        self.type = ''

    def identify_values(self):
        for file in self.files:
            print(file)
            name = file.split('/')[-3] + '\t' + file.split('/')[-2]
            soup = BeautifulSoup(open(file), 'html.parser')
            for element in self.elements:
                result = soup.select(element)
                if len(result) == 0:                    # No results
                    message = ['SPOT_CHECK', name, element, 'NOT FOUND', '\n']
                    failure_log.write('\t'.join(message))
                elif len(result[0].contents) == 0:      # Empty results
                    message = ['SPOT_CHECK', name, element, 'EMPTY', '\n']
                    failure_log.write('\t'.join(message))
                else:
                    message = ['SPOT_CHECK', name, element, 'OK', '\n']
                    success_log.write('\t'.join(message))
        print('Spot checked.')
        success_log.write('\n'), failure_log.write('\n')


class ProjectDashboard(ElementValueIdentifier):
    def __init__(self, osf_type):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '#nodeTitleEditable',                                # Title
            '#contributors span.date.node-last-modified-date',   # Last modified
            '#contributorsList > ol',                            # Contributor list
            '#tb-tbody',                                         # File list
            '#logScope > div > div > div.panel-body > span > dl' # Activity
        ]
        self.type = osf_type
        self.type = osf_type
        self.files = get_files(self.type)
        self.identify_values()


class ProjectFiles(ElementValueIdentifier):
    def __init__(self, osf_type):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '.fg-file-links',                                # Links to files (names them)
        ]
        self.type = osf_type
        self.files = get_files(self.type, 'files/')
        self.identify_values()


class ProjectWiki(ElementValueIdentifier):
    def __init__(self, osf_type):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '#wikiViewRender',                              # Links to files (names them)
            '#viewVersionSelect option:nth-child(2)',       # Current version date modified
            '.fg-file-links'                                # Links to other pages (names them)
        ]
        self.type = osf_type
        self.files = get_files(self.type, 'wiki/')
        self.identify_values()


# class ProjectAnalytics(ElementValueIdentifier):
    # def __init__(self):
    #     ElementValueIdentifier.__init__(self)
    #     self.elements = [
    #         '#wikiViewRender',                              # Links to files (names them)
    #         '#viewVersionSelect option:nth-child(2)',       # Current version date modified
    #         '.fg-file-links'                                # Links to other pages (names them)
    #     ]
    #       self.type = osf_type
    # self.files = get_files(self.type, 'analytics')
    #     self.identify_values()
    # self.type = osf_type


class ProjectForks(ElementValueIdentifier):
    def __init__(self, osf_type):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            'body > div.watermarked > div > div.row > div.col-xs-9.col-sm-8' # List
        ]
        self.type = osf_type
        self.files = get_files(self.type, 'forks/')
        self.identify_values()


class ProjectRegistrations(ElementValueIdentifier):
    def __init__(self, osf_type):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            'body > div.watermarked > div > div.row > div.col-xs-9.col-sm-8' # List
        ]
        self.type = osf_type
        self.files = get_files(self.type, 'forks/')
        self.identify_values()

dashboard = ProjectDashboard('project/')

success_log.close()
failure_log.close()
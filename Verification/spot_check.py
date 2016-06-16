"""
Step 2: Check important elements on each page to ensure they aren't empty.

Classes organized by type ('projects', 'users', etc.)
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

# Project verification classes


class ProjectDashboard(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '#nodeTitleEditable',                                # Title
            '#contributors span.date.node-last-modified-date',   # Last modified
            '#contributorsList > ol',                            # Contributor list
            '#nodeDescriptionEditable',                          # Description
            '#tb-tbody',                                         # File list
            '#logScope > div > div > div.panel-body > span > dl' # Activity
        ]
        self.files = get_files('project/')
        self.identify_values()


class ProjectFiles(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '.fg-file-links',                                # Links to files (names them)
        ]
        self.files = get_files('project/', 'files/')
        self.identify_values()


class ProjectWiki(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '#wikiViewRender',                              # Links to files (names them)
            '#viewVersionSelect option:nth-child(2)',       # Current version date modified
            '.fg-file-links'                                # Links to other pages (names them)
        ]
        self.files = get_files('project/', 'wiki/')
        self.identify_values()


# class ProjectAnalytics(ElementValueIdentifier):
    # def __init__(self):
    #     ElementValueIdentifier.__init__(self)
    #     self.elements = [
    #         '#wikiViewRender',                              # Links to files (names them)
    #         '#viewVersionSelect option:nth-child(2)',       # Current version date modified
    #         '.fg-file-links'                                # Links to other pages (names them)
    #     ]
    #       'project/' = osf_type
    # self.files = get_files('project/', 'analytics')
    #     self.identify_values()


class ProjectForks(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            'body > div.watermarked > div > div.row > div.col-xs-9.col-sm-8' # List
        ]
        self.files = get_files('project/', 'forks/')
        self.identify_values()


class ProjectRegistrations(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            'body > div.watermarked > div > div.row > div.col-xs-9.col-sm-8' # List
        ]
        self.files = get_files('project/', 'forks/')
        self.identify_values()


# Registration verification classes


class RegistrationDashboard(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '#nodeTitleEditable',                                # Title
            '#contributors span.date.node-last-modified-date',   # Last modified
            '#contributorsList > ol',                            # Contributor list
            '#nodeDescriptionEditable',                          # Description
            '#tb-tbody',                                         # File list
            '#logScope > div > div > div.panel-body > span > dl' # Activity
        ]
        self.files = get_files('')
        self.identify_values()


class RegistrationFiles(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '.fg-file-links',                                # Links to files (names them)
        ]
        self.files = get_files('', 'files/')
        self.identify_values()


class RegistrationWiki(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '#wikiViewRender',                              # Links to files (names them)
            '#viewVersionSelect option:nth-child(2)',       # Current version date modified
            '.fg-file-links'                                # Links to other pages (names them)
        ]
        self.files = get_files('', 'wiki/')
        self.identify_values()


# class RegistrationAnalytics(ElementValueIdentifier):
    # def __init__(self):
    #     ElementValueIdentifier.__init__(self)
    #     self.elements = [
    #         '#wikiViewRender',                              # Links to files (names them)
    #         '#viewVersionSelect option:nth-child(2)',       # Current version date modified
    #         '.fg-file-links'                                # Links to other pages (names them)
    #     ]
    # self.files = get_files('', 'analytics')
    #     self.identify_values()


class RegistrationForks(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            'body > div.watermarked > div > div.row > div.col-xs-9.col-sm-8' # List
        ]
        self.files = get_files('', 'registrations/')
        self.identify_values()

# User Verification Class


class UserProfile(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '#projects',
            '#projects li',                              # Specific project list item
            'body div.panel-body',                       # Component list
            'body h2'                                    # Activity points, project count
        ]
        self.files = get_files('profile/')
        self.identify_values()

# Institution Verification Class


class InstitutionProfile(ElementValueIdentifier):
    def __init__(self):
        ElementValueIdentifier.__init__(self)
        self.elements = [
            '#fileBrowser > div.db-infobar > div > div',  # Project preview
            '#tb-tbody'                                   # Project browser
        ]
        self.files = get_files('institutions/')
        self.identify_values()

# # Project Execution
project_dashboard = ProjectDashboard()
project_files = ProjectFiles()
project_wiki = ProjectWiki()
# project_analytics = ProjectAnalytics()
project_registrations = ProjectRegistrations()
project_forks = ProjectForks()

# Registration Execution
registration_dashboard = RegistrationDashboard()
registration_files = RegistrationFiles()
registration_wiki = RegistrationWiki()
# registration_analytics = RegistrationAnalytics()
registration_forks = RegistrationForks()

# User and institution execution
user_profile = UserProfile()
institution_profile = InstitutionProfile()

success_log.close()
failure_log.close()
"""
Step 2: Check important elements on each page to ensure they aren't empty.
"""
from bs4 import BeautifulSoup
import os, sys
import Verification.size_comparison as size_comp

# CONSTRUCTION DETOUR


class ElementValueIdentifier:
    def __init__(self):
        self.elements = []
        self.files = []

    def identify_values(self):
        for file in self.files:
            content = BeautifulSoup(file, 'html.parser')
            for element in self.elements:
                result = content.find_all(element)
                if result == '':
                    print(file, element, ' not found.')
                else:
                    print(file, element, ' FOUND.')


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
import glob
import json
import os

from tqdm import tqdm
from bs4 import BeautifulSoup


class Indexer:
    """
    Utility class to index OSF pages.
    Specifically, the project dashboard page, the registration dashboard page, and the user profile page.
    This utility class could be deprecated if SHARE harvesters can be used to index the OSF.
    """

    def __init__(self):
        """
        Constructor of the Indexer class.
            self.index ==> the index object
            self.project_path_list ==> the list of all .html file in the root folder of each project
            self.profile_path_list ==> the list of all .html file in the root folder of each profile
            self.registration_path_list ==> the list of all .html file in the root folder of each registration
        """
        self.index = {}
        self.project_path_list = glob.glob("archive/project/*/*.html")
        self.profile_path_list = glob.glob("archive/profile/*/*.html")
        self.registration_path_list = glob.glob("archive/registration/*/*.html")

    def index_projects(self):
        """
        Method for indexing the project dashboard pages.
        :return:
        """
        for element in tqdm(self.project_path_list):
            page = BeautifulSoup(open(element), "html.parser")
            page_url = element.replace("archive/project", "")
            page_id = page_url.strip("/")
            title = page.find("title").text
            content = ' '.join(page.find(id="projectScope").text.split())
            entry = {}
            entry['title'] = title
            entry['description'] = content
            entry['url'] = page_url
            self.index[page_id] = entry

    def index_registrations(self):
        """
        Method for indexing the registration dashboard pages.
        :return:
        """
        for element in tqdm(self.registration_path_list):
            page = BeautifulSoup(open(element), "html.parser")
            page_url = element.replace("archive/registration", "")
            print(page_url)
            title = page.find("title").text
            content = ' '.join(page.find(id="projectScope").text.split())

            entry = {}
            entry['title'] = title
            entry['description'] = content
            entry['url'] = page_url
            self.index[page_url] = entry

    def index_profiles(self):
        """
        Method for indexing the user profile pages.
        :return:
        """
        for element in tqdm(self.profile_path_list):
            page = BeautifulSoup(open(element), "html.parser")
            page_url = element.replace("archive/profile", "")
            title = page.find("title").text
            description = (' '.join(page.find(id="social").text.split()) + ' ' +
                          ' '.join(page.find(id="jobs").text.split()) + ' ' +
                          ' '.join(page.find(id="schools").text.split()))\
                          .replace("Not provided ", "").replace("Not provided", "")
            entry = {
                'url': page_url,
                'title': title
            }
            if description:
                entry['description'] = description

            self.index[page_url] = entry

import glob
import json
from tqdm import tqdm
from bs4 import BeautifulSoup


class Indexer:

    def __init__(self):
        self.index = {}
        self.project_path_list = glob.glob("archive/project/*/*.html")
        self.profile_path_list = glob.glob("archive/profile/*/*.html")
        self.registration_path_list = glob.glob("archive/registration/*/*.html")

    def index_projects(self):
        for element in tqdm(self.project_path_list):
            page = BeautifulSoup(open(element), "html.parser")
            page_url = page.find("meta", {"name":"prerender-url"})["content"]
            page_id = page_url.strip("/")
            title = page.find("title").text
            content = ' '.join(page.find(id="projectScope").text.split())
            entry = {}
            entry['title'] = title
            entry['description'] = content
            entry['url'] = page_url
            self.index[page_id] = entry

    def index_registration(self):
        for element in tqdm(self.registration_path_list):
            page = BeautifulSoup(open(element), "html.parser")
            page_url = page.find("meta", {"name": "prerender-url"})["content"]
            page_id = page_url.strip("/")
            title = page.find("title").text
            content = ' '.join(page.find(id="projectScope").text.split())
            entry = {}
            entry['title'] = title
            entry['description'] = content
            entry['url'] = page_url
            self.index[page_id] = entry

    def index_profile(self):
        for element in tqdm(self.profile_path_list):
            page = BeautifulSoup(open(element), "html.parser")
            try:
                page_url = page.find("meta", {"name": "prerender-url"})["content"]
                page_id = page_url.strip("/")
                title = page.find("title").text
                entry = {}
                entry['title'] = title
                entry['description'] = ' '.join(page.find(id="social").text.split()) + ' ' + ' '.join(page.find(id="jobs").text.split()) + ' ' + ' '.join(page.find(id="schools").text.split())
                entry['url'] = page_url
                self.index[page_id] = entry
            except:
                pass

indexer = Indexer()
indexer.index_projects()
indexer.index_registration()
indexer.index_profile()
json.dump(indexer.index, open('index.json', 'w+'))

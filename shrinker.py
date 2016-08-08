import json, codecs
from bs4 import BeautifulSoup
import tqdm


class Shrinker:
    """
    Shrinker visits every file in the JSON taskfile and removes any <style> tag
    and inserts one link to static/css/consolidated.css

    update_css.py generates this consolidated file.
    """
    def __init__(self, tf):
        with codecs.open(tf, mode='r', encoding='utf-8') as file:
            self.run_info = json.load(file)

    #  Go through each section of the taskfile, generate file paths, and replace the CSS in each file
    def run(self):
        if self.run_info['scrape_nodes']:
            print("Downsizing nodes")
            self.nodes = ['archive/' + '/'.join(url.split('/')[3:]) + 'index.html' for url in self.run_info['node_urls']]
            for node in tqdm.tqdm(self.nodes):
                self._replace_css(node)
        if self.run_info['scrape_registrations']:
            print("Downsizing registrations")
            self.registrations = ['archive/' + '/'.join(url.split('/')[3:]) + 'index.html' for url in self.run_info['registration_urls']]
            for registration in tqdm.tqdm(self.registrations):
                self._replace_css(registration)
        if self.run_info['scrape_users']:
            print("Downsizing users")
            self.users = ['archive/' + '/'.join(url.split('/')[3:]) + 'index.html' for url in self.run_info['user_urls']]
            for user in tqdm.tqdm(self.users):
                self._replace_css(user)
        if self.run_info['scrape_institutions']:
            print("Downsizing institutions")
            self.institutions = ['archive/' + '/'.join(url.split('/')[3:]) + 'index.html' for url in self.run_info['institution_urls']]
            for institution in tqdm.tqdm(self.institutions):
                self._replace_css(institution)

    # Create a BS4 object of a file, remove any <style> results, and insert <link rel=stylesheet>
    def _replace_css(self, path):
        try:
            file = open(path, "r+")
            soup = BeautifulSoup(file, 'html.parser')
            for elem in soup.findAll('style'):
                elem.extract()
            link_tag = soup.new_tag("link", href="/static/consolidated.css", rel="stylesheet")
            if soup.head is not None:
                soup.head.insert(0, link_tag)
            # soup = soup.prettify()
            file.seek(0)
            file.write(str(soup))
            file.truncate()
            file.close()
        except FileNotFoundError:
            return

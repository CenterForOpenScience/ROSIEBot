import requests
import crawler
import settings
import os
import sys

base_urls = settings.base_urls

rosie = crawler.Crawler()
itinerary = rosie.crawl(limit=10)

class Scraper():
    '''
    Scrapers save render and save page content in proper directory organization.
    '''
    def __init__(self):
        self.headers = {
            'User-Agent': 'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
            # 'User-Agent' : 'ROSIEBot/1.0 (+http://github.com/zamattiac/ROSIEBot)'
        }
        self.http_base = base_urls[0]

    def write_HTML(self, page):
        with requests.Session() as s:
            print(self.http_base+page)
            r = requests.get(self.http_base + page, headers=self.headers)
            print(r.status_code)
        if r.status_code == 200:
            html = r.text.replace('This site is running in development mode.', 'This is a read-only mirror of the OSF.')
            f = open('index.html', 'w')
            f.write(html)

    def directory_nest(self, pages):
        for page in pages:
            os.chdir('website')
            page = page.strip('/')
            tree = page.split('/')
            path = ''
            for folder in tree:
                path += folder + '/'
                if folder == '':
                    self.write_HTML('')
                    break
                try:
                    os.chdir(folder)
                except:
                    os.mkdir(folder)
                    os.chdir(folder)
                    self.write_HTML(path)
            #cd home
            os.chdir(sys.path[0])
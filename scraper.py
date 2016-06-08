import requests
import crawler
import settings
import os
import sys
import datetime

base_urls = settings.base_urls
verbose = settings.verbose

start = datetime.datetime.now()
print("Started: ", start)

rosie = crawler.Crawler()
chore_list = rosie.crawl()

if verbose: print(chore_list)

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
        if not os.path.isdir('website'):
            os.mkdir('website')

    def write_HTML(self, page):
        with requests.Session() as s:
            if verbose: print(self.http_base+page)
            s.headers.update(self.headers)
            r = s.get(self.http_base + page)
            if verbose: print(r.status_code)
        if r.status_code == 200:
            html = r.text.replace('This site is running in development mode.', 'This is a read-only mirror of the OSF.')
            f = open('index.html', 'w')
            f.write(html)
            f.close()

    def directory_nest(self, pages):
        for page in pages:
            if verbose: print(page)
            os.chdir('website')
            page = page.strip('/')
            tree = page.split('/')
            if verbose: print(tree)
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
            # cd home
            os.chdir(sys.path[0])

rosies_vaccuum = Scraper()
rosies_vaccuum.directory_nest(chore_list)

stop = datetime.datetime.now()
elapsed = stop - start
print("Time elapsed: ", elapsed)
print(len(chore_list), 'pages visited.')
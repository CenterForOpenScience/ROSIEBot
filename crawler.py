import requests
from bs4 import BeautifulSoup
import datetime
import sys

#TODO: Command line interface
#TODO: Change user agent to RosieBot
#TODO: Documentation
#TODO: AJAX
#TODO: Directories

class Crawler:
    def __init__(self, base_url):
        self.open_links = []
        self.closed_links = []
        self.url_list = []
        self.headers = {
            # 'User-Agent' : 'ROSIEBot'
            'User-Agent': 'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)'
        }
        self.base_url = base_url

    def crawl_api(self, limit=0):
        with requests.Session() as s:
            split_url = self.base_url.split("//")
            print(split_url)
            cur_url = split_url[0] + "//api." + split_url[1] + "/v2/nodes/"  # page included for debugging
            ctr = 1
            nodelist = []
            while True:
                current_page = s.get(cur_url)
                print('page -> ' + cur_url)
                parsed_json = current_page.json()
                for x in range(0, len(parsed_json['data'])):
                    print(parsed_json['data'][x]['attributes']['public'])
                    if parsed_json['data'][x]['attributes']['public']:
                        nodelist.append(parsed_json['data'][x]['id'])
                if parsed_json['links']['next'] == parsed_json['links']['last']:
                    print("end of nodes on OSF!")
                    break
                cur_url = parsed_json['links']['next']
                if limit == ctr:
                    break
                ctr += 1
            print(nodelist)
            return nodelist

    def crawl_from_root(self, url):
        self.open_links.append(url)
        with requests.Session() as s:
            while self.open_links:
                cur_link = self.open_links.pop(0)
                self.closed_links.append(cur_link)
                g = s.get(cur_link)

                if g.status_code > 200:
                    continue

                if cur_link not in self.url_list:
                    self.url_list.append(cur_link)

                c = g.content
                soup = BeautifulSoup(c)
                links = soup.find_all("a")
                for link in links:
                    if link.has_attr('href') and link['href'] not in self.closed_links:
                        if (url + link['href']) not in self.closed_links:
                            if link['href'].startswith(url) and link['href'] not in self.open_links:
                                print(link['href'])
                                self.open_links.append(link['href'])
                            if link['href'].startswith("/") and not link['href'].startswith("//"):
                                if (url + link['href']) not in self.open_links:
                                    print(link['href'])
                                    self.open_links.append(url + link['href'])

                for l in self.open_links:
                    print(l)

    def crawl_node(self, node):
        visited = []
        local_links = []
        q = []

        node_url = self.base_url + "/" + node
        with requests.Session() as s:

            #  add node root url to queue and mark it as visited
            q.append(node_url)
            visited.append(node_url)

            #  while queue isn't empty:
            while q:

                #  pop node from queue and add to visited
                cur_link = q.pop(0)
                visited.append(cur_link)

                print(cur_link)  # print link

                g = s.get(cur_link)
                if g.status_code > 200:
                    print("Error. Moving on...")
                    continue

                local_links.append(cur_link)

                #  find all links in that node
                c = g.content
                soup = BeautifulSoup(c, 'html.parser')
                neighbors = soup.find_all("a")

                #  print neighbors
                neighbors_new = []
                for link in neighbors:
                    if link.has_attr('href'):
                        l = link['href']
                        if l.startswith('/' + node + '/'):
                            l = self.base_url + l
                        if l.startswith(self.base_url):
                            neighbors_new.append(l)

                for l in neighbors_new:

                    # link already is fully formed
                    if l not in visited:
                        visited.append(l)
                        q.append(l)

    def crawl_nodes(self, nodelist):
        for n in nodelist:
            self.crawl_node(n)

    def save_html(self,response,name):
        pass


c = Crawler("http://osf.io")

# c.crawl_from_root("http://localhost:5000")
start = datetime.datetime.now()
print("timer started: " + str(start))
c.crawl_nodes(c.crawl_api(10))

stop = datetime.datetime.now()
time = stop-start
print(time)
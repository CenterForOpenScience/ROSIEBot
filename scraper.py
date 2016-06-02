import requests
import crawler
import settings
import os

# rosie = crawler.Crawler()
# itinerary = rosie.crawl(limit=10)

base_urls = settings.base_urls

itinerary = ['', '#', 'explore/activity/', 'search/?q=*&filter=registration', 'meetings/', 'support/', 'login/?sign_up=True', 'login/?campaign=institution', 'forgotpassword/', 'search/?q=repro*', 'search/?q=brian+AND+title%3Amany', 'search/?q=tags%3A%28psychology%29', '#signUp', 'wun5q', 'ehpt4', 'f529n', '6j4rb', 'uzsak', 'udw78', 'wn2ak', 'q6zaj', '4bokd', 'gmh7k', 'yhdbq', 'yd6v7', 'mey5f', 'hyfxz', '9bm8v', '679uw', 'acnbd', 'vdcyx', 'ed6gv', 'xdojz', 'jtcu9', 'apg8j', 'vhw6d', 'n5zsm', 'we3hp', 'rys97', '745qn', 'r2gkb', 'tk36j', 'v2s7d', 'sdxvj', 'hp9xt', '45g2k', 'qzuf9', 'qajt2', 'mqs69', 'vksau', '6w543', 'hxzbd', 'y8adg', 'nhf3c', 'x7wpb', 'sbt6z', 'nvfbs', '4nuhy', 'pxmjc', 'w6gx9', 'pwsyu', 's5k3r', 'tasur', 'udwy6', '9wcdh', 'x5w7h', '6t4gc', 'n532g', '3etph', '92hqf', 'e9hjs', '2upwg', 'z8kdr', 'vstcq', 'ey45d', '7sqnm', 'b8k76', '8kqge', 'bqg6v', 'hr2s5', 'dpshk', 'tav4r', 'qvbx8', '82fba', '4tdms', 'gkwjx', 'crqxs', '4ybsq', '5tv3a', 'vwytd', 'w95da', 'r5dfg', 'uex5m', '4uc85', '4u9gj', 'neumq', '9j8pn', 'mv9wk', 'rm43b', '9c4rj', '8bma7', 'b7ezu', 'u4ysf', 'zd43w', 'ea3nm', 'p6y2g', 'tsbgj', '82gst', 'qh5t8', 'r57d3', 'wktx8', 'usrw8', '7r2bg', 'mvb9k', '43jbg', 'sqf6n', 'f2vn7', 'pa8ns', '8hyxd', 'eg2ma', 'ygxva', 'x5vca', 'veahc', '3y9z7', 'n9cr6', 'g2awm', 'm6kbr', 'ck73d', '5bs7z', 'kex62', 'nzur4', 'ex5jr', 'sjq6h', 'cx9vh', 'crma5', 'nh97v', 'pqxum', 'v32cr', 'ymsnh', 'dsc4r', '63gzr', 'mdt6u', '8vhtg', 'n8jz2', 'nfbcg', 'j4hda', 'knyqh', 'huw2y', 'mx365', 'gns79', 'qgzpc', 'wqtcy', 'be6sw', 'u48jt', 'cw8kf', 'kcavq', 'dvc2r', 'h5r7v', '9gts7', '6mdy7', '5k3hq', '4rdyz', 'yua9d', '49ujy', '2asj5', 'a4w2f', 'ktbr8', 'b4qsp', 'e6qdm', 'ub6vm', 'enr67', 'g25qn', '64cvp', 'prs8g', '9e5cv', 'xhka9', 'zwxea', 'h9jep', 'fbgp6', 'dnbmr', 'g46mp', 'svw5j', 'pw7t8', '7fy8m', 'e2muc', 'hftwj', 'd34q2', '35w2j', 'x92dw', 'yx9cd', 'he5am', 'zyp6m', 'ybkda', 'cbn2r', '2hc6e', 'z7t23', '8bqcr', '7mtud', 'j48r9', 'vfpxh', '9vspn', 's6xv9', '9sjc3', 'ud2fp', 'de9tq', 'rz925', '5h7br', 's4tp9', 'hswue', '5qvz3', 'uwhtr', 'nyp2r', 'vcebh', 'institutions/cos', 'institutions/ucr', 'institutions/usc']

print(itinerary)
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

# Start with explore/activity
    def write_HTML(self, page):
        r = requests.get(self.http_base + page)
        f = open(page + '.html', 'w')
        f.write(r.text)

    # def directory_nest(self, page):
    #     tree = page.split('/')
    #     path = ''
    #     for folder in tree:
    #         path += folder + '/'
    #         print('Folder:', path)
    #         print('In directory: ', folder)
    #     # Make directory
    #     # write HTML
    #     # cd directory
    #
    #     print(tree)
    # # def

rosieVacuum = Scraper()
# rosieVacuum.directory_nest('wun5q/wiki/home/')
rosieVacuum.write_HTML('wun5q')
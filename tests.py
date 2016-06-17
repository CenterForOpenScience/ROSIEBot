import unittest
from crawler import Crawler

class test_crawler(unittest.TestCase):

    def test_page_limit_too_high(self):
        c = Crawler()
        try:
            c.crawl_institutions_api(page_limit=3)
        except:
            print("crawl_institutions_api crashed!")

if __name__ == '__main__':
    unittest.main()
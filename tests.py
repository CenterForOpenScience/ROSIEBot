import unittest
from crawler import Crawler
import urllib
import datetime

d = datetime.datetime.fromtimestamp(0)


class test_crawler(unittest.TestCase):

    def test_page_limit_too_high(self):
        c = Crawler(d)
        try:
            c.crawl_institutions_api(page_limit=3)
        except:
            print("crawl_institutions_api crashed!")

    def test_node_urls_updated_by_crawl(self):
        c = Crawler(d)
        l1 = c.node_url_tuples.copy()
        c.crawl_nodes_api(page_limit=1)
        l2 = c.node_url_tuples.copy()
        self.assertEqual(len(l1), 0)
        self.assertGreater(len(l2), len(l1))
        self.assertNotEqual(l1, l2)
        for x in range(0,len(l2)-1):
            self.assertLess(c.node_url_tuples[x][1], c.node_url_tuples[x+1][1])
        for t in c.node_url_tuples:
            self.assertTrue(is_valid_url(t[0]))

    def test_registration_urls_updated_by_crawl(self):
        c = Crawler(d)
        l1 = c.registration_url_tuples.copy()
        c.crawl_registrations_api(page_limit=1)
        l2 = c.registration_url_tuples.copy()
        self.assertEqual(len(l1), 0)
        self.assertGreater(len(l2), len(l1))
        self.assertNotEqual(l1, l2)

    def test_institutions_urls_updated_by_crawl(self):
        c = Crawler(d)
        l1 = c.institution_urls.copy()
        c.crawl_institutions_api(page_limit=1)
        l2 = c.institution_urls.copy()
        self.assertEqual(len(l1), 1)
        self.assertGreater(len(l2), len(l1))
        self.assertNotEqual(l1, l2)

    def test_profile_urls_updated_by_crawl(self):
        c = Crawler(d)
        l1 = c.user_profile_page_urls.copy()
        c.crawl_users_api(page_limit=1)
        l2 = c.user_profile_page_urls.copy()
        self.assertEqual(len(l1), 0)
        self.assertGreater(len(l2), len(l1))
        self.assertNotEqual(l1, l2)

    def test_node_wiki_urls_updated_by_crawl(self):  # needs node_url_tuples to work
        c = Crawler(d)
        l1 = c._node_wikis_by_parent_guid.copy()
        self.assertEqual(len(l1), 0)
        c.crawl_nodes_api(page_limit=1)
        c.crawl_node_wiki()
        l2 = c._node_wikis_by_parent_guid.copy()
        self.assertGreater(len(l2), len(l1))
        self.assertNotEqual(l1, l2)

    def test_registration_wiki_urls_updated_by_crawl(self):  # needs node_url_tuples to work
        c = Crawler(d)
        l1 = c._registration_wikis_by_parent_guid.copy()
        self.assertEqual(len(l1), 0)
        c.crawl_registrations_api(page_limit=1)
        c.crawl_registration_wiki()
        l2 = c._registration_wikis_by_parent_guid.copy()
        self.assertGreater(len(l2), len(l1))
        self.assertNotEqual(l1, l2)

    def test_generate_node_urls(self):
        c = Crawler(d)
        c.crawl_nodes_api(page_limit=1)
        try:
            c.generate_node_urls()
        except:
            self.fail("crawler.generate_node_urls() failed")

    def test_scrape_url(self):
        c = Crawler(d)
        try:
            c._scrape_pages(['http://google.com', 'http://google.com/'])
            f = open('google.com/index.html')
            f.close()
        except:
            self.fail("page didn't save / get scraped at all")

        # if there isn't one already


def is_valid_url(url):
    if len(url) > 0:
        return True
    else:
        return False

if __name__ == '__main__':
    unittest.main()
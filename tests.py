import unittest
from crawler import Crawler
import urllib


class test_crawler(unittest.TestCase):

    def test_page_limit_too_high(self):
        c = Crawler()
        try:
            c.crawl_institutions_api(page_limit=3)
        except:
            print("crawl_institutions_api crashed!")

    def test_node_urls_updated_by_crawl(self):
        c = Crawler()
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

    # def test_registration_urls_updated_by_crawl(self):
    #     c = Crawler()
    #     l1 = c.registration_url_tuples.copy()
    #     c.crawl_registrations_api(page_limit=1)
    #     l2 = c.registration_url_tuples.copy()
    #     self.assertEqual(len(l1), 0)
    #     self.assertGreater(len(l2), len(l1))
    #     self.assertNotEqual(l1, l2)

    def test_institutions_urls_updated_by_crawl(self):
        c = Crawler()
        l1 = c.institution_url_list.copy()
        c.crawl_institutions_api(page_limit=1)
        l2 = c.institution_url_list.copy()
        self.assertEqual(len(l1), 1)
        self.assertGreater(len(l2), len(l1))
        self.assertNotEqual(l1, l2)

    def test_profile_urls_updated_by_crawl(self):
        c = Crawler()
        l1 = c.user_profile_page_list.copy()
        c.crawl_users_api(page_limit=1)
        l2 = c.user_profile_page_list.copy()
        self.assertEqual(len(l1), 0)
        self.assertGreater(len(l2), len(l1))
        self.assertNotEqual(l1, l2)

    def test_wiki_urls_updated_by_crawl(self):  # needs node_url_tuples to work
        c = Crawler()
        c.crawl_nodes_api(page_limit=1)
        l1 = c._wikis_by_parent_guid.copy()
        c.crawl_wiki()
        l2 = c._wikis_by_parent_guid.copy()
        self.assertEqual(len(l1), 0)
        self.assertGreater(len(l2), len(l1))
        self.assertNotEqual(l1, l2)

    def test_scrape_url(self):
        c = Crawler()
        c._scrape_pages(['http://google.com'])  # we need to put a slash at the end of each URL
        # if there isn't one already


def is_valid_url(url):
    if len(url) > 0:
        return True
    else:
        return False

if __name__ == '__main__':
    unittest.main()
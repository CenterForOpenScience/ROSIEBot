import os
from verifier import Verifier
import verifier
import unittest
# Verification tests
import json
import codecs

TASK_FILE = '201606231548.json'
with codecs.open(TASK_FILE, mode='r', encoding='utf-8') as file:
    run_info = json.load(file)

v = Verifier()


class TestVerifer(unittest.TestCase):
    def test_handle_errors(self):
        l1 = verifier.send_to_retry
        verifier.handle_errors()
        l2 = verifier.send_to_retry
        self.assertGreater(len(l1), len(l2))
        self.assertEqual(len(l2), len(l1) + len(run_info['error_list']))

    def test_get_path_from_url(self):
        path = v.get_path_from_url('http://staging.osf.io/mst3k')
        self.assertTrue(os.path.exists(path))

    def test_generate_page_dictionary(self):
        d1 = v.generate_page_dictionary('wiki/')
        self.assertGreater(len(d1), 0)


if __name__ == '__main__':
    unittest.main()

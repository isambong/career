
import unittest
from career.linkedin.jobs.parser import *


#@unittest.skip("showing class skipping")
class FunctionIteratorTestCase(unittest.TestCase):

    search_keywords = ['data analytics','data engineer']

    #@unittest.skip("demonstrating skipping")
    def test__init(self):
        fi = FunctionIterator(self.search_keywords, func, duration=10, sleepsecs=2)
        self.assertEqual(fi.idx, 0)
        self.assertEqual(fi.len, 2)
        self.assertTrue(fi.iterable)


def tests():
    unittest.main()

# if __name__ == '__main__':
#     unittest.main()

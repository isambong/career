
import unittest
from career.linkedin.jobs.collector import *


#@unittest.skip("showing class skipping")
class JobsDriverTestCase(unittest.TestCase):

    #@unittest.skip("demonstrating skipping")
    def test__init(self):
        jd = JobsDriver(driver='driver')
        attrs = [
            'base_url','search_keywords',
            'keywords_writing_secs','searchbutton_click_secs',
            'scroll_to_see_more_secs','scroll_to_premium_block_secs','job_details_human_reading_secs','job_details_ajax_waiting_secs',
        ]
        dirs = sorted(dir(jd))
        for attr in attrs:
            self.assertTrue(attr in dirs)

def tests():
    unittest.main()

# if __name__ == '__main__':
#     unittest.main()

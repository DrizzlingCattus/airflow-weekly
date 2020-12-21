import unittest
import numbers

from crawler_app import request as req


class TestRequest(unittest.TestCase):

    def test_get_maxitem_num_pass(self):
        num = req.get_maxitem_num()
        self.assertTrue(isinstance(num, numbers.Number))

    def test_get_item_info_pass(self):
        item_10_info = {
            'by': 'frobnicate', 
            'descendants': 0, 
            'id': 10, 
            'kids': [454419], 
            'score': 3, 
            'time': 1160421674, 
            'title': 'PhotoShow: Broadcast Photos to Cable TV', 
            'type': 'story', 
            'url': 'http://www.techcrunch.com/2006/10/09/broadcast-photos-to-cable-tv/'
        }
        info = req.get_item_info(10)
        self.assertDictEqual(info, item_10_info)


if __name__ == "__main__":
    unittest.main()

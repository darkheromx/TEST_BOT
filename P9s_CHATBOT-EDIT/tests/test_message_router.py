#Path : tests/test_message_router.py

import unittest
from core.intent_classifier import classify_intent
from core.oos_filter import is_out_of_scope

class TestMessageRouter(unittest.TestCase):
    def test_intent_lead(self):
        self.assertEqual(classify_intent('ผมสนใจเรียน'), 'lead')

    def test_oos_filter(self):
        self.assertTrue(is_out_of_scope('ราคาเท่าไร'))

if __name__ == '__main__':
    unittest.main()
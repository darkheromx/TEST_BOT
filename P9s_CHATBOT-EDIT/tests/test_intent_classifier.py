#Path : tests/test_intent_classifier.py

import unittest
from core.intent_classifier import classify_intent

class TestIntentClassifier(unittest.TestCase):
    def test_classify_lead(self):
        self.assertEqual(classify_intent('สมัครคอร์ส'), 'lead')
    def test_classify_ask(self):
        self.assertEqual(classify_intent('สวัสดี'), 'ask')

if __name__ == '__main__':
    unittest.main()
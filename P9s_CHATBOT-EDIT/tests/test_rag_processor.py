#Path : tests/test_rag_processor.py

import unittest
from core.rag_processor import process_question

class TestRagProcessor(unittest.TestCase):
    def test_missing_index(self):
        with self.assertRaises(Exception):
            process_question("test query without index")

if __name__ == '__main__':
    unittest.main()
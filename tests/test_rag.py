import unittest
from app.config import SIMILARITY_THRESHOLD

class TestRAGConfig(unittest.TestCase):
    def test_threshold(self):
        self.assertGreater(SIMILARITY_THRESHOLD, 0.0)
        self.assertLess(SIMILARITY_THRESHOLD, 1.0)

if __name__ == '__main__':
    unittest.main()

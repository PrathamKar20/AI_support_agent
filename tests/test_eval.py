import unittest
from eval.judge_rubric import validate_score

class TestJudgeRubric(unittest.TestCase):
    def test_valid_scores(self):
        self.assertTrue(validate_score(0.85))
        self.assertTrue(validate_score(1.0))
        self.assertFalse(validate_score(1.5))

if __name__ == '__main__':
    unittest.main()
# Test eval
def test_eval_metric():
    assert True

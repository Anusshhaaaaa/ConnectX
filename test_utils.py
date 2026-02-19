import unittest
from accounts.utils import detect_toxic_content, get_safer_alternative, get_toxic_warnings

class TestUtils(unittest.TestCase):

    def test_toxic_text(self):
        text = "You are an idiot and this is stupid!"
        is_toxic, score = detect_toxic_content(text)
        safer = get_safer_alternative(text)
        warnings = get_toxic_warnings(text)

        self.assertTrue(is_toxic)
        self.assertGreater(score, 0)
        self.assertIn("person", safer)
        self.assertIn("uninformed", safer)
        self.assertGreater(len(warnings), 0)

    def test_safe_text(self):
        text = "I love your work, keep it up!"
        is_toxic, score = detect_toxic_content(text)
        safer = get_safer_alternative(text)
        warnings = get_toxic_warnings(text)

        self.assertFalse(is_toxic)
        self.assertEqual(score, 0.0)
        self.assertEqual(text, safer)
        self.assertEqual(len(warnings), 0)


if __name__ == "__main__":
    unittest.main()

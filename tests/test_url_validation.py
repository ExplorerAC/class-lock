"""Unit tests for URL validation logic in Class Lock."""

import unittest
from src.class_mode import ClassModeController


class TestURLValidation(unittest.TestCase):
    """Test suite for URL parsing and normalization."""

    def test_valid_urls(self):
        test_cases = [
            ("https://app.sciastra.com/", "https://app.sciastra.com/"),
            ("http://example.com/class", "http://example.com/class"),
            ("app.sciastra.com", "https://app.sciastra.com"),
            ("classroom.google.com/u/0/h", "https://classroom.google.com/u/0/h"),
            ("  https://zoom.us/j/123456  ", "https://zoom.us/j/123456"),
            ("http://localhost:8000", "http://localhost:8000"),
        ]

        for raw_url, expected in test_cases:
            with self.subTest(raw_url=raw_url):
                valid, normalized, err = ClassModeController.validate_and_normalize_url(raw_url)
                self.assertTrue(valid, f"Expected {raw_url} to be valid. Error: {err}")
                self.assertEqual(normalized, expected)
                self.assertEqual(err, "")

    def test_invalid_urls(self):
        invalid_cases = [
            "",
            "   ",
            "not_a_domain",
            "ftp://files.example.com",
            "file:///C:/test.txt",
            "/invalid/path",
        ]

        for raw_url in invalid_cases:
            with self.subTest(raw_url=raw_url):
                valid, normalized, err = ClassModeController.validate_and_normalize_url(raw_url)
                self.assertFalse(valid, f"Expected {raw_url} to be invalid.")
                self.assertNotEqual(err, "")


if __name__ == "__main__":
    unittest.main()

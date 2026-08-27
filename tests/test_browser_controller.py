"""Unit tests for BrowserController."""

import unittest
from src.browser_controller import BrowserController


class TestBrowserController(unittest.TestCase):
    """Test suite for BrowserController."""

    def setUp(self):
        self.controller = BrowserController()

    def test_browser_detection(self):
        """Verify that at least one browser is detected on the Windows machine."""
        self.assertTrue(self.controller.is_browser_available(), "No supported browser was detected.")
        name = self.controller.get_browser_name()
        self.assertIn(name, ["Google Chrome", "Microsoft Edge"])

    def test_build_launch_arguments(self):
        """Verify the generated command line flags."""
        url = "https://app.sciastra.com/"
        args = self.controller.build_launch_arguments(url)
        self.assertIn(f"--app={url}", args)
        self.assertIn("--start-maximized", args)


if __name__ == "__main__":
    unittest.main()

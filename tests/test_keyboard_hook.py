"""Unit tests for KeyboardHook."""

import unittest
import sys
from src.keyboard_hook import KeyboardHook


class TestKeyboardHook(unittest.TestCase):
    """Test suite for KeyboardHook."""

    def test_hook_lifecycle(self):
        hook = KeyboardHook()
        self.assertFalse(hook.is_installed())

        if sys.platform == "win32":
            installed = hook.install()
            self.assertTrue(installed)
            hook.uninstall()
            self.assertFalse(hook.is_installed())


if __name__ == "__main__":
    unittest.main()

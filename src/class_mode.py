"""Class Mode Controller for Class Lock.

Coordinates state transitions between Normal PC mode and Class Mode,
manages URL validation, and interfaces with the browser, keyboard hook, and focus guardian.
"""

import re
import urllib.parse
from datetime import datetime
from typing import Optional, Tuple, Callable
from src.browser_controller import BrowserController
from src.window_controller import WindowController, FocusGuardian
from src.keyboard_hook import KeyboardHook


class ClassModeController:
    """Manages the lifecycle and state of Class Mode."""

    def __init__(self, browser_controller: Optional[BrowserController] = None):
        self.browser_controller = browser_controller or BrowserController()
        self.window_controller = WindowController()
        self.keyboard_hook = KeyboardHook(emergency_exit_callback=self._on_emergency_exit)
        self._get_ui_hwnd_callback: Callable[[], int] = lambda: 0
        self._on_state_change_callback: Optional[Callable[[bool], None]] = None

        self.focus_guardian = FocusGuardian(
            get_browser_pids=self.browser_controller.get_related_pids,
            get_ui_hwnd=lambda: self._get_ui_hwnd_callback()
        )

        self.is_active: bool = False
        self.active_url: Optional[str] = None
        self.start_time: Optional[datetime] = None

    def set_ui_hwnd_getter(self, callback: Callable[[], int]) -> None:
        """Set a callback that returns the HWND of the Class Lock UI window."""
        self._get_ui_hwnd_callback = callback

    def set_state_change_callback(self, callback: Callable[[bool], None]) -> None:
        """Set a callback to notify UI when class mode state changes."""
        self._on_state_change_callback = callback

    def _on_emergency_exit(self) -> None:
        """Handler for emergency exit hotkey."""
        self.end_class()

    @staticmethod
    def validate_and_normalize_url(raw_url: str) -> Tuple[bool, str, str]:
        """Validate and normalize user-provided URL.

        Returns:
            (is_valid, normalized_url, error_message)
        """
        if not raw_url or not raw_url.strip():
            return False, "", "URL cannot be empty."

        url = raw_url.strip()

        if not url.startswith("http://") and not url.startswith("https://"):
            if "." in url and not url.startswith("/"):
                url = "https://" + url
            else:
                return False, "", "Invalid URL format. Please enter a valid website address."

        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or parsed.scheme not in ["http", "https"]:
                return False, "", "URL must use HTTP or HTTPS protocol."

            if not parsed.netloc:
                return False, "", "Invalid domain name."

            domain = parsed.netloc.split(":")[0]
            if domain != "localhost" and "." not in domain:
                return False, "", "Invalid domain name. Must contain a valid TLD (e.g., .com, .org)."

            normalized = urllib.parse.urlunparse(parsed)
            return True, normalized, ""
        except Exception as e:
            return False, "", f"Failed to parse URL: {str(e)}"

    def start_class(self, raw_url: str) -> Tuple[bool, str]:
        """Start Class Mode with the specified URL."""
        if self.is_active:
            return True, "Class Mode is already active."

        is_valid, normalized_url, err_msg = self.validate_and_normalize_url(raw_url)
        if not is_valid:
            return False, err_msg

        try:
            # 1. Launch Native Browser
            self.browser_controller.start(normalized_url)

            # 2. Install Low-Level Keyboard Interceptor with Emergency Exit
            self.keyboard_hook.install()

            # 3. Start Window Focus Guardian
            self.focus_guardian.start()

            self.is_active = True
            self.active_url = normalized_url
            self.start_time = datetime.now()

            if self._on_state_change_callback:
                self._on_state_change_callback(True)

            return True, f"Class Mode started with {normalized_url}"
        except Exception as e:
            self.end_class()
            return False, f"Failed to launch Class Mode: {str(e)}"

    def end_class(self) -> Tuple[bool, str]:
        """End Class Mode and restore standard desktop environment."""
        try:
            # 1. Stop Focus Guardian
            self.focus_guardian.stop()

            # 2. Uninstall Keyboard Hook
            self.keyboard_hook.uninstall()

            # 3. Close Browser Session
            self.browser_controller.stop()

            self.is_active = False
            self.active_url = None
            self.start_time = None

            if self._on_state_change_callback:
                self._on_state_change_callback(False)

            return True, "Class Mode ended. Normal PC state restored."
        except Exception as e:
            return False, f"Error while stopping Class Mode: {str(e)}"

    def launch_calculator(self) -> bool:
        """Launch or bring Calculator into focus."""
        return self.window_controller.launch_calculator()

    def get_status(self) -> str:
        """Get the current textual status indicator."""
        return "CLASS MODE ACTIVE" if self.is_active else "INACTIVE"

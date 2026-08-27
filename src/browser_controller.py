"""Browser controller for Class Lock.

Launches the class website using the user's native Google Chrome / Microsoft Edge profile
in an application window that hides the tab strip to prevent tab clicking and switching,
while preserving all user extensions, logins, themes, and bookmarks.
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, List, Set

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    WM_CLOSE = 0x0010
else:
    user32 = None
    WM_CLOSE = 0


class BrowserController:
    """Controls the native browser instance used during Class Mode."""

    def __init__(self):
        self.browser_path: Optional[Path] = self._find_browser_executable()
        self.process: Optional[subprocess.Popen] = None
        self.class_hwnds: Set[int] = set()

    def _find_browser_executable(self) -> Optional[Path]:
        """Locate Google Chrome or Microsoft Edge on Windows."""
        possible_paths = [
            # Google Chrome locations
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            # Microsoft Edge locations
            Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        ]

        for p in possible_paths:
            if p.exists() and p.is_file():
                return p

        # Check system PATH
        for name in ["chrome.exe", "msedge.exe", "chrome", "msedge"]:
            found = shutil.which(name)
            if found:
                return Path(found)

        return None

    def is_browser_available(self) -> bool:
        """Return True if a supported browser was found."""
        return self.browser_path is not None and self.browser_path.exists()

    def get_browser_name(self) -> str:
        """Return the friendly name of the detected browser."""
        if not self.browser_path:
            return "None"
        if "chrome" in self.browser_path.name.lower():
            return "Google Chrome"
        if "msedge" in self.browser_path.name.lower() or "edge" in self.browser_path.name.lower():
            return "Microsoft Edge"
        return self.browser_path.name

    def build_launch_arguments(self, url: str) -> List[str]:
        """Build command line arguments to launch native browser in tab-free app mode."""
        if not self.browser_path:
            raise RuntimeError("No supported browser found on this system.")

        # Using --app with user's native profile removes tab strip while preserving extensions
        args = [
            str(self.browser_path),
            f"--app={url}",
            "--start-maximized",
        ]
        return args

    def _get_current_browser_hwnds(self) -> Set[int]:
        """Get all currently visible Chrome/Edge window handles."""
        if sys.platform != "win32" or not user32:
            return set()

        hwnds = set()
        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def enum_cb(hwnd, lparam):
            if user32.IsWindowVisible(hwnd):
                buf = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, buf, 256)
                if buf.value == "Chrome_WidgetWin_1":
                    hwnds.add(hwnd)
            return True

        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        return hwnds

    def start(self, url: str) -> bool:
        """Launch the class website in the user's native browser."""
        if not self.is_browser_available():
            raise FileNotFoundError("Could not find Google Chrome or Microsoft Edge installed.")

        hwnds_before = self._get_current_browser_hwnds()
        cmd = self.build_launch_arguments(url)

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

        if sys.platform == "win32":
            time.sleep(0.6)
            hwnds_after = self._get_current_browser_hwnds()
            new_hwnds = hwnds_after - hwnds_before
            self.class_hwnds = new_hwnds if new_hwnds else hwnds_after

        return True

    def is_running(self) -> bool:
        """Check if the launched browser process or window is currently active."""
        if sys.platform == "win32" and self.class_hwnds:
            for hwnd in self.class_hwnds:
                if user32.IsWindow(hwnd):
                    return True
        if self.process is None:
            return False
        return self.process.poll() is None

    def get_related_pids(self) -> Set[int]:
        """Return set of known process IDs."""
        pids = set()
        if self.process and self.process.pid:
            pids.add(self.process.pid)
        return pids

    def stop(self) -> None:
        """Close the launched class window cleanly."""
        if sys.platform == "win32" and user32 and self.class_hwnds:
            for hwnd in list(self.class_hwnds):
                if user32.IsWindow(hwnd):
                    user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            self.class_hwnds.clear()

        if self.process is not None:
            try:
                if self.process.poll() is None:
                    self.process.terminate()
            except Exception:
                pass
            finally:
                self.process = None

"""Window and Focus Guardian for Class Lock.

Handles launching and managing allowed windows (Class Browser, Calculator,
Class Lock UI) and keeping focus strictly within the study environment,
preventing minimization and switching to other apps.
"""

import os
import subprocess
import sys
import threading
import time
from typing import Optional, Set, Callable, List

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # Windows Constants
    SW_MINIMIZE = 6
    SW_RESTORE = 9
    SW_SHOWMAXIMIZED = 3
    SW_SHOW = 5
    SW_FORCEMINIMIZE = 11

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE

    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD)
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL

    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    # Window Enumeration Callback
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


class WindowController:
    """Provides window and application controls for Class Lock."""

    @staticmethod
    def get_process_image_path(pid: int) -> str:
        """Get the full executable path for a given process ID."""
        if sys.platform != "win32" or not pid:
            return ""
        h_proc = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h_proc:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(512)
            size = wintypes.DWORD(512)
            if kernel32.QueryFullProcessImageNameW(h_proc, 0, buf, ctypes.byref(size)):
                return buf.value.lower()
        finally:
            kernel32.CloseHandle(h_proc)
        return ""

    @staticmethod
    def find_calculator_hwnds() -> List[int]:
        """Find visible window handles belonging to Windows Calculator."""
        if sys.platform != "win32" or not user32:
            return []

        calc_hwnds = []

        def enum_cb(hwnd, lparam):
            if user32.IsWindowVisible(hwnd):
                title = WindowController.get_window_title(hwnd).lower()
                class_name = WindowController.get_window_class_name(hwnd).lower()
                pid = WindowController.get_window_pid(hwnd)
                proc_path = WindowController.get_process_image_path(pid)

                if "calculator" in title or "calc" in proc_path or "calculator" in class_name:
                    calc_hwnds.append(hwnd)
            return True

        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        return calc_hwnds

    @staticmethod
    def launch_calculator() -> bool:
        """Launch or bring Windows Calculator to foreground (reusing existing instance if open)."""
        try:
            if sys.platform == "win32":
                # Check if calculator is already open and bring it to front
                calc_hwnds = WindowController.find_calculator_hwnds()
                if calc_hwnds:
                    hwnd = calc_hwnds[0]
                    user32.ShowWindow(hwnd, SW_RESTORE)
                    user32.SetForegroundWindow(hwnd)
                    return True

                # If not open, launch calculator
                try:
                    os.startfile("calculator:")
                    return True
                except Exception:
                    subprocess.Popen(["calc.exe"], shell=True)
                    return True
            else:
                subprocess.Popen(["gnome-calculator"], shell=True)
                return True
        except Exception as e:
            print(f"Error launching calculator: {e}", file=sys.stderr)
            return False

    @staticmethod
    def is_calculator_running() -> bool:
        """Check if Windows Calculator process or window is active."""
        if sys.platform != "win32":
            return False
        if WindowController.find_calculator_hwnds():
            return True
        try:
            cmd = 'tasklist /FI "IMAGENAME eq CalculatorApp.exe" /FI "IMAGENAME eq calc.exe" /NH'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            output = result.stdout.lower()
            return "calculatorapp.exe" in output or "calc.exe" in output
        except Exception:
            return False

    @staticmethod
    def get_foreground_window() -> int:
        """Get the HWND of the currently active foreground window."""
        if sys.platform != "win32":
            return 0
        return user32.GetForegroundWindow()

    @staticmethod
    def get_window_pid(hwnd: int) -> int:
        """Get the process ID of a given window handle."""
        if sys.platform != "win32" or not hwnd:
            return 0
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return pid.value

    @staticmethod
    def get_window_title(hwnd: int) -> str:
        """Get the window title for a given window handle."""
        if sys.platform != "win32" or not hwnd:
            return ""
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value

    @staticmethod
    def get_window_class_name(hwnd: int) -> str:
        """Get the class name for a given window handle."""
        if sys.platform != "win32" or not hwnd:
            return ""
        buff = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buff, 256)
        return buff.value

    @staticmethod
    def is_window_minimized(hwnd: int) -> bool:
        """Check if a window is minimized."""
        if sys.platform != "win32" or not hwnd:
            return False
        return bool(user32.IsIconic(hwnd))

    @staticmethod
    def restore_and_maximize(hwnd: int) -> None:
        """Restore and maximize a window."""
        if sys.platform != "win32" or not hwnd:
            return
        user32.ShowWindow(hwnd, SW_SHOWMAXIMIZED)
        user32.SetForegroundWindow(hwnd)


class FocusGuardian:
    """Background daemon thread ensuring the class browser stays maximized and focused."""

    def __init__(self, get_browser_pids: Callable[[], Set[int]], get_ui_hwnd: Callable[[], int]):
        self.get_browser_pids = get_browser_pids
        self.get_ui_hwnd = get_ui_hwnd
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.own_pid = os.getpid()

    def start(self) -> None:
        """Start the focus monitor daemon."""
        if self._running or sys.platform != "win32":
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the focus monitor daemon."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None

    def _is_window_allowed(self, hwnd: int, fg_pid: int) -> bool:
        """Determine if a window belongs to the allowed study environment."""
        if not hwnd:
            return True

        # 1. Class Lock UI process
        if fg_pid == self.own_pid:
            return True

        # 2. Browser PIDs and Executable Image check
        browser_pids = self.get_browser_pids()
        if fg_pid in browser_pids:
            return True

        proc_path = WindowController.get_process_image_path(fg_pid)
        if "chrome.exe" in proc_path or "msedge.exe" in proc_path:
            return True

        # 3. Calculator Window check
        title = WindowController.get_window_title(hwnd).lower()
        class_name = WindowController.get_window_class_name(hwnd).lower()
        if "calc" in proc_path or "calculator" in title or "calculator" in class_name:
            return True

        # 4. Windows Desktop / Taskbar elements
        if class_name in ("shell_traywnd", "progman", "workerw"):
            return False

        # 5. System permission dialogs
        if class_name in ("#32770", "credential dialog xaml host"):
            return True

        return False

    def _find_browser_windows(self) -> List[int]:
        """Find visible window handles belonging to Chrome or Edge."""
        found_hwnds = []

        def enum_windows_callback(hwnd, lParam):
            if user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
                pid = WindowController.get_window_pid(hwnd)
                proc_path = WindowController.get_process_image_path(pid)
                if "chrome.exe" in proc_path or "msedge.exe" in proc_path:
                    class_name = WindowController.get_window_class_name(hwnd)
                    if class_name == "Chrome_WidgetWin_1":
                        found_hwnds.append(hwnd)
            return True

        cb = WNDENUMPROC(enum_windows_callback)
        user32.EnumWindows(cb, 0)
        return found_hwnds

    def _monitor_loop(self) -> None:
        """Continuously enforce browser maximized state and distraction block."""
        while self._running:
            try:
                # 1. Prevent Browser from being minimized: restore and maximize if iconic
                browser_hwnds = self._find_browser_windows()
                for bhwnd in browser_hwnds:
                    if WindowController.is_window_minimized(bhwnd):
                        WindowController.restore_and_maximize(bhwnd)

                # 2. Check current foreground window
                fg_hwnd = WindowController.get_foreground_window()
                if fg_hwnd:
                    fg_pid = WindowController.get_window_pid(fg_hwnd)
                    if not self._is_window_allowed(fg_hwnd, fg_pid):
                        # Unauthorized app has stolen focus -> minimize it immediately
                        user32.ShowWindow(fg_hwnd, SW_MINIMIZE)

                        # Restore and focus the Class Browser or Class Lock bar
                        if browser_hwnds:
                            WindowController.restore_and_maximize(browser_hwnds[0])
                        else:
                            ui_hwnd = self.get_ui_hwnd()
                            if ui_hwnd:
                                user32.SetForegroundWindow(ui_hwnd)
            except Exception:
                pass

            time.sleep(0.15)

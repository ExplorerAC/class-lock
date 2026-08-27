"""Low-Level Keyboard Hook for Class Lock.

Intercepts distraction shortcuts during active Class Mode and provides an
emergency escape shortcut (Ctrl+Alt+End or Ctrl+Alt+X) to safely end class mode anytime.
"""

import sys
import threading
from typing import Optional, Callable

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # Windows Hook Constants
    WH_KEYBOARD_LL = 13
    WM_KEYDOWN = 0x0100
    WM_SYSKEYDOWN = 0x0104
    WM_KEYUP = 0x0101
    WM_SYSKEYUP = 0x0105
    WM_QUIT = 0x0012

    # Virtual Key Codes
    VK_TAB = 0x09
    VK_ESCAPE = 0x1B
    VK_PRIOR = 0x21      # Page Up
    VK_NEXT = 0x22       # Page Down
    VK_END = 0x23        # End Key
    VK_LWIN = 0x5B
    VK_RWIN = 0x5C
    VK_CONTROL = 0x11
    VK_LCONTROL = 0xA2
    VK_RCONTROL = 0xA3
    VK_MENU = 0x12       # Alt
    VK_LMENU = 0xA4
    VK_RMENU = 0xA5
    VK_SHIFT = 0x10

    # Numbers 1-9 (0x31 - 0x39) & Numpad 1-9 (0x61 - 0x69)
    VK_NUM_1_TO_9 = tuple(range(0x31, 0x3A)) + tuple(range(0x61, 0x6A))

    # Letters / Browser hotkeys
    VK_T = 0x54  # New Tab
    VK_N = 0x4E  # New Window
    VK_W = 0x57  # Close Tab
    VK_H = 0x48  # History
    VK_J = 0x4A  # Downloads
    VK_L = 0x4C  # Address Bar focus
    VK_K = 0x4B  # Search bar focus
    VK_E = 0x45  # Search bar focus
    VK_O = 0x4F  # Open file
    VK_U = 0x55  # View source
    VK_X = 0x58  # X Key (Ctrl+Alt+X)
    VK_D = 0x44  # Win+D Show Desktop
    VK_M = 0x4D  # Win+M Minimize
    VK_DOWN = 0x28  # Win+Down Minimize

    LLKHF_ALTDOWN = 0x20

    # Hook callback type & win32 signatures
    HOOKPROC = ctypes.WINFUNCTYPE(
        wintypes.LPARAM,
        ctypes.c_int,
        wintypes.WPARAM,
        wintypes.LPARAM
    )

    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE

    user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
    user32.SetWindowsHookExW.restype = wintypes.HHOOK

    user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
    user32.UnhookWindowsHookEx.restype = wintypes.BOOL

    user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
    user32.CallNextHookEx.restype = wintypes.LPARAM

    user32.GetKeyState.argtypes = [ctypes.c_int]
    user32.GetKeyState.restype = wintypes.SHORT

    user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
    user32.GetAsyncKeyState.restype = wintypes.SHORT

    class KBDLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [
            ("vkCode", wintypes.DWORD),
            ("scanCode", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.c_ulonglong if sys.maxsize > 2**32 else ctypes.c_ulong),
        ]


class KeyboardHook:
    """Manages installation and removal of low-level keyboard distraction interceptor."""

    def __init__(self, emergency_exit_callback: Optional[Callable[[], None]] = None):
        self.emergency_exit_callback = emergency_exit_callback
        self.hook_id = None
        self._thread: Optional[threading.Thread] = None
        self._thread_id: Optional[int] = None
        self._hook_proc = None
        self._is_active = False
        self._ready_event = threading.Event()
        self._ctrl_pressed = False
        self._alt_pressed = False
        self._win_pressed = False

    def is_installed(self) -> bool:
        return self._is_active

    def _is_ctrl_down(self) -> bool:
        if sys.platform != "win32":
            return False
        return (
            self._ctrl_pressed
            or bool(user32.GetAsyncKeyState(VK_CONTROL) & 0x8000)
            or bool(user32.GetKeyState(VK_CONTROL) & 0x8000)
        )

    def _is_alt_down(self, flags: int) -> bool:
        if sys.platform != "win32":
            return False
        return (
            bool(flags & LLKHF_ALTDOWN)
            or self._alt_pressed
            or bool(user32.GetAsyncKeyState(VK_MENU) & 0x8000)
            or bool(user32.GetKeyState(VK_MENU) & 0x8000)
        )

    def _is_win_down(self) -> bool:
        if sys.platform != "win32":
            return False
        return (
            self._win_pressed
            or bool(user32.GetAsyncKeyState(VK_LWIN) & 0x8000)
            or bool(user32.GetAsyncKeyState(VK_RWIN) & 0x8000)
        )

    def _hook_callback(self, nCode, wParam, lParam):
        """Callback executed for every low-level keyboard event."""
        if nCode >= 0:
            kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk = kb_struct.vkCode
            flags = kb_struct.flags
            is_down = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)

            # Update modifier key tracking
            if vk in (VK_CONTROL, VK_LCONTROL, VK_RCONTROL):
                self._ctrl_pressed = is_down
            elif vk in (VK_MENU, VK_LMENU, VK_RMENU):
                self._alt_pressed = is_down
            elif vk in (VK_LWIN, VK_RWIN):
                self._win_pressed = is_down

            ctrl_down = self._is_ctrl_down()
            alt_down = self._is_alt_down(flags)
            win_down = self._is_win_down()

            # 0. Emergency Exit Shortcut: Ctrl + Alt + End OR Ctrl + Alt + X
            if is_down and ctrl_down and alt_down and vk in (VK_END, VK_X):
                if self.emergency_exit_callback:
                    threading.Thread(target=self.emergency_exit_callback, daemon=True).start()
                return 1

            # 1. Block Windows Key (Start Menu) & Win Shortcuts (Win+D, Win+M, Win+Down)
            if vk in (VK_LWIN, VK_RWIN):
                return 1
            if win_down and vk in (VK_D, VK_M, VK_DOWN, VK_TAB):
                return 1

            # 2. Block Alt + Tab / Alt + Esc (Task Switcher)
            if alt_down and vk in (VK_TAB, VK_ESCAPE):
                return 1

            # 3. Block Tab Switching, Tab Creation, and Browser Navigation when Ctrl is held
            if ctrl_down:
                # Tab switching: Ctrl+Tab, Ctrl+Shift+Tab, Ctrl+PageUp/Down, Ctrl+1..9
                if vk in (VK_TAB, VK_PRIOR, VK_NEXT) or vk in VK_NUM_1_TO_9:
                    return 1

                # Tab opening / navigation / closing
                blocked_ctrl_keys = (
                    VK_T,  # New Tab
                    VK_N,  # New Window
                    VK_W,  # Close Tab
                    VK_H,  # History
                    VK_J,  # Downloads
                    VK_L,  # Address Bar focus
                    VK_K,  # Search bar
                    VK_E,  # Search bar
                    VK_O,  # Open file
                    VK_U,  # View source
                )
                if vk in blocked_ctrl_keys:
                    return 1

        return user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

    def _hook_thread_func(self):
        """Dedicated thread function that installs the hook and runs a message pump."""
        if sys.platform != "win32":
            self._ready_event.set()
            return

        self._thread_id = kernel32.GetCurrentThreadId()
        self._hook_proc = HOOKPROC(self._hook_callback)
        mod_handle = kernel32.GetModuleHandleW(None)

        self.hook_id = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self._hook_proc,
            mod_handle,
            0
        )

        if not self.hook_id:
            self._is_active = False
            self._ready_event.set()
            return

        self._is_active = True
        self._ready_event.set()

        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_QUIT:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if self.hook_id:
            user32.UnhookWindowsHookEx(self.hook_id)
            self.hook_id = None
        self._is_active = False

    def install(self) -> bool:
        """Start the keyboard hook in a background thread."""
        if sys.platform != "win32" or self._is_active:
            return True

        self._ready_event.clear()
        self._ctrl_pressed = False
        self._alt_pressed = False
        self._win_pressed = False
        self._thread = threading.Thread(target=self._hook_thread_func, daemon=True)
        self._thread.start()
        self._ready_event.wait(timeout=1.0)
        return self._is_active

    def uninstall(self) -> None:
        """Remove the keyboard hook and terminate the hook message loop."""
        if sys.platform != "win32" or not self._is_active:
            return

        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        self._thread = None
        self._thread_id = None
        self._is_active = False

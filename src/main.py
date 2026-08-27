"""Main entry point for Class Lock application."""

import atexit
import signal
import sys
import tkinter as tk
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.class_mode import ClassModeController
from src.ui import ClassLockUI

# Global controller instance for clean termination handlers
_global_controller = None


def _cleanup():
    global _global_controller
    if _global_controller and _global_controller.is_active:
        try:
            _global_controller.end_class()
        except Exception:
            pass


def _signal_handler(sig, frame):
    _cleanup()
    sys.exit(0)


def main():
    global _global_controller

    # Register exit handlers
    atexit.register(_cleanup)
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Windows DPI awareness & console handlers
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        try:
            import ctypes
            from ctypes import wintypes

            PHANDLER_ROUTINE = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

            def win_ctrl_handler(ctrl_type):
                _cleanup()
                return False

            ctypes.windll.kernel32.SetConsoleCtrlHandler(PHANDLER_ROUTINE(win_ctrl_handler), True)
        except Exception:
            pass

    root = tk.Tk()
    _global_controller = ClassModeController()
    app = ClassLockUI(root, _global_controller)
    root.mainloop()


if __name__ == "__main__":
    main()

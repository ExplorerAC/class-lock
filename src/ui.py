"""Class Lock User Interface.

A clean, minimal, distraction-free desktop interface built with Tkinter.
Supports a standard config window when inactive and a compact, always-on-top
floating control pill when Class Mode is active, with emergency exit keybindings.
"""

import json
import os
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from typing import Optional

from src.class_mode import ClassModeController


class ClassLockUI:
    """Desktop UI for toggling Class Mode."""

    def __init__(self, root: tk.Tk, controller: Optional[ClassModeController] = None):
        self.root = root
        self.controller = controller or ClassModeController()
        self.config_path = Path(__file__).parent.parent / "config" / "settings.json"

        # Register UI callbacks
        self.controller.set_ui_hwnd_getter(self._get_hwnd)
        self.controller.set_state_change_callback(self._on_state_change)

        self.root.title("Class Lock")
        self.normal_geometry = "480x430"
        self.root.geometry(self.normal_geometry)
        self.root.minsize(440, 390)
        self.root.configure(bg="#121417")

        self._timer_job = None

        self._setup_styles()
        self._load_config()
        self._build_normal_ui()
        self._update_status_display()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_hwnd(self) -> int:
        """Get the native Windows HWND for the Tkinter root window."""
        try:
            return self.root.winfo_id()
        except Exception:
            return 0

    def _on_state_change(self, is_active: bool) -> None:
        """Thread-safe UI update when state changes (e.g. via emergency shortcut)."""
        def update():
            if is_active:
                self._switch_to_floating_mode()
            else:
                self._switch_to_normal_mode()
        self.root.after(0, update)

    def _setup_styles(self) -> None:
        """Configure Tkinter fonts and palette."""
        self.font_title = ("Segoe UI", 18, "bold")
        self.font_subtitle = ("Segoe UI", 9)
        self.font_label = ("Segoe UI", 10, "bold")
        self.font_entry = ("Segoe UI", 11)
        self.font_status = ("Segoe UI", 11, "bold")
        self.font_btn_main = ("Segoe UI", 12, "bold")
        self.font_btn_sec = ("Segoe UI", 10)
        self.font_pill = ("Segoe UI", 10, "bold")

        # Palette
        self.c_bg = "#121417"
        self.c_card = "#1E2228"
        self.c_text = "#F0F3F6"
        self.c_muted = "#8B949E"
        self.c_primary = "#2EA043"      # Active Green
        self.c_primary_hover = "#3FB950"
        self.c_danger = "#DA3633"       # Stop Red
        self.c_danger_hover = "#F85149"
        self.c_sec_btn = "#30363D"
        self.c_sec_btn_hover = "#3D444D"
        self.c_border = "#30363D"

    def _load_config(self) -> None:
        """Load settings from config file if present."""
        self.default_url = "https://app.sciastra.com/"
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.default_url = data.get("last_url", self.default_url)
            except Exception:
                pass

    def _save_config(self, url: str) -> None:
        """Persist last used URL to config."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({"last_url": url.strip()}, f, indent=2)
        except Exception:
            pass

    def _build_normal_ui(self) -> None:
        """Build the full configuration interface for normal PC mode."""
        self.main_container = tk.Frame(self.root, bg=self.c_bg, padx=24, pady=20)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Header Title
        title_frame = tk.Frame(self.main_container, bg=self.c_bg)
        title_frame.pack(fill=tk.X, pady=(0, 16))

        title_label = tk.Label(
            title_frame,
            text="Class Lock",
            font=self.font_title,
            fg=self.c_text,
            bg=self.c_bg
        )
        title_label.pack(anchor="w")

        subtitle = tk.Label(
            title_frame,
            text="Dedicated Single-Site Study Environment",
            font=self.font_subtitle,
            fg=self.c_muted,
            bg=self.c_bg
        )
        subtitle.pack(anchor="w")

        # Status Bar Card
        self.status_card = tk.Frame(
            self.main_container,
            bg=self.c_card,
            padx=16,
            pady=12,
            highlightthickness=1,
            highlightbackground=self.c_border
        )
        self.status_card.pack(fill=tk.X, pady=(0, 16))

        status_title = tk.Label(
            self.status_card,
            text="CURRENT STATUS",
            font=("Segoe UI", 8, "bold"),
            fg=self.c_muted,
            bg=self.c_card
        )
        status_title.pack(anchor="w")

        self.status_badge = tk.Label(
            self.status_card,
            text="INACTIVE",
            font=self.font_status,
            fg=self.c_muted,
            bg=self.c_card
        )
        self.status_badge.pack(anchor="w", pady=(2, 0))

        # URL Input Area
        input_frame = tk.Frame(self.main_container, bg=self.c_bg)
        input_frame.pack(fill=tk.X, pady=(0, 16))

        url_label = tk.Label(
            input_frame,
            text="Class Website URL",
            font=self.font_label,
            fg=self.c_text,
            bg=self.c_bg
        )
        url_label.pack(anchor="w", pady=(0, 6))

        self.url_entry = tk.Entry(
            input_frame,
            font=self.font_entry,
            bg=self.c_card,
            fg=self.c_text,
            insertbackground=self.c_text,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.c_border,
            highlightcolor="#58A6FF"
        )
        self.url_entry.pack(fill=tk.X, ipady=8, padx=1)
        self.url_entry.insert(0, self.default_url)

        # Primary Action Buttons
        btn_frame = tk.Frame(self.main_container, bg=self.c_bg)
        btn_frame.pack(fill=tk.X, pady=(0, 14))

        self.btn_start = tk.Button(
            btn_frame,
            text="START CLASS",
            font=self.font_btn_main,
            bg=self.c_primary,
            fg="#FFFFFF",
            activebackground=self.c_primary_hover,
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._on_start_class
        )
        self.btn_start.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8, padx=(0, 6))

        self.btn_end = tk.Button(
            btn_frame,
            text="END CLASS",
            font=self.font_btn_main,
            bg=self.c_sec_btn,
            fg=self.c_muted,
            activebackground=self.c_danger_hover,
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._on_end_class
        )
        self.btn_end.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8, padx=(6, 0))

        # Utilities / Calculator Row
        util_frame = tk.Frame(self.main_container, bg=self.c_bg)
        util_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_calc = tk.Button(
            util_frame,
            text="🖩  OPEN CALCULATOR",
            font=self.font_btn_sec,
            bg=self.c_sec_btn,
            fg=self.c_text,
            activebackground=self.c_sec_btn_hover,
            activeforeground=self.c_text,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._on_open_calculator
        )
        self.btn_calc.pack(fill=tk.X, ipady=6)

        # Emergency & Browser info footer
        footer_frame = tk.Frame(self.main_container, bg=self.c_bg)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.info_label = tk.Label(
            footer_frame,
            text=f"Browser: {self.controller.browser_controller.get_browser_name()}  •  Emergency Exit: Ctrl+Alt+End (or Ctrl+Alt+X)",
            font=("Segoe UI", 8),
            fg=self.c_muted,
            bg=self.c_bg
        )
        self.info_label.pack(anchor="center")

    def _build_floating_pill_ui(self) -> None:
        """Build the compact always-on-top toolbar used during Class Mode."""
        self.pill_container = tk.Frame(
            self.root,
            bg="#161B22",
            padx=12,
            pady=6,
            highlightthickness=1,
            highlightbackground="#2EA043"
        )
        self.pill_container.pack(fill=tk.BOTH, expand=True)

        # Status badge & indicator
        status_lbl = tk.Label(
            self.pill_container,
            text="● CLASS ACTIVE",
            font=self.font_pill,
            fg="#3FB950",
            bg="#161B22"
        )
        status_lbl.pack(side=tk.LEFT, padx=(4, 10))

        # Session Timer
        self.timer_label = tk.Label(
            self.pill_container,
            text="00:00",
            font=("Segoe UI", 10),
            fg=self.c_muted,
            bg="#161B22"
        )
        self.timer_label.pack(side=tk.LEFT, padx=(0, 10))

        # Open Calculator Quick Button
        calc_btn = tk.Button(
            self.pill_container,
            text="🖩 Calc",
            font=("Segoe UI", 9, "bold"),
            bg=self.c_sec_btn,
            fg=self.c_text,
            activebackground=self.c_sec_btn_hover,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._on_open_calculator,
            padx=8,
            pady=2
        )
        calc_btn.pack(side=tk.LEFT, padx=(0, 8))

        # End Class Button (Large & prominent)
        end_btn = tk.Button(
            self.pill_container,
            text="🔴 END CLASS",
            font=("Segoe UI", 9, "bold"),
            bg=self.c_danger,
            fg="#FFFFFF",
            activebackground=self.c_danger_hover,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._on_end_class,
            padx=12,
            pady=2
        )
        end_btn.pack(side=tk.RIGHT, padx=(4, 4))

    def _switch_to_floating_mode(self) -> None:
        """Switch window into compact always-on-top floating pill at top of screen."""
        if hasattr(self, "main_container") and self.main_container.winfo_exists():
            self.main_container.destroy()

        screen_width = self.root.winfo_screenwidth()
        pill_width = 460
        pill_height = 50
        x = max(10, (screen_width - pill_width) // 2)
        y = 10

        self.root.geometry(f"{pill_width}x{pill_height}+{x}+{y}")
        self.root.minsize(pill_width, pill_height)
        self.root.attributes("-topmost", True)
        self.root.lift()
        self._build_floating_pill_ui()
        self._start_timer_tick()

    def _switch_to_normal_mode(self) -> None:
        """Switch window back to standard dashboard configuration."""
        self._stop_timer_tick()
        if hasattr(self, "pill_container") and self.pill_container.winfo_exists():
            self.pill_container.destroy()

        self.root.attributes("-topmost", False)
        self.root.minsize(440, 390)
        self.root.geometry(self.normal_geometry)
        self._build_normal_ui()
        self._update_status_display()

    def _start_timer_tick(self) -> None:
        """Update session timer and continuously re-assert always-on-top prominence."""
        if self.controller.is_active and self.controller.start_time:
            # Guarantee floating bar is never buried or lost
            self.root.attributes("-topmost", True)
            self.root.lift()

            elapsed = datetime.now() - self.controller.start_time
            total_seconds = int(elapsed.total_seconds())
            mins, secs = divmod(total_seconds, 60)
            hrs, mins = divmod(mins, 60)
            if hrs > 0:
                time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
            else:
                time_str = f"{mins:02d}:{secs:02d}"

            if hasattr(self, "timer_label") and self.timer_label.winfo_exists():
                self.timer_label.config(text=time_str)

            self._timer_job = self.root.after(1000, self._start_timer_tick)

    def _stop_timer_tick(self) -> None:
        """Cancel active timer job."""
        if self._timer_job:
            self.root.after_cancel(self._timer_job)
            self._timer_job = None

    def _on_start_class(self) -> None:
        """Handler for START CLASS button."""
        raw_url = self.url_entry.get()
        success, message = self.controller.start_class(raw_url)

        if success:
            self._save_config(raw_url)
        else:
            messagebox.showerror("Error Starting Class", message, parent=self.root)

    def _on_end_class(self) -> None:
        """Handler for END CLASS button."""
        success, message = self.controller.end_class()
        if not success:
            messagebox.showerror("Error Ending Class", message, parent=self.root)

    def _on_open_calculator(self) -> None:
        """Handler for OPEN CALCULATOR button."""
        launched = self.controller.launch_calculator()
        if not launched:
            messagebox.showwarning("Calculator", "Could not open Windows Calculator.", parent=self.root)

    def _update_status_display(self) -> None:
        """Update normal UI status display."""
        if not hasattr(self, "status_badge") or not self.status_badge.winfo_exists():
            return

        if self.controller.is_active:
            self.status_badge.config(
                text="● CLASS MODE ACTIVE",
                fg="#3FB950"
            )
            self.status_card.config(highlightbackground="#2EA043")
            self.btn_start.config(
                state=tk.DISABLED,
                bg=self.c_sec_btn,
                fg=self.c_muted
            )
            self.btn_end.config(
                state=tk.NORMAL,
                bg=self.c_danger,
                fg="#FFFFFF"
            )
            self.url_entry.config(state=tk.DISABLED)
        else:
            self.status_badge.config(
                text="○ INACTIVE",
                fg=self.c_muted
            )
            self.status_card.config(highlightbackground=self.c_border)
            self.btn_start.config(
                state=tk.NORMAL,
                bg=self.c_primary,
                fg="#FFFFFF"
            )
            self.btn_end.config(
                state=tk.DISABLED,
                bg=self.c_sec_btn,
                fg=self.c_muted
            )
            self.url_entry.config(state=tk.NORMAL)

    def _on_close(self) -> None:
        """Handle application close safely by ending active class mode."""
        if self.controller.is_active:
            confirm = messagebox.askyesno(
                "Exit Class Lock",
                "Class Mode is currently active. Ending Class Lock will close the class browser session and restore normal PC mode. Continue?",
                parent=self.root
            )
            if not confirm:
                return

            self.controller.end_class()

        self._stop_timer_tick()
        self.root.destroy()

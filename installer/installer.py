"""Class Lock GUI Setup Installer.

Installs Class Lock to %LOCALAPPDATA%\\Programs\\ClassLock, creates Desktop & Start Menu
shortcuts, registers Windows Uninstaller entry, and launches the application.
"""

import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
import winreg


class ClassLockInstallerUI:
    """Modern Windows Setup Wizard for Class Lock."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Class Lock Setup")
        self.root.geometry("520x460")
        self.root.minsize(500, 440)
        self.root.configure(bg="#121417")

        # Determine embedded or sibling payload path
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            self.bundle_dir = Path(sys._MEIPASS)
        else:
            self.bundle_dir = Path(__file__).parent.parent / "dist"

        self.payload_exe = self.bundle_dir / "ClassLock.exe"
        if not self.payload_exe.exists():
            # Check project dist folder as fallback
            alt = Path(__file__).parent.parent / "dist" / "ClassLock.exe"
            if alt.exists():
                self.payload_exe = alt

        # Default install paths (no admin required)
        local_appdata = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        self.default_install_dir = Path(local_appdata) / "Programs" / "ClassLock"
        self.install_dir_var = tk.StringVar(value=str(self.default_install_dir))

        self.desktop_shortcut_var = tk.BooleanVar(value=True)
        self.startmenu_shortcut_var = tk.BooleanVar(value=True)
        self.launch_after_var = tk.BooleanVar(value=True)

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self) -> None:
        """Palette and fonts."""
        self.c_bg = "#121417"
        self.c_card = "#1E2228"
        self.c_text = "#F0F3F6"
        self.c_muted = "#8B949E"
        self.c_primary = "#2EA043"
        self.c_primary_hover = "#3FB950"
        self.c_border = "#30363D"

        self.font_title = ("Segoe UI", 16, "bold")
        self.font_body = ("Segoe UI", 10)
        self.font_btn = ("Segoe UI", 11, "bold")

    def _build_ui(self) -> None:
        container = tk.Frame(self.root, bg=self.c_bg, padx=28, pady=24)
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(container, bg=self.c_bg)
        header_frame.pack(fill=tk.X, pady=(0, 16))

        title_lbl = tk.Label(
            header_frame,
            text="Install Class Lock",
            font=self.font_title,
            fg=self.c_text,
            bg=self.c_bg
        )
        title_lbl.pack(anchor="w")

        desc_lbl = tk.Label(
            header_frame,
            text="Setup will install Class Lock to your user environment.",
            font=self.font_body,
            fg=self.c_muted,
            bg=self.c_bg
        )
        desc_lbl.pack(anchor="w", pady=(2, 0))

        # Destination Folder Card
        folder_card = tk.Frame(
            container,
            bg=self.c_card,
            padx=16,
            pady=14,
            highlightthickness=1,
            highlightbackground=self.c_border
        )
        folder_card.pack(fill=tk.X, pady=(0, 16))

        folder_title = tk.Label(
            folder_card,
            text="DESTINATION FOLDER",
            font=("Segoe UI", 8, "bold"),
            fg=self.c_muted,
            bg=self.c_card
        )
        folder_title.pack(anchor="w", pady=(0, 6))

        entry_frame = tk.Frame(folder_card, bg=self.c_card)
        entry_frame.pack(fill=tk.X)

        self.entry_dir = tk.Entry(
            entry_frame,
            textvariable=self.install_dir_var,
            font=("Segoe UI", 10),
            bg="#161B22",
            fg=self.c_text,
            insertbackground=self.c_text,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.c_border
        )
        self.entry_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))

        # Options Card
        opts_card = tk.Frame(
            container,
            bg=self.c_card,
            padx=16,
            pady=14,
            highlightthickness=1,
            highlightbackground=self.c_border
        )
        opts_card.pack(fill=tk.X, pady=(0, 20))

        opts_title = tk.Label(
            opts_card,
            text="INSTALLATION OPTIONS",
            font=("Segoe UI", 8, "bold"),
            fg=self.c_muted,
            bg=self.c_card
        )
        opts_title.pack(anchor="w", pady=(0, 8))

        cb_style = {"bg": self.c_card, "fg": self.c_text, "activebackground": self.c_card, "activeforeground": self.c_text, "selectcolor": "#161B22", "font": self.font_body}

        cb_desktop = tk.Checkbutton(opts_card, text="Create Desktop Shortcut", variable=self.desktop_shortcut_var, **cb_style)
        cb_desktop.pack(anchor="w", pady=2)

        cb_start = tk.Checkbutton(opts_card, text="Create Start Menu Shortcut", variable=self.startmenu_shortcut_var, **cb_style)
        cb_start.pack(anchor="w", pady=2)

        cb_launch = tk.Checkbutton(opts_card, text="Launch Class Lock after installation", variable=self.launch_after_var, **cb_style)
        cb_launch.pack(anchor="w", pady=2)

        # Progress / Status
        self.status_lbl = tk.Label(
            container,
            text="Ready to install.",
            font=("Segoe UI", 9),
            fg=self.c_muted,
            bg=self.c_bg
        )
        self.status_lbl.pack(anchor="w", pady=(0, 8))

        # Action Buttons
        btn_frame = tk.Frame(container, bg=self.c_bg)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_install = tk.Button(
            btn_frame,
            text="INSTALL NOW",
            font=self.font_btn,
            bg=self.c_primary,
            fg="#FFFFFF",
            activebackground=self.c_primary_hover,
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._run_installation
        )
        self.btn_install.pack(fill=tk.X, ipady=8)

    def _create_shortcut(self, target_path: Path, shortcut_path: Path, description: str = "Class Lock") -> None:
        """Create a Windows .lnk shortcut using PowerShell WScript.Shell."""
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)
        ps_script = (
            f"$w = New-Object -ComObject WScript.Shell; "
            f"$s = $w.CreateShortcut('{str(shortcut_path)}'); "
            f"$s.TargetPath = '{str(target_path)}'; "
            f"$s.WorkingDirectory = '{str(target_path.parent)}'; "
            f"$s.Description = '{description}'; "
            f"$s.Save()"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

    def _register_uninstaller(self, install_dir: Path, target_exe: Path) -> None:
        """Register application in Windows Add or Remove Programs (HKCU)."""
        if sys.platform != "win32":
            return
        try:
            # Create uninstall script
            uninstaller_bat = install_dir / "uninstall.bat"
            uninstaller_content = (
                "@echo off\n"
                "title Uninstall Class Lock\n"
                "echo Uninstalling Class Lock...\n"
                f'del /f /q "{Path.home() / "Desktop" / "Class Lock.lnk"}" 2>nul\n'
                f'del /f /q "{Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Class Lock.lnk"}" 2>nul\n'
                'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ClassLock" /f 2>nul\n'
                'timeout /t 1 >nul\n'
                f'rd /s /q "{install_dir}"\n'
                'echo Class Lock has been uninstalled successfully.\n'
                'pause\n'
            )
            with open(uninstaller_bat, "w", encoding="utf-8") as f:
                f.write(uninstaller_content)

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ClassLock"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Class Lock")
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Class Lock Team")
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(target_exe))
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_dir))
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'cmd.exe /c "{uninstaller_bat}"')
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        except Exception:
            pass

    def _run_installation(self) -> None:
        """Execute the installation sequence."""
        target_dir = Path(self.install_dir_var.get().strip())
        if not target_dir:
            messagebox.showerror("Error", "Please select a valid installation directory.", parent=self.root)
            return

        if not self.payload_exe.exists():
            messagebox.showerror("Error", f"ClassLock.exe payload not found at {self.payload_exe}.", parent=self.root)
            return

        try:
            self.status_lbl.config(text="Creating destination folder...")
            self.root.update()
            target_dir.mkdir(parents=True, exist_ok=True)

            target_exe = target_dir / "ClassLock.exe"
            self.status_lbl.config(text="Copying ClassLock.exe...")
            self.root.update()
            shutil.copy2(self.payload_exe, target_exe)

            # Copy config directory if available
            config_src = self.bundle_dir / "config"
            if not config_src.exists():
                config_src = Path(__file__).parent.parent / "config"
            if config_src.exists():
                config_dst = target_dir / "config"
                config_dst.mkdir(exist_ok=True)
                for item in config_src.glob("*.json"):
                    shutil.copy2(item, config_dst / item.name)

            # Create Desktop Shortcut
            if self.desktop_shortcut_var.get():
                self.status_lbl.config(text="Creating Desktop shortcut...")
                self.root.update()
                desktop_dir = Path.home() / "Desktop"
                self._create_shortcut(target_exe, desktop_dir / "Class Lock.lnk")

            # Create Start Menu Shortcut
            if self.startmenu_shortcut_var.get():
                self.status_lbl.config(text="Creating Start Menu shortcut...")
                self.root.update()
                appdata = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
                start_menu_dir = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs"
                self._create_shortcut(target_exe, start_menu_dir / "Class Lock.lnk")

            # Register in Windows Add/Remove Programs
            self._register_uninstaller(target_dir, target_exe)

            self.status_lbl.config(text="Installation Complete! ✓", fg="#3FB950")
            self.btn_install.config(text="FINISHED", bg="#2EA043", command=self.root.destroy)

            messagebox.showinfo("Success", f"Class Lock installed successfully to:\n{target_dir}", parent=self.root)

            # Launch application if option selected
            if self.launch_after_var.get():
                subprocess.Popen([str(target_exe)], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
                self.root.destroy()

        except Exception as e:
            messagebox.showerror("Installation Failed", f"Error during installation:\n{str(e)}", parent=self.root)
            self.status_lbl.config(text="Installation failed.", fg="#DA3633")


def main():
    root = tk.Tk()
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    app = ClassLockInstallerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

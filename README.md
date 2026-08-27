# Class Lock

> A lightweight, distraction-proof Windows desktop utility that locks your computer into a minimal study environment during online classes.

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue.svg)](https://github.com/ExplorerAC/class-lock)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Release](https://img.shields.io/badge/Release-v1.0.0-success.svg)](https://github.com/ExplorerAC/class-lock/releases)

---

## The Objective

During an online class or exam, lock your computer into a dedicated study environment where you can access **only one specified class website and the Windows Calculator**.

Class Lock is a personal productivity tool—not a permanent kiosk restriction or invasive enterprise software. You toggle it **ON before class** and **OFF after class**.

```text
Normal PC
   │
   ├── [ Click "START CLASS" ]
   ▼
CLASS MODE ACTIVE
   ├── Class Website        [ ALLOWED - Fullscreen / App Mode ]
   ├── Windows Calculator   [ ALLOWED - Quick Pop-up Access ]
   └── All Other Apps/Tabs  [ BLOCKED - Anti-Distraction Guardian ]
   │
   ├── [ Click "END CLASS" or Ctrl+Alt+End ]
   ▼
Normal PC (100% Restored)
```

---

## Features

* **Native Browser and Extensions Preserved**: Launches using your native Google Chrome or Microsoft Edge profile. All your browser extensions (ad blockers, dark mode, classroom plugins, password managers) and logged-in accounts work out of the box.
* **Zero Tab Switching and No New Tabs**: Uses app-window presentation that hides the top tab bar strip, while a hardware-level keyboard hook blocks `Ctrl+Tab`, `Ctrl+1..9`, `Ctrl+T`, `Ctrl+N`, `Ctrl+W`, and `Ctrl+Shift+N`.
* **Anti-Minimize and Focus Guardian**: Automatically keeps the study window maximized and immediately suppresses unauthorized applications that attempt to steal focus.
* **Calculator Always Available**: Windows Calculator is an explicit allowed exception. Launch or bring it to the front with one click.
* **Always-On-Top Floating Pill Bar**: A compact, sleek control bar sits at the top center of your screen with a live session timer, a Calculator quick launcher, and a prominent `END CLASS` button.
* **Emergency Escape Shortcut**: Press **`Ctrl + Alt + End`** (or **`Ctrl + Alt + X`**) anywhere at any time to immediately and safely terminate Class Mode and restore normal PC operation.
* **Portable Executable and Windows Installer**: Includes both a zero-install portable `.exe` and a complete Windows Setup Wizard (`ClassLock_Setup.exe`) that creates Desktop and Start Menu shortcuts with **zero administrator privileges required**.

---

## Download and Installation

### Option 1: One-Click Setup Installer (Recommended for Users)
1. Go to the [**GitHub Releases**](https://github.com/ExplorerAC/class-lock/releases) page.
2. Download **`ClassLock_Setup.exe`**.
3. Run the installer (No Python installation required).
4. Launch **Class Lock** from your Desktop or Start Menu.

### Option 2: Portable Executable (No Install Required)
1. Download **`ClassLock.exe`** from [Releases](https://github.com/ExplorerAC/class-lock/releases).
2. Double-click to run immediately without installing.

### Option 3: Run from Source (Developers)
```powershell
# 1. Clone the repository
git clone https://github.com/ExplorerAC/class-lock.git
cd class-lock

# 2. Run with Python 3.10+
python src/main.py

# 3. (Optional) Build standalone executables
python build.py
```

---

## Shortcut Behavior Cheatsheet

| Shortcut | Action in Class Mode |
| :--- | :--- |
| **`Ctrl + Alt + End`** or **`Ctrl + Alt + X`** | **Emergency Exit** (Instantly terminates Class Mode & restores normal PC) |
| **Alphanumeric typing & Numbers** | **Allowed** (For notes, class chat, video controls, math) |
| **`Ctrl + Tab` / `Ctrl + Shift + Tab`** | **Blocked** (Prevents tab cycling) |
| **`Ctrl + 1` ... `Ctrl + 9`** | **Blocked** (Prevents switching to specific tabs) |
| **`Ctrl + T` / `Ctrl + N` / `Ctrl + Shift + N`** | **Blocked** (Prevents opening new tabs / windows) |
| **`Ctrl + W` / `Ctrl + Shift + T`** | **Blocked** (Prevents closing / reopening tabs) |
| **`Alt + Tab` / `Alt + Esc`** | **Blocked** (Prevents app switching) |
| **`Win` Key / `Win + D` / `Win + M`** | **Blocked** (Prevents opening Start Menu or showing Desktop) |

---

## Project Architecture

```text
class-lock/
├── .github/
│   └── workflows/
│       └── release.yml          # Automated CI/CD build & GitHub Releases
├── dist/
│   ├── ClassLock.exe            # Standalone Portable Executable (9.8 MB)
│   └── ClassLock_Setup.exe      # Windows Setup Wizard Installer (19.3 MB)
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point with exit handlers & DPI scaling
│   ├── ui.py                    # Tkinter UI (Standard mode & Floating Pill mode)
│   ├── class_mode.py            # Session state & lifecycle orchestrator
│   ├── browser_controller.py    # Native Chrome/Edge launcher & window closer
│   ├── window_controller.py     # Focus Guardian & Calculator manager
│   └── keyboard_hook.py         # Low-level Windows keyboard interceptor
├── installer/
│   ├── installer.py             # Setup wizard GUI source
│   ├── Installer.spec           # PyInstaller spec for setup installer
│   └── ClassLock_Setup.iss      # Inno Setup 6 script
├── config/
│   └── settings.json            # Persists user settings (last URL)
├── tests/
│   ├── test_url_validation.py   # Unit tests for URL validator
│   ├── test_browser_controller.py
│   └── test_keyboard_hook.py
├── build.py                     # Master build script (Builds portable + installer)
├── install.bat                  # One-click Windows batch installer
├── install.ps1                  # One-click PowerShell installer
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
└── README.md
```

---

## Running Automated Tests

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## Building Standalone Binaries

To build both `dist/ClassLock.exe` and `dist/ClassLock_Setup.exe` from source:

```powershell
pip install pyinstaller
python build.py
```

---

## License

This project is open-source software licensed under the [MIT License](LICENSE).

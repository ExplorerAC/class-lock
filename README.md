# Class Lock

A lightweight, personal productivity desktop utility for Windows designed to lock your computer into a focused study environment during online classes.

## Workflow

```text
Normal PC
   ↓
START CLASS
   ↓
Class Mode
   ├── Class Website (Allowed)
   └── Calculator (Allowed)
   ↓
END CLASS
   ↓
Normal PC
```

---

## Key Features

* **Minimal Desktop Interface**: Clear, distraction-free Tkinter UI.
* **Native Chrome / Edge Profile**: Loads your native browser profile so all your extensions (ad blockers, dark mode, password managers, classroom plugins), accounts, and logins work seamlessly.
* **Tab & Window Lockdown**: Removes the top tab strip to eliminate tab clicking, while hardware keyboard hooks suppress `Ctrl+Tab`, `Ctrl+1..9`, `Ctrl+T`, `Ctrl+N`, and `Ctrl+W`.
* **Anti-Minimize Guardian**: Automatically keeps the study window maximized and prevents switching away to distracting applications.
* **Calculator Allowed**: Quick access to the Windows Calculator via the top floating bar.
* **Always-On-Top Floating Pill Bar**: A compact, prominent top toolbar displays class time, a `🖩 Calc` button, and a large `🔴 END CLASS` button.
* **Emergency Escape Routes**: Press **`Ctrl + Alt + End`** (or **`Ctrl + Alt + X`**) anywhere at any time to instantly exit Class Mode safely.
* **Complete Installer**: Includes a dedicated Windows Setup Installer (`ClassLock_Setup.exe`) that installs to `%LOCALAPPDATA%\Programs\ClassLock`, adds Desktop and Start Menu shortcuts, and registers with Windows Add/Remove Programs.

---

## Installation & Distribution (For GitHub)

### Option 1: One-Click Windows Setup Installer (Recommended for Users)
Download `ClassLock_Setup.exe` from the GitHub Releases page and run it:
- Installs to `%LOCALAPPDATA%\Programs\ClassLock` (no administrator privileges needed).
- Automatically creates a Desktop shortcut (`Class Lock.lnk`).
- Automatically creates a Start Menu shortcut.
- Registers an uninstaller in Windows *Add or Remove Programs*.

### Option 2: Portable Executable (No Install Required)
Download and double-click `ClassLock.exe` to run immediately.

### Option 3: Run / Install from Source
```powershell
# Clone the repository
git clone https://github.com/your-username/ClassLock.git
cd ClassLock

# Run directly with Python
python src/main.py

# Or build both the portable exe and the setup installer:
python build.py
```

---

## GitHub Actions Automated Releases

A GitHub Actions workflow is included at [`.github/workflows/release.yml`](.github/workflows/release.yml).
Whenever you push a tag (e.g. `git tag v1.0.0 && git push origin v1.0.0`), GitHub Actions will automatically:
1. Run all unit tests.
2. Build `dist/ClassLock.exe` (Portable) and `dist/ClassLock_Setup.exe` (Installer).
3. Publish them as release assets on your GitHub repository.

---

## Project Structure

```text
ClassLock/
├── .github/
│   └── workflows/
│       └── release.yml          # GitHub Actions auto-release workflow
├── dist/
│   ├── ClassLock.exe            # Standalone Portable Executable (9.8 MB)
│   └── ClassLock_Setup.exe      # Windows Setup Wizard Installer (19.3 MB)
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point with signal & exit handling
│   ├── ui.py                    # Tkinter UI (Normal mode & Floating Pill mode)
│   ├── class_mode.py            # Lifecycle & state orchestrator
│   ├── browser_controller.py    # Native Chrome/Edge launcher
│   ├── window_controller.py     # Focus Guardian & Calculator manager
│   └── keyboard_hook.py         # Low-level Windows keyboard interceptor
├── installer/
│   ├── installer.py             # Setup wizard GUI source
│   ├── Installer.spec           # PyInstaller spec for setup executable
│   └── ClassLock_Setup.iss      # Optional Inno Setup script
├── config/
│   └── settings.json            # Persists user settings
├── tests/
│   ├── test_url_validation.py   # Unit tests
│   ├── test_browser_controller.py
│   └── test_keyboard_hook.py
├── build.py                     # Master build script (Builds portable + installer)
├── install.bat                  # One-click local install helper
├── ClassLock.spec               # PyInstaller spec for main app
├── requirements.txt
├── .gitignore
└── README.md
```

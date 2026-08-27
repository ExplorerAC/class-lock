@echo off
title Class Lock Installer
echo ===================================================
echo             Installing Class Lock
echo ===================================================
echo.

:: 1. If pre-built Setup Installer exists, launch it directly (Zero Python needed!)
if exist "dist\ClassLock_Setup.exe" (
    echo Launching Class Lock Setup Wizard...
    start "" "dist\ClassLock_Setup.exe"
    exit /b 0
)

:: 2. If standalone portable exe exists, install it directly using PowerShell
if exist "dist\ClassLock.exe" (
    echo Installing Class Lock to your user profile...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $dest = Join-Path $env:LOCALAPPDATA 'Programs\ClassLock'; New-Item -ItemType Directory -Force -Path $dest | Out-Null; Copy-Item 'dist\ClassLock.exe' -Destination $dest -Force; $ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Class Lock.lnk')); $s.TargetPath = (Join-Path $dest 'ClassLock.exe'); $s.Save(); $sm = $ws.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Programs')) 'Class Lock.lnk')); $sm.TargetPath = (Join-Path $dest 'ClassLock.exe'); $sm.Save(); Write-Host 'Class Lock has been installed successfully!' -ForegroundColor Green; Start-Process (Join-Path $dest 'ClassLock.exe') }"
    exit /b 0
)

:: 3. If running from source, check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python detected. Building standalone installer...
    python -m pip install pyinstaller
    python build.py
    if exist "dist\ClassLock_Setup.exe" (
        start "" "dist\ClassLock_Setup.exe"
    )
    exit /b 0
)

:: 4. If Python is NOT installed and no pre-built exe is found
echo [!] Python is not detected on your system.
echo.
echo If you downloaded the source code, you can either:
echo   1. Download the pre-built installer (ClassLock_Setup.exe) from GitHub Releases (Recommended - No Python required)
echo   2. Install Python from https://www.python.org or via Windows Terminal: winget install Python.Python.3.11
echo.
echo Would you like to install Python automatically now? (Y/N)
set /p USER_CHOICE="Choice: "
if /i "%USER_CHOICE%"=="Y" (
    echo Installing Python via Windows Package Manager (winget)...
    winget install --id Python.Python.3.11 -e --source winget
    echo.
    echo Please restart this installer after Python installation completes.
)

pause

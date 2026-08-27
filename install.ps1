# Class Lock PowerShell One-Click Installer
# Works with OR without Python installed!

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "             Class Lock Installer                 " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$distDir = Join-Path $PSScriptRoot "dist"
$setupExe = Join-Path $distDir "ClassLock_Setup.exe"
$portableExe = Join-Path $distDir "ClassLock.exe"
$installDest = Join-Path $env:LOCALAPPDATA "Programs\ClassLock"

# Case 1: If pre-built ClassLock_Setup.exe exists, launch it directly (Zero Python needed!)
if (Test-Path $setupExe) {
    Write-Host "Launching Class Lock Setup Wizard..." -ForegroundColor Green
    Start-Process $setupExe
    exit 0
}

# Case 2: If portable ClassLock.exe exists, install it immediately (Zero Python needed!)
if (Test-Path $portableExe) {
    Write-Host "Installing Class Lock to $installDest..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $installDest | Out-Null
    Copy-Item $portableExe -Destination $installDest -Force

    $wscript = New-Object -ComObject WScript.Shell
    
    # Desktop shortcut
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $desktopLnk = $wscript.CreateShortcut((Join-Path $desktopPath "Class Lock.lnk"))
    $desktopLnk.TargetPath = (Join-Path $installDest "ClassLock.exe")
    $desktopLnk.Save()

    # Start Menu shortcut
    $programsPath = [Environment]::GetFolderPath("Programs")
    $startMenuLnk = $wscript.CreateShortcut((Join-Path $programsPath "Class Lock.lnk"))
    $startMenuLnk.TargetPath = (Join-Path $installDest "ClassLock.exe")
    $startMenuLnk.Save()

    Write-Host "✓ Installation Complete! Shortcuts created on Desktop and Start Menu." -ForegroundColor Green
    Start-Process (Join-Path $installDest "ClassLock.exe")
    exit 0
}

# Case 3: If running from source and Python is available
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    Write-Host "Python detected ($($pythonCmd.Source)). Building executable..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    python (Join-Path $PSScriptRoot "build.py")
    if (Test-Path $setupExe) {
        Start-Process $setupExe
    }
    exit 0
}

# Case 4: No pre-built exe and Python is not installed
Write-Host "[!] Python is not installed on this system." -ForegroundColor Red
Write-Host ""
Write-Host "For regular users:" -ForegroundColor Yellow
Write-Host "  -> Download 'ClassLock_Setup.exe' from the GitHub Releases page (No Python required!)" -ForegroundColor White
Write-Host ""
Write-Host "Would you like to install Python 3.11 now via winget? (y/N)" -ForegroundColor Cyan
$choice = Read-Host
if ($choice -eq 'y' -or $choice -eq 'Y') {
    winget install --id Python.Python.3.11 -e --source winget
    Write-Host "Please restart this installer once Python is installed." -ForegroundColor Green
}

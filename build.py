"""Build script for packaging Class Lock into:
1. Standalone portable executable (dist/ClassLock.exe)
2. Standalone Windows installer (dist/ClassLock_Setup.exe)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_pyinstaller(spec_path: Path, cwd: Path):
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_path)
    ]
    print(f"\nExecuting: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"Build failed for {spec_path.name} with exit code {result.returncode}")
        sys.exit(result.returncode)


def build_all():
    root = Path(__file__).parent.resolve()
    dist_dir = root / "dist"
    installer_spec = root / "installer" / "Installer.spec"
    main_spec = root / "ClassLock.spec"

    print("=" * 65)
    print("STEP 1: Building Portable Executable (dist/ClassLock.exe)...")
    print("=" * 65)
    run_pyinstaller(main_spec, root)

    portable_exe = dist_dir / "ClassLock.exe"
    if not portable_exe.exists():
        print(f"Error: {portable_exe} not found after build.")
        sys.exit(1)
    print(f"[OK] Created: {portable_exe} ({portable_exe.stat().st_size / (1024 * 1024):.2f} MB)")

    print("\n" + "=" * 65)
    print("STEP 2: Building Windows Setup Installer (dist/ClassLock_Setup.exe)...")
    print("=" * 65)
    run_pyinstaller(installer_spec, root)

    installer_exe = dist_dir / "ClassLock_Setup.exe"
    if not installer_exe.exists():
        print(f"Error: {installer_exe} not found after build.")
        sys.exit(1)
    print(f"[OK] Created: {installer_exe} ({installer_exe.stat().st_size / (1024 * 1024):.2f} MB)")

    print("\n" + "=" * 65)
    print("ALL BUILDS COMPLETED SUCCESSFULLY!")
    print(f"1. Portable App: {portable_exe}")
    print(f"2. Windows Setup: {installer_exe}")
    print("=" * 65)


if __name__ == "__main__":
    build_all()

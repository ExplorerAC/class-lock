# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

block_cipher = None

installer_dir = os.path.abspath(SPECPATH)
project_dir = os.path.dirname(installer_dir)

# Bundle ClassLock.exe and config directly into the installer executable
dist_exe = os.path.join(project_dir, 'dist', 'ClassLock.exe')
config_dir = os.path.join(project_dir, 'config')

datas = []
if os.path.exists(dist_exe):
    datas.append((dist_exe, '.'))
if os.path.exists(config_dir):
    datas.append((config_dir, 'config'))

a = Analysis(
    [os.path.join(installer_dir, 'installer.py')],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'winreg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClassLock_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

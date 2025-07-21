# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

block_cipher = None

# Get the root directory (parent of config)
ROOT_DIR = Path(SPECPATH).parent

a = Analysis(
    [str(ROOT_DIR / 'main.py')],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        # Include the assets folder with icons
        (str(ROOT_DIR / 'assets' / '*.png'), 'assets'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'pystray._win32' if sys.platform == 'win32' else 'pystray._gtk' if sys.platform == 'linux' else 'pystray._darwin',
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
    name='OBS-VirtualCam-Tray-Controller' if sys.platform == 'win32' else 'obs-virtualcam-tray-controller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT_DIR / 'assets' / 'OBS-WebCam-Tray-Logo_Webcam_Turned_On.png') if (ROOT_DIR / 'assets' / 'OBS-WebCam-Tray-Logo_Webcam_Turned_On.png').exists() else None,
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='OBS VirtualCam Tray Controller.app',
        icon=str(ROOT_DIR / 'assets' / 'OBS-WebCam-Tray-Logo_Webcam_Turned_On.png'),
        bundle_identifier='com.burhanayan.obs-virtualcam-tray-controller',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSUIElement': '1',  # Hide from dock
        },
    )
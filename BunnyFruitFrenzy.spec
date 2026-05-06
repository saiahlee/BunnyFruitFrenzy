# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Bunny Fruit Frenzy.

Build with:
    pyinstaller BunnyFruitFrenzy.spec

Outputs:
    dist/BunnyFruitFrenzy        (Windows/Linux executable)
    dist/BunnyFruitFrenzy.app    (macOS app bundle)
"""

import sys

block_cipher = None

a = Analysis(
    ['bunny_fruit_frenzy.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BunnyFruitFrenzy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='BunnyFruitFrenzy.app',
        icon=None,
        bundle_identifier='com.saiah.bunnyfruitfrenzy',
        info_plist={
            'CFBundleName': 'Bunny Fruit Frenzy',
            'CFBundleDisplayName': 'Bunny Fruit Frenzy',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13',
            'NSHumanReadableCopyright': '© 2026 Saiah. MIT License.',
        },
    )

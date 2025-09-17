# -*- mode: python ; coding: utf-8 -*-

from __future__ import annotations

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

BASE_DIR = Path(__file__).parent.resolve()

# Pull in binaries/datas/hidden imports that PyQt6 needs on Windows.
pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all("PyQt6")

a = Analysis(
    ['src/main.py'],
    pathex=[str(BASE_DIR)],
    binaries=pyqt6_binaries,
    datas=pyqt6_datas,
    hiddenimports=pyqt6_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Cyclops',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Cyclops',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='Cyclops.app',
        icon=None,
        bundle_identifier=None,
    )

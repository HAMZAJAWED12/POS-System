# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Absolute base path of your project
project_root = os.path.abspath(".")

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        # .kv files
        ('views/home/home.kv', 'views/home'),
        ('views/products/products.kv', 'views/products'),
        ('views/cart/cart.kv', 'views/cart'),
        ('views/orderhistory/orderhistory.kv', 'views/orderhistory'),
        ('views/analytics/analytics.kv', 'views/analytics'),
        ('views/splash/splash.kv', 'views/splash'),

        # Database
        ('database/pos.db', 'database'),

    ],
    hiddenimports=collect_submodules('views'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='POSApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Change to True if you want to see console logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)

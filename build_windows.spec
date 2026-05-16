# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the base directory
basedir = os.path.abspath('.')

# Data files to include
data_files = [
    ('web/templates', 'web/templates'),
    ('web/static', 'web/static'),
    ('prompts', 'prompts'),
    ('.env.example', '.'),
]

# Hidden imports for Flask-SocketIO and other dynamic imports
hidden_imports = [
    'flask_socketio',
    'socketio',
    'engineio',
    'anthropic',
    'requests',
    'dotenv',
    'json',
    'uuid',
    'datetime',
    'threading',
    'logging',
    'sys',
    'os',
    'pathlib',
    'werkzeug.serving',
    'eventlet',
    'eventlet.wsgi',
    'eventlet.greenthread',
    'dns',
    'dns.resolver',
    'dns.rdatatype',
]

a = Analysis(
    ['web_app.py'],
    pathex=[basedir],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CongaAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='CongaAgent'
)
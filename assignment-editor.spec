# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Assignment Editor GUI

This creates a standalone executable for instructors to create and edit
assignments.xlsx files for the AutoGrader system.

Usage:
    pyinstaller assignment-editor.spec

Output:
    - dist/AssignmentEditor.exe (Windows)
    - dist/AssignmentEditor.app (Mac)
    - dist/AssignmentEditor (Linux)

Notes:
    - Bundles autograder.py and autograder-gui-app.py
    - These files are extracted when needed
    - Includes matplotlib for "Test Current Assignment" feature
"""

import sys

block_cipher = None

# Detect platform
is_mac = sys.platform == 'darwin'
is_windows = sys.platform == 'win32'

a = Analysis(
    ['assignment-editor-gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Bundle the autograder files - they'll be extracted when needed
        ('autograder.py', 'bundled_files'),
        ('autograder-gui-app.py', 'bundled_files'),
    ],
    hiddenimports=[
        # Data processing (required)
        'pandas',
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.utils',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        
        # NumPy (for test input parsing and autograder)
        'numpy',
        
        # Matplotlib (required for Test Current Assignment feature)
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.figure',
        'matplotlib.backends',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends.backend_tkagg',
        
        # Common scientific packages (included by default)
        'scipy',
        'scipy.optimize',
        'scipy.integrate',
        'scipy.linalg',
        'scipy.interpolate',
        'scipy.stats',
        'scipy.signal',
        'scipy.fft',
        'sympy',
        'sympy.core',
        'sympy.parsing',
        'sympy.printing',
        'sklearn',
        'sklearn.linear_model',
        'sklearn.model_selection',
        'sklearn.preprocessing',
        'sklearn.metrics',
        'sklearn.cluster',
        
        # PDF generation (needed for AutoGrader testing)
        'reportlab',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.platypus',
        'reportlab.lib.enums',
        
        # GUI
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        
        # Standard library
        'configparser',
        'json',
        'subprocess',
        'ast',
        'shutil',
        'base64',
        'threading',
        'smtplib',
        'email',
        'email.mime.text',
        'email.mime.multipart',
        'email.mime.base',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'test',
        'pdb',
        'doctest',
        'IPython',
        'jupyter',
        'pytest',
        'sphinx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if is_mac:
    # macOS: Use onedir mode for .app bundle (required for PyInstaller 6.0+)
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='AssignmentEditor',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,  # No console window
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=None,  # Add 'icon.icns' if you have one
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='AssignmentEditor',
    )
    
    app = BUNDLE(
        coll,
        name='AssignmentEditor.app',
        icon=None,  # Add 'icon.icns' if you have one
        bundle_identifier='com.autograder.assignment-editor',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleName': 'Assignment Editor',
            'CFBundleDisplayName': 'Assignment Editor',
            'NSHighResolutionCapable': True,
        },
    )
else:
    # Windows/Linux: Use onefile mode for single executable
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='AssignmentEditor',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,  # Use UPX compression to reduce file size
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # Set to True for debugging (shows console window)
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=None,  # Add 'icon.ico' (Windows) if you have one
    )

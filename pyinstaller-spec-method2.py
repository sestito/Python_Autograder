# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AutoGrader (Method 2 - Embedded Resources)

This configuration embeds config.ini and assignments.xlsx directly in the code
via the embedded_resources.py module. No external config files are needed.

Prerequisites:
    1. Run encode_resources.py to generate embedded_resources.py
    2. Ensure autograder.py and autograder_gui.py are present
    3. Run: pyinstaller autograder.spec

Output:
    - dist/AutoGrader.exe (Windows)
    - dist/AutoGrader.app (Mac)
    - dist/AutoGrader (Linux)
"""

block_cipher = None

a = Analysis(
    ['autograder_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # NO config.ini or assignments.xlsx here!
        # They are embedded in embedded_resources.py
        ('solutions', 'solutions'),  # Include solutions folder
    ],
    hiddenimports=[
        # Core modules
        'autograder',
        'embedded_resources',  # Our embedded config and Excel
        
        # Data processing
        'pandas',
        'openpyxl',
        'numpy',
        
        # Plotting
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_tkagg',
        
        # PDF generation
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
        'smtplib',
        'email',
        'email.mime.text',
        'email.mime.multipart',
        'email.mime.base',
        'socket',
        'getpass',
        'base64',
        'tempfile',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'test',
        'unittest',
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AutoGrader',
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
    icon=None  # Add 'icon.ico' (Windows) or 'icon.icns' (Mac) if you have one
)

# For Mac app bundle
app = BUNDLE(
    exe,
    name='AutoGrader.app',
    icon=None,  # Add 'icon.icns' if you have one
    bundle_identifier='com.university.autograder',
)
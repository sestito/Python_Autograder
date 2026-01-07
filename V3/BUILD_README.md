# Building Distributable Executables

This guide explains how to create standalone executables for the AutoGrader system.

## Overview

There are **two applications** you can build:

| Application | Who Uses It | Purpose |
|------------|-------------|---------|
| **Assignment Editor** | Instructors | Create and edit assignments.xlsx files with test definitions |
| **AutoGrader** | Students | Check their code against the assignment tests |

---

## Quick Start

### Building the Assignment Editor (for instructors)

The Assignment Editor bundles `autograder.py` and `autograder-gui-app.py` inside the executable. The encoding functionality is built directly into the editor.

```bash
# 1. Install dependencies
pip install pyinstaller pandas openpyxl numpy

# 2. Make sure all required files are in the same directory:
#    - assignment-editor-gui.py
#    - assignment-editor.spec
#    - autograder.py
#    - autograder-gui-app.py

# 3. Build the executable
pyinstaller --clean assignment-editor.spec

# 4. Find the executable in:
#    Windows: dist/AssignmentEditor.exe
#    Mac:     dist/AssignmentEditor.app
#    Linux:   dist/AssignmentEditor
```

### Building the AutoGrader (for students)

Use the Assignment Editor's built-in build feature:

```bash
# In Assignment Editor:
# 1. Create/edit assignments.xlsx
# 2. Click "Edit Config" to set up email settings (optional)
# 3. Click "Encode Resources" to embed config and assignments
# 4. Click "Build Executable"

# The executable will be in the 'dist' folder
```

---

## How It Works

### No External Files Created

The Assignment Editor is designed to be clean:

- **Encode Resources**: The encoding functionality is built directly into the editor - no `encode_resources.py` file is created
- **Launch AutoGrader / Build**: Files are extracted to a **temporary directory** and cleaned up automatically
- **Test Assignment**: Uses bundled `autograder.py` from temp directory

### Bundled Files

The executable contains these files bundled inside:
- `autograder.py` - Core grading logic  
- `autograder-gui-app.py` - Student GUI application

These are extracted to a temporary directory only when needed and cleaned up when the editor closes.

---

## Detailed Workflow

### Step 1: Set Up Your Environment

```bash
# Create a virtual environment (recommended)
python -m venv autograder_env
source autograder_env/bin/activate  # Linux/Mac
# or
autograder_env\Scripts\activate  # Windows

# Install all dependencies
pip install pyinstaller pandas openpyxl numpy matplotlib reportlab
```

### Step 2: Build Assignment Editor

```bash
pyinstaller --clean assignment-editor.spec
```

Distribute `dist/AssignmentEditor.exe` (or .app) to instructors.

### Step 3: Create Assignments

Use the Assignment Editor to:
1. Create a new assignments.xlsx file
2. Add assignments (each becomes an Excel sheet)
3. Add tests to each assignment
4. Save the file

### Step 4: Configure Email (Optional)

Click "Edit Config" in the Assignment Editor to set up SMTP settings for emailing results.

### Step 5: Build AutoGrader for Students

In the Assignment Editor:
1. Click "Encode Resources" - embeds config.ini and assignments.xlsx
2. Click "Build Executable" - creates the student application
3. Files are automatically cleaned up after build

### Step 6: Distribute

Give students:
- `dist/AutoGrader.exe` (Windows) or `dist/AutoGrader.app` (Mac)
- Any solution files referenced in your tests (in a `solutions/` folder)

---

## File Reference

| File | Purpose |
|------|---------|
| `assignment-editor-gui.py` | Source code for Assignment Editor |
| `assignment-editor.spec` | PyInstaller spec for Assignment Editor |
| `autograder-gui-app.py` | Source code for student GUI (bundled in editor) |
| `autograder.py` | Core autograding logic (bundled in editor) |
| `config.ini` | Email and settings configuration |
| `assignments.xlsx` | Assignment definitions (created by editor) |
| `embedded_resources.py` | Generated file with embedded config/assignments |
| `autograder_build.spec` | PyInstaller spec for AutoGrader (auto-generated) |

---

## Troubleshooting

### "Python interpreter not found"

The Assignment Editor needs Python installed on the system to:
- Launch the AutoGrader for testing
- Build executables with PyInstaller

Make sure Python is in your system PATH.

### "ModuleNotFoundError" when running executable

Add the missing module to `hiddenimports` in the .spec file and rebuild.

### Executable is very large

This is normal. PyInstaller bundles Python and all dependencies. Typical sizes:
- Assignment Editor: ~50-80 MB
- AutoGrader: ~80-150 MB (includes matplotlib, numpy)

### macOS: "App is damaged and can't be opened"

```bash
xattr -cr dist/AssignmentEditor.app
```

Or go to System Preferences → Security & Privacy → Allow.

### Windows: SmartScreen warning

Click "More info" → "Run anyway". This happens with unsigned executables.

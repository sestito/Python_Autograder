# Python AutoGrader

A system for creating and grading Python assignments. Instructors use the **Assignment Editor** to create tests, then build an **AutoGrader** executable for students.

---

## Requirements

### Python Version
- **Python 3.8 or higher**

### Required Packages

```bash
pip install pandas openpyxl numpy matplotlib reportlab pyinstaller
```

### Optional Packages (install as needed)

```bash
# Scientific computing (recommended)
pip install scipy sympy scikit-learn

# Other optional packages
pip install Pillow seaborn statsmodels requests opencv-python networkx nltk plotly
```

---

## Quick Start

### 1. Run the Assignment Editor

**Windows:**
```cmd
python assignment-editor-gui.py
```

**Linux/macOS:**
```bash
python3 assignment-editor-gui.py
```

Or, you can use the provided launcher scripts:
- **Windows:** Double-click `run-assignment-editor.bat`
- **Linux/macOS:** Run `./run-assignment-editor.sh`

### 2. Create Assignments

1. Click **New** to create an assignment
2. Add tests using the **Add Test** button
3. Click **Save** to save to `assignments.xlsx`

### 3. Build the AutoGrader (for Students)

From within the Assignment Editor:
1. Click **Encode Resources** to embed your assignments
2. Click **Build Executable**
3. Select the packages your assignments need
4. Click **OK** to build

Output: `dist/AutoGrader.exe` (Windows), `dist/AutoGrader.app` (Mac), or `dist/AutoGrader` (Linux)

### 4. Distribute to Students

Give students:
- The AutoGrader executable from the `dist/` folder
- Any solution files (if using file comparison tests)

---

## Generate Example Files (Optional)

To create example assignments and sample student submissions:

```bash
python setup-examples.py
```

Or use the provided scripts:
- **Windows:** Double-click `setup-examples.bat`
- **Linux/macOS:** Run `./setup-examples.sh`

---

## Building the Assignment Editor Executable (Optional)

If you want to distribute the Assignment Editor as a standalone executable:

**Windows:** 
```cmd
build-assignment-editor.bat
```

**Linux/macOS:**
```bash
chmod +x build-assignment-editor.sh
./build-assignment-editor.sh
```

Output: `dist/AssignmentEditor.exe` (Windows), `dist/AssignmentEditor.app` (Mac), or `dist/AssignmentEditor` (Linux)

---

## AutoGrader Packages

When building the AutoGrader, you can select which packages to include. Packages must be installed on your computer to be available.

| Package | Purpose |
|---------|---------|
| **Core (Always Included)** ||
| `numpy` | Numerical computing |
| `pandas` | Data manipulation |
| `matplotlib` | Plotting |
| `openpyxl` | Excel file support |
| `reportlab` | PDF generation |
| **Scientific (Default)** ||
| `scipy` | Scientific computing |
| `sympy` | Symbolic mathematics |
| `scikit-learn` | Machine learning |
| **Optional** ||
| `Pillow` | Image processing |
| `seaborn` | Statistical visualization |
| `statsmodels` | Statistical models |
| `requests` | HTTP requests |
| `opencv-python` | Computer vision |
| `networkx` | Graph/network analysis |
| `nltk` | Natural language processing |
| `plotly` | Interactive plots |

---

## File Reference

| File | Purpose |
|------|---------|
| **Core Application** ||
| `assignment-editor-gui.py` | Assignment Editor (run this) |
| `autograder.py` | Core grading logic |
| `autograder-gui-app.py` | Student AutoGrader GUI |
| **Launcher Scripts** ||
| `run-assignment-editor.bat/.sh` | Run editor from Python |
| **Build Scripts (Optional)** ||
| `build-assignment-editor.bat/.sh` | Build editor executable |
| `assignment-editor.spec` | PyInstaller spec for editor |
| `autograder.spec` | PyInstaller spec for AutoGrader |
| **Examples** ||
| `setup-examples.py` | Generate example assignments |
| `setup-examples.bat/.sh` | Run setup-examples.py |
| **Configuration** ||
| `config.ini` | Email/SMTP settings |

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'xxx'"**  
Install the missing package: `pip install xxx`

**Package shows as "not installed" in Packages dialog**  
Use the **Browse...** button to select a different Python executable.

**macOS: "App is damaged"**  
Run: `xattr -cr dist/AutoGrader.app`

**Windows: SmartScreen warning**  
Click "More info" → "Run anyway"

**Executable is large (100-200+ MB)**  
Normal — PyInstaller bundles Python and all dependencies.
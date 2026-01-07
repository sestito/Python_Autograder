# Python AutoGrader

A system for creating and grading Python assignments. Instructors use the **Assignment Editor** to create tests, then build an **AutoGrader** executable for students.

---

## Quick Start

### 1. Build the Assignment Editor

**Windows:** Double-click `build-assignment-editor.bat`

**Linux/macOS:**
```bash
chmod +x build-assignment-editor.sh
./build-assignment-editor.sh
```

Output: `dist/AssignmentEditor.exe` (Windows), `dist/AssignmentEditor.app` (Mac), or `dist/AssignmentEditor` (Linux)

### 2. Generate Example Files (Optional)

**Windows:** Double-click `setup-examples.bat`

**Linux/macOS:**
```bash
chmod +x setup-examples.sh
./setup-examples.sh
```

This creates `assignments.xlsx` and sample student submissions for testing.

### 3. Build the AutoGrader (for Students)

From within the Assignment Editor:
1. Create or open `assignments.xlsx`
2. Click **Encode Resources** to embed the assignments
3. Click **Build Executable** — a package selection dialog will appear
4. Select the packages your assignments need, then click **Build with Selected Packages**

Output: `dist/AutoGrader.exe` (or .app)

---

## Included Packages

The AutoGrader includes these Python packages by default:

| Package | Purpose |
|---------|---------|
| **Core (Always Included)** ||
| `numpy` | Numerical computing |
| `pandas` | Data manipulation |
| `matplotlib` | Plotting |
| `openpyxl` | Excel file support |
| `reportlab` | PDF generation |
| **Scientific (Default, Optional)** ||
| `scipy` | Scientific computing |
| `sympy` | Symbolic mathematics |
| `scikit-learn` | Machine learning |
| **Other Optional Packages** ||
| `Pillow` | Image processing |
| `seaborn` | Statistical visualization |
| `statsmodels` | Statistical models |
| `requests` | HTTP requests |
| `opencv-python` | Computer vision |
| `networkx` | Graph/network analysis |
| `nltk` | Natural language processing |
| `plotly` | Interactive plots |

### Need Additional Packages?

If your assignments require packages not in the list above:

1. **Run Assignment Editor from Python source** instead of the executable:
   - **Windows:** Double-click `run-assignment-editor.bat`
   - **Linux/macOS:** Run `./run-assignment-editor.sh`

2. Install the additional packages on your computer:
   ```bash
   pip install <package-name>
   ```

3. When building the AutoGrader, add the package names in the **Additional Custom Packages** field.

---

## File Reference

| File | Purpose |
|------|---------|
| **Core Application** ||
| `assignment-editor-gui.py` | Assignment Editor source code |
| `autograder.py` | Core grading logic |
| `autograder-gui-app.py` | Student AutoGrader GUI source code |
| **Build Files** ||
| `assignment-editor.spec` | PyInstaller spec for Assignment Editor |
| `autograder.spec` | PyInstaller spec for AutoGrader |
| `build-assignment-editor.bat` | Windows build script |
| `build-assignment-editor.sh` | Linux/macOS build script |
| `build_executables.py` | Python build script (alternative) |
| `encode_resources.py` | Embeds config and assignments into Python module |
| **Launcher Scripts** ||
| `run-assignment-editor.bat` | Run editor from Python (Windows) — use for custom packages |
| `run-assignment-editor.sh` | Run editor from Python (Linux/macOS) — use for custom packages |
| **Examples** ||
| `setup-examples.bat` | Windows script to generate example files |
| `setup-examples.sh` | Linux/macOS script to generate example files |
| `setup-examples.py` | Python script that creates example assignments |
| **Configuration** ||
| `config.ini` | Email/SMTP settings |
| `assignment_editor_settings.json` | Editor preferences (including selected packages) |
| **Generated Files** ||
| `assignments.xlsx` | Assignment definitions (created by editor) |
| `embedded_resources.py` | Generated file with embedded config/assignments |
| `autograder_build.spec` | Auto-generated spec file from editor |

---

## Troubleshooting

**"Python interpreter not found"** — Ensure Python is installed and in your system PATH.

**"ModuleNotFoundError" when running executable** — The package isn't included in the build. Either add it via the package selection dialog (if running from source) or add it to `hiddenimports` in the .spec file and rebuild.

**macOS: "App is damaged"** — Run: `xattr -cr dist/AssignmentEditor.app`

**Windows: SmartScreen warning** — Click "More info" → "Run anyway" (expected for unsigned executables).

**Executable is large (100-200+ MB)** — Normal. PyInstaller bundles Python and all dependencies including scipy/scikit-learn.
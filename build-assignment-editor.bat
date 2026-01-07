@echo off
REM ============================================================
REM Build Script for Assignment Editor GUI (Windows)
REM ============================================================
REM This script builds the Assignment Editor executable using PyInstaller
REM 
REM Requirements:
REM   - Python 3.8+ installed and in PATH
REM   - Required files in same directory:
REM     - assignment-editor-gui.py
REM     - assignment-editor.spec
REM     - autograder.py
REM     - autograder-gui-app.py
REM ============================================================

echo.
echo ============================================================
echo   Assignment Editor Build Script
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo [1/5] Python found:
python --version
echo.

REM Check for required files
echo [2/5] Checking required files...

if not exist "assignment-editor-gui.py" (
    echo ERROR: assignment-editor-gui.py not found!
    pause
    exit /b 1
)
echo       - assignment-editor-gui.py [OK]

if not exist "assignment-editor.spec" (
    echo ERROR: assignment-editor.spec not found!
    pause
    exit /b 1
)
echo       - assignment-editor.spec [OK]

if not exist "autograder.py" (
    echo ERROR: autograder.py not found!
    pause
    exit /b 1
)
echo       - autograder.py [OK]

if not exist "autograder-gui-app.py" (
    echo ERROR: autograder-gui-app.py not found!
    pause
    exit /b 1
)
echo       - autograder-gui-app.py [OK]

echo.

REM Install/upgrade required packages
echo [3/5] Installing/upgrading required packages...
pip install --upgrade pyinstaller pandas openpyxl numpy matplotlib >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some packages may not have installed correctly
    echo Attempting to continue anyway...
) else (
    echo       Packages installed successfully
)
echo.

REM Clean previous build
echo [4/5] Cleaning previous build files...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist\AssignmentEditor.exe" del /f /q "dist\AssignmentEditor.exe" 2>nul
echo       Done
echo.

REM Run PyInstaller
echo [5/5] Building executable with PyInstaller...
echo       This may take a few minutes...
echo.
echo ============================================================
pyinstaller --clean --noconfirm assignment-editor.spec
echo ============================================================
echo.

REM Check if build succeeded
if exist "dist\AssignmentEditor.exe" (
    echo.
    echo ============================================================
    echo   BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    echo   Output: dist\AssignmentEditor.exe
    echo.
    for %%A in ("dist\AssignmentEditor.exe") do echo   Size: %%~zA bytes
    echo.
    echo   You can now distribute AssignmentEditor.exe to instructors.
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo   BUILD FAILED!
    echo ============================================================
    echo.
    echo   Check the output above for error messages.
    echo   Common issues:
    echo     - Missing Python packages
    echo     - Antivirus blocking PyInstaller
    echo     - Insufficient disk space
    echo ============================================================
)

echo.
pause

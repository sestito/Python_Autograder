@echo off
REM ============================================================
REM Run Assignment Editor from Python Source
REM ============================================================
REM Use this script if you need to include additional Python
REM packages beyond the defaults (scipy, sympy, sklearn, etc.)
REM 
REM Prerequisites:
REM   - Python 3.8+ installed
REM   - Required packages: pip install pandas openpyxl numpy matplotlib
REM   - Any additional packages you want to include in the build
REM ============================================================

echo.
echo ============================================================
echo   Assignment Editor (Python Source)
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.8+ first
        pause
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

REM Check if assignment-editor-gui.py exists
if not exist "assignment-editor-gui.py" (
    echo ERROR: assignment-editor-gui.py not found!
    echo Make sure this script is in the same folder as the source files.
    pause
    exit /b 1
)

echo Starting Assignment Editor...
echo.

%PYTHON_CMD% assignment-editor-gui.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo   ERROR: Assignment Editor failed to start
    echo ============================================================
    echo.
    echo Common issues:
    echo   - Missing packages: pip install pandas openpyxl numpy matplotlib
    echo   - Python not in PATH
    echo.
    pause
)

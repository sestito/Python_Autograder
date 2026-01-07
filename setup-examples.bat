@echo off
REM ============================================================
REM Setup Example Files for AutoGrader (Windows)
REM ============================================================
REM This script creates example assignments, student submissions,
REM and solution files for testing the AutoGrader system.
REM ============================================================

echo.
echo ============================================================
echo   AutoGrader Example Files Setup
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

echo Found Python:
python --version
echo.

REM Check for required packages and install if missing
echo Checking required packages...
pip show pandas >nul 2>&1
if errorlevel 1 (
    echo Installing pandas...
    pip install pandas --quiet
)

pip show openpyxl >nul 2>&1
if errorlevel 1 (
    echo Installing openpyxl...
    pip install openpyxl --quiet
)

echo.
echo Running setup script...
echo.

REM Run the Python script
python setup-examples.py

if errorlevel 1 (
    echo.
    echo ERROR: Setup failed!
    pause
    exit /b 1
)

echo.
pause

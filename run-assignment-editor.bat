@echo off
setlocal EnableDelayedExpansion
REM ============================================================
REM Run Assignment Editor from Python Source
REM ============================================================
REM Use this script if you need to include additional Python
REM packages beyond the defaults (scipy, sympy, sklearn, etc.)
REM 
REM Prerequisites:
REM   - Python 3.8+ installed
REM   - Required packages: pip install pandas openpyxl numpy matplotlib reportlab
REM   - PyInstaller (optional): Required only for building executables
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
    set PIP_CMD=pip3
) else (
    set PYTHON_CMD=python
    set PIP_CMD=pip
)

REM Check if assignment-editor-gui.py exists
if not exist "assignment-editor-gui.py" (
    echo ERROR: assignment-editor-gui.py not found!
    echo Make sure this script is in the same folder as the source files.
    pause
    exit /b 1
)

REM Check for core packages
echo Checking for required packages...
%PYTHON_CMD% -c "import pandas, openpyxl, numpy, matplotlib, reportlab" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo   Some required packages are missing!
    echo ============================================================
    echo.
    echo The following packages are required:
    echo   pandas, openpyxl, numpy, matplotlib, reportlab
    echo.
    set /p INSTALL_NOW="Would you like to install them now? [Y/n]: "
    if /i "!INSTALL_NOW!"=="" set INSTALL_NOW=Y
    if /i "!INSTALL_NOW!"=="Y" (
        echo.
        echo Installing core packages...
        %PIP_CMD% install pandas openpyxl numpy matplotlib reportlab
        if !errorlevel! neq 0 (
            echo.
            echo WARNING: Some packages may not have installed correctly.
            echo.
            set /p CONTINUE="Continue anyway? [y/N]: "
            if /i not "!CONTINUE!"=="Y" (
                echo Exiting.
                pause
                exit /b 1
            )
        ) else (
            echo.
            echo Packages installed successfully!
            echo.
        )
    ) else (
        echo.
        echo Skipping package installation.
        echo Some features may not work correctly.
        echo.
    )
)

REM Check for PyInstaller (optional - only needed for building)
%PYTHON_CMD% -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo   NOTE: PyInstaller is not installed
    echo ============================================================
    echo.
    echo PyInstaller is required to build the Student AutoGrader executable.
    echo You can still use the Assignment Editor, but you will not be able
    echo to build executables until PyInstaller is installed.
    echo.
    set /p INSTALL_PYINSTALLER="Would you like to install PyInstaller now? [y/N]: "
    if /i "!INSTALL_PYINSTALLER!"=="Y" (
        echo.
        echo Installing PyInstaller...
        %PIP_CMD% install pyinstaller
        if !errorlevel! neq 0 (
            echo.
            echo WARNING: PyInstaller may not have installed correctly.
            echo You can install it later with: %PIP_CMD% install pyinstaller
            echo.
        ) else (
            echo.
            echo PyInstaller installed successfully!
            echo.
        )
    ) else (
        echo.
        echo Continuing without PyInstaller...
        echo To install later: %PIP_CMD% install pyinstaller
        echo.
    )
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
    echo   - Missing packages: %PIP_CMD% install pandas openpyxl numpy matplotlib reportlab
    echo   - Python not in PATH
    echo.
    pause
)
endlocal
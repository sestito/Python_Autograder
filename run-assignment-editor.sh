#!/bin/bash
# ============================================================
# Run Assignment Editor from Python Source
# ============================================================
# Use this script if you need to include additional Python
# packages beyond the defaults (scipy, sympy, sklearn, etc.)
# 
# Prerequisites:
#   - Python 3.8+ installed
#   - Required packages: pip install pandas openpyxl numpy matplotlib reportlab
#   - PyInstaller (optional): Required only for building executables
# ============================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================================"
echo "  Assignment Editor (Python Source)"
echo "============================================================"
echo ""

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    echo -e "${RED}ERROR: Python is not installed or not in PATH${NC}"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo -e "Using: ${BLUE}$($PYTHON_CMD --version)${NC}"
echo ""

# Check if assignment-editor-gui.py exists
if [ ! -f "assignment-editor-gui.py" ]; then
    echo -e "${RED}ERROR: assignment-editor-gui.py not found!${NC}"
    echo "Make sure this script is in the same folder as the source files."
    exit 1
fi

# Check for core packages
echo "Checking for required packages..."
$PYTHON_CMD -c "import pandas, openpyxl, numpy, matplotlib, reportlab" 2>/dev/null

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}============================================================${NC}"
    echo -e "${YELLOW}  Some required packages are missing!${NC}"
    echo -e "${YELLOW}============================================================${NC}"
    echo ""
    echo "The following packages are required:"
    echo "  pandas, openpyxl, numpy, matplotlib, reportlab"
    echo ""
    read -p "Would you like to install them now? [Y/n]: " INSTALL_NOW
    INSTALL_NOW=${INSTALL_NOW:-Y}
    
    if [[ "$INSTALL_NOW" =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}Installing core packages...${NC}"
        $PIP_CMD install pandas openpyxl numpy matplotlib reportlab
        
        if [ $? -ne 0 ]; then
            echo ""
            echo -e "${YELLOW}WARNING: Some packages may not have installed correctly.${NC}"
            echo ""
            read -p "Continue anyway? [y/N]: " CONTINUE
            if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
                echo "Exiting."
                exit 1
            fi
        else
            echo ""
            echo -e "${GREEN}Packages installed successfully!${NC}"
            echo ""
        fi
    else
        echo ""
        echo "Skipping package installation."
        echo "Some features may not work correctly."
        echo ""
    fi
fi

# Check for PyInstaller (optional - only needed for building)
$PYTHON_CMD -c "import PyInstaller" 2>/dev/null

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}============================================================${NC}"
    echo -e "${YELLOW}  NOTE: PyInstaller is not installed${NC}"
    echo -e "${YELLOW}============================================================${NC}"
    echo ""
    echo "PyInstaller is required to build the Student AutoGrader executable."
    echo "You can still use the Assignment Editor, but you will not be able"
    echo "to build executables until PyInstaller is installed."
    echo ""
    read -p "Would you like to install PyInstaller now? [y/N]: " INSTALL_PYINSTALLER
    
    if [[ "$INSTALL_PYINSTALLER" =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}Installing PyInstaller...${NC}"
        $PIP_CMD install pyinstaller
        
        if [ $? -ne 0 ]; then
            echo ""
            echo -e "${YELLOW}WARNING: PyInstaller may not have installed correctly.${NC}"
            echo -e "You can install it later with: ${BLUE}$PIP_CMD install pyinstaller${NC}"
            echo ""
        else
            echo ""
            echo -e "${GREEN}PyInstaller installed successfully!${NC}"
            echo ""
        fi
    else
        echo ""
        echo "Continuing without PyInstaller..."
        echo -e "To install later: ${BLUE}$PIP_CMD install pyinstaller${NC}"
        echo ""
    fi
fi

echo "Starting Assignment Editor..."
echo ""

$PYTHON_CMD assignment-editor-gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}============================================================${NC}"
    echo -e "${RED}  ERROR: Assignment Editor failed to start${NC}"
    echo -e "${RED}============================================================${NC}"
    echo ""
    echo "Common issues:"
    echo -e "  - Missing packages: ${BLUE}$PIP_CMD install pandas openpyxl numpy matplotlib reportlab${NC}"
    echo "  - Python not in PATH"
    echo ""
fi

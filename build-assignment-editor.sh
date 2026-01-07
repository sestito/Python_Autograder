#!/bin/bash
# ============================================================
# Build Script for Assignment Editor GUI (Linux/macOS)
# ============================================================
# This script builds the Assignment Editor executable using PyInstaller
# 
# Requirements:
#   - Python 3.8+ installed
#   - Required files in same directory:
#     - assignment-editor-gui.py
#     - assignment-editor.spec
#     - autograder.py
#     - autograder-gui-app.py
#
# Usage:
#   chmod +x build-assignment-editor.sh
#   ./build-assignment-editor.sh
# ============================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================================"
echo "  Assignment Editor Build Script"
echo "============================================================"
echo ""

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    OUTPUT_NAME="AssignmentEditor"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    OUTPUT_NAME="AssignmentEditor.app"
else
    OS="other"
    OUTPUT_NAME="AssignmentEditor"
fi

echo -e "${BLUE}Detected OS:${NC} $OS"
echo ""

# Check if Python is available
echo -e "${BLUE}[1/5] Checking Python...${NC}"
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

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "       ${GREEN}$PYTHON_VERSION${NC}"
echo ""

# Check for required files
echo -e "${BLUE}[2/5] Checking required files...${NC}"

check_file() {
    if [ -f "$1" ]; then
        echo -e "       - $1 ${GREEN}[OK]${NC}"
        return 0
    else
        echo -e "       - $1 ${RED}[MISSING]${NC}"
        return 1
    fi
}

MISSING=0
check_file "assignment-editor-gui.py" || MISSING=1
check_file "assignment-editor.spec" || MISSING=1
check_file "autograder.py" || MISSING=1
check_file "autograder-gui-app.py" || MISSING=1

if [ $MISSING -eq 1 ]; then
    echo ""
    echo -e "${RED}ERROR: Required files are missing!${NC}"
    echo "Make sure all files are in the same directory as this script."
    exit 1
fi
echo ""

# Install/upgrade required packages
echo -e "${BLUE}[3/5] Installing/upgrading required packages...${NC}"
$PIP_CMD install --upgrade pyinstaller pandas openpyxl numpy matplotlib --quiet 2>/dev/null || {
    echo -e "${YELLOW}WARNING: Some packages may not have installed correctly${NC}"
    echo "Attempting to continue anyway..."
}
echo -e "       ${GREEN}Packages installed successfully${NC}"
echo ""

# Clean previous build
echo -e "${BLUE}[4/5] Cleaning previous build files...${NC}"
rm -rf build/ 2>/dev/null || true
rm -rf "dist/$OUTPUT_NAME" 2>/dev/null || true
rm -rf dist/AssignmentEditor/ 2>/dev/null || true
echo -e "       ${GREEN}Done${NC}"
echo ""

# Run PyInstaller
echo -e "${BLUE}[5/5] Building executable with PyInstaller...${NC}"
echo "       This may take a few minutes..."
echo ""
echo "============================================================"

pyinstaller --clean --noconfirm assignment-editor.spec

echo "============================================================"
echo ""

# Check if build succeeded
if [ "$OS" == "macos" ]; then
    OUTPUT_PATH="dist/AssignmentEditor.app"
else
    OUTPUT_PATH="dist/AssignmentEditor"
fi

if [ -e "$OUTPUT_PATH" ]; then
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}  BUILD SUCCESSFUL!${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo -e "  Output: ${BLUE}$OUTPUT_PATH${NC}"
    echo ""
    
    if [ -f "$OUTPUT_PATH" ]; then
        SIZE=$(du -h "$OUTPUT_PATH" | cut -f1)
        echo -e "  Size: $SIZE"
    elif [ -d "$OUTPUT_PATH" ]; then
        SIZE=$(du -sh "$OUTPUT_PATH" | cut -f1)
        echo -e "  Size: $SIZE"
    fi
    
    echo ""
    
    if [ "$OS" == "macos" ]; then
        echo "  To run: open dist/AssignmentEditor.app"
        echo ""
        echo "  Note: You may need to allow the app in"
        echo "        System Preferences > Security & Privacy"
        echo ""
        echo "  If you get 'damaged' error, run:"
        echo "        xattr -cr dist/AssignmentEditor.app"
    else
        echo "  To run: ./dist/AssignmentEditor"
        echo ""
        # Make executable
        chmod +x "$OUTPUT_PATH" 2>/dev/null || true
    fi
    
    echo ""
    echo "  You can now distribute this to instructors."
    echo -e "${GREEN}============================================================${NC}"
else
    echo ""
    echo -e "${RED}============================================================${NC}"
    echo -e "${RED}  BUILD FAILED!${NC}"
    echo -e "${RED}============================================================${NC}"
    echo ""
    echo "  Check the output above for error messages."
    echo ""
    echo "  Common issues:"
    echo "    - Missing Python packages"
    echo "    - Missing system dependencies (tkinter)"
    echo "    - Insufficient disk space"
    echo ""
    echo "  On Ubuntu/Debian, you may need:"
    echo "    sudo apt-get install python3-tk"
    echo ""
    echo "  On macOS, tkinter should be included with Python."
    echo -e "${RED}============================================================${NC}"
    exit 1
fi

echo ""

#!/bin/bash
# ============================================================
# Setup Example Files for AutoGrader (Linux/macOS)
# ============================================================
# This script creates example assignments, student submissions,
# and solution files for testing the AutoGrader system.
#
# Usage:
#   chmod +x setup-examples.sh
#   ./setup-examples.sh
# ============================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================================"
echo "  AutoGrader Example Files Setup"
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

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "Found Python: ${GREEN}$PYTHON_VERSION${NC}"
echo ""

# Check for required packages and install if missing
echo "Checking required packages..."

$PYTHON_CMD -c "import pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing pandas..."
    $PIP_CMD install pandas --quiet 2>/dev/null
fi

$PYTHON_CMD -c "import openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing openpyxl..."
    $PIP_CMD install openpyxl --quiet 2>/dev/null
fi

echo ""
echo "Running setup script..."
echo ""

# Run the Python script
$PYTHON_CMD setup-examples.py

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}ERROR: Setup failed!${NC}"
    exit 1
fi

echo ""

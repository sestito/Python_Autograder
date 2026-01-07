#!/bin/bash
# ============================================================
# Run Assignment Editor from Python Source
# ============================================================
# Use this script if you need to include additional Python
# packages beyond the defaults (scipy, sympy, sklearn, etc.)
# 
# Prerequisites:
#   - Python 3.8+ installed
#   - Required packages: pip install pandas openpyxl numpy matplotlib
#   - Any additional packages you want to include in the build
# ============================================================

echo ""
echo "============================================================"
echo "  Assignment Editor (Python Source)"
echo "============================================================"
echo ""

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "Using: $($PYTHON_CMD --version)"
echo ""

# Check if assignment-editor-gui.py exists
if [ ! -f "assignment-editor-gui.py" ]; then
    echo "ERROR: assignment-editor-gui.py not found!"
    echo "Make sure this script is in the same folder as the source files."
    exit 1
fi

echo "Starting Assignment Editor..."
echo ""

$PYTHON_CMD assignment-editor-gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo "============================================================"
    echo "  ERROR: Assignment Editor failed to start"
    echo "============================================================"
    echo ""
    echo "Common issues:"
    echo "  - Missing packages: pip install pandas openpyxl numpy matplotlib"
    echo "  - Python not in PATH"
    echo ""
fi

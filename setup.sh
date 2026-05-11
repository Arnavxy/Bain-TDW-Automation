#!/bin/bash
# TDW Cuts Automation Tool - Setup Script
# For Linux/Mac users

echo "=========================================="
echo "TDW Cuts Automation Tool - Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please download and install Python from: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo "✓ Python found"
echo ""

# Install dependencies
echo "Installing required packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "To start the application, run:"
    echo "  ./run.sh"
    echo ""
    echo "Or manually:"
    echo "  python3 app.py"
    echo ""
else
    echo ""
    echo "❌ Installation failed. Please check the error messages above."
    echo ""
    exit 1
fi
#!/bin/bash
# Quick start script for Task Backup Base

echo "=================================="
echo "Task Backup Base - Quick Start"
echo "=================================="
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi

echo "1. Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "2. Installing package..."
pip install -q -e .
if [ $? -ne 0 ]; then
    echo "Error: Failed to install package"
    exit 1
fi

echo "3. Running tests..."
python test_integration.py
if [ $? -ne 0 ]; then
    echo "Error: Tests failed"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo "=================================="
echo ""
echo "Available commands:"
echo "  python -m task_backup list"
echo "  python -m task_backup backup <platform> <input-file>"
echo "  python -m task_backup migrate <backup-file> <source> <target>"
echo ""
echo "Try these examples:"
echo "  python -m task_backup backup google_tasks examples/google_tasks_sample.json"
echo "  python -m task_backup backup todoist examples/todoist_sample.json --format toml"
echo ""
echo "For more information, see README.md and USAGE.md"
echo ""

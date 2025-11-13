#!/bin/bash

echo "========================================"
echo "AI Search Algorithm Visualizer"
echo "Quick Start Script"
echo "========================================"
echo

echo "Checking for Python..."
if ! command -v python3 &> /dev/null
then
    if ! command -v python &> /dev/null
    then
        echo "Python not found! Please install Python 3."
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

echo "Python found!"
echo
echo "Starting local HTTP server on port 8000..."
echo
echo "========================================"
echo "Open your browser and go to:"
echo "http://localhost:8000"
echo "========================================"
echo
echo "Press Ctrl+C to stop the server"
echo

$PYTHON_CMD -m http.server 8000

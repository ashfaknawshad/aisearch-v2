@echo off
echo ========================================
echo AI Search Algorithm Visualizer
echo Quick Start Script
echo ========================================
echo.

echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.
    pause
    exit /b 1
)

echo Python found!
echo.
echo Starting local HTTP server on port 8000...
echo.
echo ========================================
echo Open your browser and go to:
echo http://localhost:8000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python -m http.server 8000

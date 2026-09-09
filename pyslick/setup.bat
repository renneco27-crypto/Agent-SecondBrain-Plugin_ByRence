@echo off
REM PySlick Setup Script
REM This script installs dependencies and sets up PySlick globally

echo ========================================
echo PySlick Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [1/5] Python found:
python --version
echo.

REM Create a dedicated virtual environment (optional but recommended)
echo [2/5] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo WARNING: Failed to create virtual environment, using system Python
) else (
    echo Virtual environment created successfully
)

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
    echo.
)

REM Install Python dependencies
echo [3/5] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Create a batch wrapper for pyslick
echo [4/5] Creating pyslick.bat wrapper...
(
echo @echo off
echo python "%~dp0pyslick.py" %%*
) > pyslick.bat
echo Wrapper created successfully
echo.

REM Add to PATH (optional - requires admin rights)
echo [5/5] PATH Setup
echo.
echo To use pyslick from anywhere, you have two options:
echo.
echo OPTION 1: Add current directory to PATH (requires admin)
echo   - Right-click "This PC" -^> Properties -^> Advanced System Settings
echo   - Environment Variables -^> System Variables -^> Path -^> Edit
echo   - Add: %CD%
echo.
echo OPTION 2: Use the local pyslick.bat wrapper
echo   - pyslick.bat is in the current directory
echo   - You can call it directly: pyslick.bat --help
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Quick Test:
python pyslick.py --help
echo.
echo Next Steps:
echo 1. Run: pyslick.bat --help
echo 2. Add this directory to PATH for global access
echo 3. Or use: python pyslick.py --help
echo.
pause
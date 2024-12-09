@echo off
echo Starting Basic Windsurf Installation...

:: Run directory setup
call setup_basic.bat

:: Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo Python not found! Please download and install Python from:
    echo https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

:: Install basic requirements
echo Installing basic requirements...
python -m pip install --upgrade pip
pip install -r requirements_basic.txt

echo Installation completed!
echo To start using the project:
echo 1. Activate the virtual environment: .venv\Scripts\activate.bat
echo 2. Run Python scripts from the src directory
pause

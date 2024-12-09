@echo off
setlocal enabledelayedexpansion

echo Starting Windsurf Project Installation (Windows)...

:: Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.8 or higher.
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Upgrade pip
python -m pip install --upgrade pip

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Setup directories
echo Setting up project directories...
python setup_directories.py

:: Initialize database
echo Initializing database...
python src/database/init_db.py

:: Setup CUDA if available
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"

:: Create necessary environment variables
echo Setting up environment variables...
setx WINDSURF_HOME "%CD%"
setx WINDSURF_DATA "%CD%\data"
setx WINDSURF_MODELS "%CD%\models"

:: Test installation
echo Running system tests...
python -m pytest tests/

echo Installation complete! Run 'python src/main.py' to start the system.
pause

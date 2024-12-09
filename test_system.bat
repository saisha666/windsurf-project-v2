@echo off
echo Testing Windsurf System (No Voice Components)...

:: Set environment variables
set WINDSURF_HOME=E:\windsurf-project
set WINDSURF_DATA=%WINDSURF_HOME%\data
set WINDSURF_MODELS=%WINDSURF_HOME%\models

:: Create necessary directories
mkdir "%WINDSURF_DATA%" 2>nul
mkdir "%WINDSURF_MODELS%" 2>nul

:: Test pattern analyzer
echo.
echo Testing Pattern Analyzer...
echo.
echo Sample test: 2 4 6 8 10
python src/simple_analyzer.py

echo.
echo Test completed.
pause

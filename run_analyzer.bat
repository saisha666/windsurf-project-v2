@echo off
echo Starting Pattern Analyzer...

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Run the analyzer
python src/simple_analyzer.py

pause

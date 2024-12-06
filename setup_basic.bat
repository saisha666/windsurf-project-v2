@echo off
echo Setting up Windsurf Project...

:: Create main project directories
mkdir src\voice 2>nul
mkdir src\scrapers 2>nul
mkdir src\config 2>nul
mkdir tests 2>nul
mkdir logs 2>nul

:: Create data directories in AppData
set DATA_ROOT=%LOCALAPPDATA%\RouletteData
mkdir "%DATA_ROOT%\System\Cache" 2>nul
mkdir "%DATA_ROOT%\System\Backup" 2>nul
mkdir "%DATA_ROOT%\System\Archive" 2>nul
mkdir "%DATA_ROOT%\System\Temp" 2>nul

:: Create timestamp-based cache folder
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set CACHE_FOLDER=sys_%mydate%_%mytime%
mkdir "%DATA_ROOT%\System\Cache\%CACHE_FOLDER%" 2>nul

echo Setup completed successfully!
echo Data directory: %DATA_ROOT%
echo Cache folder: %CACHE_FOLDER%

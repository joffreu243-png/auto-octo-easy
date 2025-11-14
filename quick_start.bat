@echo off
title OctoMaster Pro

echo.
echo ============================================================
echo   OctoMaster Pro
echo ============================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run install_and_run.bat first
    pause
    exit /b 1
)

REM Activate and run
call venv\Scripts\activate.bat
python main.py

pause

@echo off
REM Fix greenlet installation issues on Windows
REM This script helps resolve greenlet compilation problems

echo ================================================
echo OctoMaster Pro - Greenlet Fix for Windows
echo ================================================
echo.

echo This script will attempt to fix greenlet installation issues.
echo.

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

echo Step 1: Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)
echo OK
echo.

echo Step 2: Uninstalling existing greenlet (if any)...
pip uninstall -y greenlet 2>nul
echo OK
echo.

echo Step 3: Installing greenlet with binary wheel...
pip install greenlet --prefer-binary --only-binary :all:
if errorlevel 1 (
    echo.
    echo WARNING: Binary wheel installation failed
    echo.
    echo Trying alternative method...
    echo.

    REM Try with --no-cache-dir
    pip install greenlet --prefer-binary --no-cache-dir
    if errorlevel 1 (
        echo.
        echo ERROR: Greenlet installation failed!
        echo.
        echo This usually means you need Microsoft C++ Build Tools.
        echo.
        echo Solutions:
        echo 1. Install Visual Studio Build Tools from:
        echo    https://visualstudio.microsoft.com/downloads/
        echo.
        echo 2. Or download pre-built wheel from:
        echo    https://www.lfd.uci.edu/~gohlke/pythonlibs/#greenlet
        echo.
        echo 3. Or use Python 3.11 which has better binary wheel support
        echo.
        pause
        exit /b 1
    )
)

echo OK
echo.

echo Step 4: Verifying greenlet installation...
python -c "import greenlet; print(f'Greenlet version: {greenlet.__version__}')" 2>nul
if errorlevel 1 (
    echo ERROR: Greenlet verification failed
    pause
    exit /b 1
)
echo OK
echo.

echo ================================================
echo Greenlet successfully installed!
echo ================================================
echo.
echo You can now continue with: python setup_windows.bat
echo.
pause

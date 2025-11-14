@echo off
echo Creating desktop shortcut...

set SCRIPT_DIR=%~dp0
set SHORTCUT=%USERPROFILE%\Desktop\OctoMaster Pro.lnk

powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT%'); $SC.TargetPath = '%SCRIPT_DIR%quick_start.bat'; $SC.WorkingDirectory = '%SCRIPT_DIR%'; $SC.Description = 'OctoMaster Pro - Browser Automation'; $SC.Save()"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Shortcut created on Desktop!
    echo You can now launch OctoMaster Pro from desktop
) else (
    echo.
    echo ERROR: Failed to create shortcut
)

echo.
pause
